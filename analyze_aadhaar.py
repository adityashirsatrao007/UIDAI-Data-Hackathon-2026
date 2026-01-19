import os
import glob
import pandas as pd
import seaborn as sns
import warnings

# Configuration
BASE_DIR = r"z:\UIDAI"
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_files(base_dir):
    """Recursively find all CSV files."""
    csv_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files

def classify_files(file_list):
    """Classify files into Biometric, Demographic, Enrolment based on filename."""
    categories = {
        'biometric': [],
        'demographic': [],
        'enrolment': []
    }
    
    for f in file_list:
        fname = os.path.basename(f).lower()
        if 'biometric' in fname:
            categories['biometric'].append(f)
        elif 'demographic' in fname:
            categories['demographic'].append(f)
        elif 'enrolment' in fname:
            categories['enrolment'].append(f)
            
    return categories

def load_and_aggregate(files, category_name):
    """Load multiple CSVs and concat them into one DataFrame."""
    print(f"Loading {len(files)} files for {category_name}...")
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")
    
    if not dfs:
        return pd.DataFrame()
        
    full_df = pd.concat(dfs, ignore_index=True)
    print(f"Aggregated {category_name}: {full_df.shape} rows.")
    return full_df

def clean_dataframe(df, category_name):
    """Standardizes column names, parses dates, and formats numeric columns."""
    if df.empty:
        return df
        
    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    
    numeric_cols = []
    if category_name == 'enrolment':
        numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    elif category_name == 'biometric':
        numeric_cols = ['bio_age_5_17', 'bio_age_17_']
    elif category_name == 'demographic':
        numeric_cols = ['demo_age_5_17', 'demo_age_17_']
        
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

def generate_eda_plots(df_dict):
    """Generate basic exploratory plots."""
    print("Generating EDA plots...")
    
    # 1. Time Series of Activity
    plt.figure(figsize=(12, 6))
    
    for cat, df in df_dict.items():
        if df.empty or 'date' not in df.columns:
            continue
            
        if cat == 'enrolment':
            df['total_activity'] = df['age_0_5'] + df['age_5_17'] + df.get('age_18_greater', 0)
        elif cat == 'biometric':
             df['total_activity'] = df['bio_age_5_17'] + df.get('bio_age_17_', 0)
        elif cat == 'demographic':
             df['total_activity'] = df['demo_age_5_17'] + df.get('demo_age_17_', 0)
             
        daily_sums = df.groupby('date')['total_activity'].sum()
        plt.plot(daily_sums.index, daily_sums.values, label=cat.capitalize())

    plt.title("Daily Aadhaar Activity (2025)")
    plt.xlabel("Date")
    plt.ylabel("Total Count (Updates/Enrolments)")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'activity_over_time.png'))
    plt.close()
    
    # 2. State-wise Comparison
    # Creating a combined metric dataframe for states
    state_stats = {}
    
    for cat, df in df_dict.items():
        if df.empty or 'state' not in df.columns:
            continue
        
        state_sums = df.groupby('state')['total_activity'].sum().sort_values(ascending=False).head(10)
        state_stats[cat] = state_sums
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=state_sums.values, y=state_sums.index)
        plt.title(f"Top 10 States - {cat.capitalize()}")
        plt.xlabel("Count")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f'top_states_{cat}.png'))
        plt.close()

def main():
    print("Starting Analysis...")
    all_files = find_files(BASE_DIR)
    print(f"Found {len(all_files)} CSV files.")
    
    categories = classify_files(all_files)
    
    df_dict = {}
    for cat, files in categories.items():
        if not files:
            print(f"No files found for {cat}")
            continue
            
        raw_df = load_and_aggregate(files, cat)
        df_dict[cat] = clean_dataframe(raw_df, cat)
        
    generate_eda_plots(df_dict)
    print(f"Analysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
