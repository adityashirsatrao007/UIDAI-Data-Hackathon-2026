import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    # Hacky import to avoid circular dep issues in this environment
    import sys
    sys.path.append(BASE_DIR)
    if os.path.exists(os.path.join(BASE_DIR, "analyze_insights.py")):
        from analyze_insights import load_data as ld
        return ld()
    return {}

def find_outliers(dfs):
    print("Detecting Statistical Anomalies...")
    
    # 1. Aggregate Features (Reuse Logic)
    enrol = dfs['enrolment'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    bio = dfs['biometric'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    
    bio_cols = [c for c in bio.columns if 'age' in c]
    bio['total_bio'] = bio[bio_cols].sum(axis=1)
    
    # Merge
    df = pd.merge(enrol, bio[['state', 'district', 'total_bio']], on=['state', 'district'], how='outer').fillna(0)
    df = df.rename(columns={'age_0_5': 'enrol_0_5'})
    df['bio_ratio'] = df['total_bio'] / (df['enrol_0_5'] + 1)
    
    X = df[['bio_ratio', 'enrol_0_5', 'total_bio']].fillna(0)
    
    # Isolation Forest
    iso = IsolationForest(contamination=0.01, random_state=42)
    df['anomaly'] = iso.fit_predict(X)
    
    outliers = df[df['anomaly'] == -1]
    
    print(f"Found {len(outliers)} anomalies.")
    
    report_path = os.path.join(OUTPUT_DIR, "anomaly_report.md")
    with open(report_path, "w") as f:
        f.write("# Anomaly Detection Report\n\n")
        f.write("Districts with statistically unusual patterns (e.g., abnormally high updates vs enrolments).\n\n")
        f.write("| State | District | Enrol (0-5) | Bio Updates | Ratio |\n")
        f.write("|---|---|---|---|---|\n")
        for _, row in outliers.iterrows():
            f.write(f"| {row['state']} | {row['district']} | {int(row['enrol_0_5'])} | {int(row['total_bio'])} | {row['bio_ratio']:.2f} |\n")
            
    print(f"Anomaly report saved to {report_path}")

if __name__ == "__main__":
    dfs = load_data()
    find_outliers(dfs)
