# Aadhaar Analytics Dashboard

**Submission for Data-Driven Innovation on Aadhaar Hackathon 2026**

## 1. Problem

District officials currently wait 30 days to get reports on Aadhaar updates. Because of this delay, they cannot quickly send extra help (like more kits or staff) to places where many people are moving.

- **Impact**: Long waiting lines for citizens and slow government response.
- **Solution**: A dashboard that shows what is happening right now and predicts what will happen next month.

## 2. Features

### A. Predicting Migration

- **What it does**: Uses a prediction model to guess how many people will move to a district next month.
- **How**: It looks at past data on address changes.
- **Benefit**: Officials can send extra staff to these places _before_ the crowd arrives.

### B. Grouping Districts (Segmentation)

- **What it does**: Groups districts into 4 types based on their activity.
- **Groups**:
  1.  _Steady State_: Normal activity.
  2.  _High Volume_: Busy cities.
  3.  _Emerging_: Areas with many new babies/children.
  4.  _Transient_: Areas with many address changes (migration).

### C. Finding Errors

- **What it does**: Spots unusual numbers in the data.
- **Benefit**: Helps find mistakes or potential fraud.

### D. Alerts

- **What it does**: Sends simple warnings.
- **Examples**:
  - _High Migration_: "Too many address changes."
  - _Child Gap_: "Many school kids but few babies enrolled."

## 3. How It Works

### Parts

1.  **Ingestion**: Reads the CSV files.
2.  **Analysis**: Uses Python to calculate trends and specific groups.
3.  **Dashboard**: A simple website to show the charts and maps.

### Limitations

- It uses past data to predict the future, so it might miss sudden new events.
- It assumes the data files are uploaded regularly.

## 4. How to Run

```bash
python -m streamlit run app.py
```

- **Needs**: Python 3.9+, pandas, scikit-learn.
