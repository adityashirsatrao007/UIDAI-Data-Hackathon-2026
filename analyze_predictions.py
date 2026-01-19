import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_training_data():
    print("Loading data for prediction...")
    import sys
    sys.path.append(BASE_DIR)
    from analyze_insights import load_data
    
    dfs = load_data()
    
    # Flatten data
    frames = []
    
    for cat, df in dfs.items():
        if df.empty: continue
        # Identify value columns
        val_cols = [c for c in df.columns if 'age' in c]
        # Sum them to get 'count'
        df['value'] = df[val_cols].sum(axis=1)
        frames.append(process_df(df, cat, {}))
        
    if not frames:
        return pd.DataFrame()
        
    full_log = pd.concat(frames)
    
    pivot = raw_log.pivot_table(index=['date', 'state', 'district'], columns='category', values='value', aggfunc='sum').fillna(0).reset_index()
    pivot['mig_score'] = pivot['demographic'] / (pivot['biometric'] + 1)
    pivot = pivot.sort_values(['state', 'district', 'date'])
    
    return pivot

def run_forecast(df):
    print("Training Random Forest Model...")
    
    df['prev_mig_score'] = df.groupby(['state', 'district'])['mig_score'].shift(1)
    df['prev_demo'] = df.groupby(['state', 'district'])['demographic'].shift(1)
    
    df = df.dropna()
    
    if df.empty:
        print("Not enough historical data for lags.")
        return
        
    features = ['prev_mig_score', 'prev_demo', 'enrolment', 'biometric']
    target = 'mig_score'
    
    X = df[features]
    y = df[target]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
    print(f"Model RMSE: {rmse:.4f}")
    
    recent = df.groupby(['state', 'district']).tail(1).copy()
    recent['prev_mig_score'] = recent['mig_score']
    recent['prev_demo'] = recent['demographic']
    
    preds = model.predict(recent[features])
    recent['pred_score'] = preds
    recent['change'] = recent['pred_score'] - recent['mig_score']
    
    return recent

def save_report(preds):
    top_risks = preds.sort_values('change', ascending=False).head(10)
    
    report_path = os.path.join(OUTPUT_DIR, "prediction_report.md")
    with open(report_path, "w") as f:
        f.write("# Predictive Insights: Future Migration Hotspots\n\n")
        f.write("> **Forecast**: Predicting Districts likely to see a SURGE in migration-related updates next month.\n\n")
        
        f.write("## Top 10 Districts with Predicted Increase in Migration Pressure\n")
        f.write("| State | District | Current Score | Predicted Score | Predicted Increase |\n")
        f.write("|---|---|---|---|---|\n")
        
        for _, row in top_risks.iterrows():
            f.write(f"| {row['state']} | {row['district']} | {row['mig_score']:.2f} | {row['pred_score']:.2f} | +{row['change']:.2f} |\n")
            
    print(f"Prediction report saved to {report_path}")

if __name__ == "__main__":
    # Ensure dependencies
    try:
        import sklearn
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "scikit-learn"])
        
    df = get_training_data()
    if not df.empty:
        preds = run_forecast(df)
        if preds is not None:
            save_report(preds)
    else:
        print("Data loading failed or empty.")
