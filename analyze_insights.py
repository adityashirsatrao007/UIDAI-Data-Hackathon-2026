import os
import pandas as pd
import numpy as np

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_files(base_dir):
    csv_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def load_data():
    files = find_files(BASE_DIR)
    categories = {'biometric': [], 'demographic': [], 'enrolment': []}
    for f in files:
        fname = os.path.basename(f).lower()
        if 'biometric' in fname: categories['biometric'].append(f)
        elif 'demographic' in fname: categories['demographic'].append(f)
        elif 'enrolment' in fname: categories['enrolment'].append(f)
    
    dfs = {}
    for cat, flist in categories.items():
        if flist:
            dfs[cat] = pd.concat([pd.read_csv(f) for f in flist], ignore_index=True)
            # Normalize columns
            dfs[cat].columns = [c.strip().lower() for c in dfs[cat].columns]
    return dfs

def analyze_insights(dfs):
    print("Calculating Insights...")
    
    # Pre-processing: Group by District/State
    # Enrolment
    enrol = dfs['enrolment'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    # Biometric
    bio = dfs['biometric'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    # Demographic
    demo = dfs['demographic'].groupby(['state', 'district']).sum(numeric_only=True).reset_index()
    
    # Rename columns for merge
    enrol = enrol.rename(columns={'age_0_5': 'enrol_0_5', 'age_5_17': 'enrol_5_17', 'age_18_greater': 'enrol_18_plus'})
    bio = bio.rename(columns={'bio_age_5_17': 'bio_update_child', 'bio_age_17_': 'bio_update_adult'})
    demo = demo.rename(columns={'demo_age_5_17': 'demo_update_child', 'demo_age_17_': 'demo_update_adult'})
    
    # Merge
    merged = pd.merge(enrol, bio, on=['state', 'district'], how='outer').fillna(0)
    merged = pd.merge(merged, demo, on=['state', 'district'], how='outer').fillna(0)
    
    # --- METRIC 1: Migration Hotspots (Demographic Update Intensity) ---
    # Hypothesis: High demographic updates (address change) relative to static biometric updates implies migration.
    # Metric: Demo_Updates / (Bio_Updates + 1)
    # Why +1? Avoid div by zero.
    merged['total_demo_updates'] = merged['demo_update_child'] + merged['demo_update_adult']
    merged['total_bio_updates'] = merged['bio_update_child'] + merged['bio_update_adult']
    merged['total_enrolments'] = merged['enrol_0_5'] + merged['enrol_5_17'] + merged['enrol_18_plus']
    
    merged['migration_score'] = merged['total_demo_updates'] / (merged['total_bio_updates'] + 1)
    
    # --- METRIC 2: Child Enrolment Lag ---
    # Is the system catching kids late?
    # Ratio of 5-17 enrolments vs 0-5 enrolments. High ratio = Late enrolment (catchup). Low ratio = Early capture.
    merged['child_catchup_ratio'] = merged['enrol_5_17'] / (merged['enrol_0_5'] + 1)
    
    # --- METRIC 3: Digital Maturity (Update Intensity) ---
    # How active are users? Total Updates / New Enrolments (Proxy for base size assuming base is proportional to new enrolments, which is weak, but workable)
    # Better: Total Updates. Just absolute volume for now, or Updates per District avg.
    merged['digital_intensity'] = merged['total_demo_updates'] + merged['total_bio_updates']

    # --- GENERATE REPORT ---
    report_path = os.path.join(OUTPUT_DIR, "findings.md")
    with open(report_path, "w") as f:
        f.write("# Aadhaar Data Insights: Unlocking Societal Trends\n\n")
        
        # 1. Migration
        top_migration = merged.sort_values('migration_score', ascending=False).head(10)
        f.write("## 1. Potential Migration Hotspots\n")
        f.write("These districts have a disproportionately high number of demographic updates (likely address changes) compared to biometric updates.\n\n")
        f.write("| State | District | Demo Updates | Bio Updates | Migration Score |\n")
        f.write("|---|---|---|---|---|\n")
        for _, row in top_migration.iterrows():
            f.write(f"| {row['state']} | {row['district']} | {int(row['total_demo_updates'])} | {int(row['total_bio_updates'])} | {row['migration_score']:.2f} |\n")
        f.write("\n")
        
        # 2. Child Enrolment
        top_lag = merged[merged['enrol_0_5'] > 100].sort_values('child_catchup_ratio', ascending=False).head(10) # Filter low volume
        f.write("## 2. Child Enrolment 'Catch-up' Areas\n")
        f.write("Districts where school-age enrolment (5-17) significantly outpaces birth enrolment (0-5). Focus areas for early childhood coverage.\n\n")
        f.write("| State | District | Enrol 0-5 | Enrol 5-17 | Lag Ratio |\n")
        f.write("|---|---|---|---|---|\n")
        for _, row in top_lag.iterrows():
            f.write(f"| {row['state']} | {row['district']} | {int(row['enrol_0_5'])} | {int(row['enrol_5_17'])} | {row['child_catchup_ratio']:.2f} |\n")
        f.write("\n")
        
        # 3. Digital Intensity
        top_digital = merged.sort_values('digital_intensity', ascending=False).head(10)
        f.write("## 3. High Digital Maturity Zones\n")
        f.write("Districts with the highest absolute volume of updates, indicating an active, tech-integrated population.\n\n")
        f.write("| State | District | Total Updates | Enrolments |\n")
        f.write("|---|---|---|---|\n")
        for _, row in top_digital.iterrows():
            f.write(f"| {row['state']} | {row['district']} | {int(row['digital_intensity'])} | {int(row['total_enrolments'])} |\n")
        f.write("\n")
        
    print(f"Insights generated at {report_path}")

if __name__ == "__main__":
    dfs = load_data()
    analyze_insights(dfs)
