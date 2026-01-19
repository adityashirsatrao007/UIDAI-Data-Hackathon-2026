import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    import sys
    sys.path.append(BASE_DIR)
    # Hacky import to avoid circular dep issues in this environment
    if os.path.exists(os.path.join(BASE_DIR, "analyze_insights.py")):
        from analyze_insights import load_data as ld
        return ld()
    return {}

def run_kmeans(dfs):
    print("Performing District DNA Clustering...")
    
    # 1. Aggregate Features
    # We need: Enrolment Volume, Update Volume, Child Ratio
    
    enrol = dfs['enrolment'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    bio = dfs['biometric'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    demo = dfs['demographic'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    
    # Rename
    enrol = enrol.rename(columns={'age_0_5': 'enrol_0_5', 'age_5_17': 'enrol_5_17', 'age_18_greater': 'enrol_18_plus'})
    bio_cols = [c for c in bio.columns if 'age' in c]
    bio['total_bio'] = bio[bio_cols].sum(axis=1)
    
    demo_cols = [c for c in demo.columns if 'age' in c]
    demo['total_demo'] = demo[demo_cols].sum(axis=1)
    
    # Merge
    df = pd.merge(enrol, bio[['state', 'district', 'total_bio']], on=['state', 'district'], how='outer').fillna(0)
    df = pd.merge(df, demo[['state', 'district', 'total_demo']], on=['state', 'district'], how='outer').fillna(0)
    
    df['total_enrol'] = df['enrol_0_5'] + df['enrol_5_17'] + df['enrol_18_plus']
    df['total_updates'] = df['total_bio'] + df['total_demo']
    
    df['intensity'] = df['total_updates'] / (df['total_enrol'] + 1)
    df['child_share'] = (df['enrol_0_5'] + df['enrol_5_17']) / (df['total_enrol'] + 1)
    df['mig_idx'] = df['total_demo'] / (df['total_bio'] + 1)
    features = ['total_enrol', 'intensity', 'child_share', 'mig_idx']
    X = df[features].fillna(0)
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    output_file = os.path.join(OUTPUT_DIR, "district_clusters.csv")
    df.to_csv(output_file, index=False)
    print(f"Cluster data saved to {output_file}")
    
    return df

if __name__ == "__main__":
    dfs = load_data()
    run_kmeans(dfs)
