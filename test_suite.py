import os
import sys
import subprocess
import pandas as pd

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
SCRIPTS = [
    "analyze_aadhaar.py",
    "analyze_insights.py",
    "analyze_predictions.py",
    "analyze_clustering.py",
    "analyze_anomalies.py"
]

EXPECTED_FILES = [
    "activity_over_time.png",
    "top_states_demographic.png",
    "findings.md",
    "prediction_report.md",
    "district_clusters.csv",
    "anomaly_report.md"
]

def run_script(script_name):
    print(f"Testing {script_name}...")
    try:
        path = os.path.join(BASE_DIR, script_name)
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FAIL]: {script_name}")
            print(result.stderr)
            return False
        else:
            print(f"[PASS]: {script_name}")
            return True
    except Exception as e:
        print(f"[ERROR]: Could not run {script_name}: {e}")
        return False

def verify_outputs():
    print("\nVerifying Artifacts...")
    all_exists = True
    for f in EXPECTED_FILES:
        path = os.path.join(OUTPUT_DIR, f)
        if os.path.exists(path):
            print(f"[FOUND]: {f}")
            # Optional: Check size > 0
            if os.path.getsize(path) == 0:
                print(f"[WARNING]: {f} is empty!")
        else:
            print(f"[MISSING]: {f}")
            all_exists = False
            
    # Logic Checks
    cluster_path = os.path.join(OUTPUT_DIR, "district_clusters.csv")
    if os.path.exists(cluster_path):
        try:
            df = pd.read_csv(cluster_path)
            if 'cluster' not in df.columns:
                print("[DATA ERROR]: 'cluster' column missing in district_clusters.csv")
                all_exists = False
            if df.empty:
                print("[DATA ERROR]: Cluster file is empty.")
                all_exists = False
            else:
                 print(f"[OK]: Data Integrity: {len(df)} districts clustered.")
        except Exception as e:
            print(f"[READ ERROR]: Could not validate CSV: {e}")
            all_exists = False
            
    return all_exists

def main():
    print("Starting Pre-Submission Test Suite")
    
    # 1. Run Pipeline
    pipeline_success = True
    for script in SCRIPTS:
        if not run_script(script):
            pipeline_success = False
            break # Stop on error
            
    if pipeline_success:
        print("\n---------------------------------------")
        # 2. Verify Outputs
        if verify_outputs():
            print("\n[RESULT]: SYSTEM STABLE. READY FOR SUBMISSION.")
        else:
            print("\n[RESULT]: PIPELINE RAN BUT ARTIFACTS ARE MISSING/INVALID.")
    else:
        print("\n[RESULT]: CRITICAL PIPELINE FAILURE.")

if __name__ == "__main__":
    main()
