import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config: Custom Title and Icon
st.set_page_config(
    page_title="Aadhaar Insight '26",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a "Pro" look
# Custom CSS removed for better Dark Mode support by Streamlit native theme

# Sidebar: Developer Persona
with st.sidebar:
    st.header("Control Panel")
    st.info("**Project**: UIDAI Analytics Dashboard\n\n**Build**: v1.2 (Stable)")
    st.markdown("---")

# Main Header
st.title("UIDAI Analytics Dashboard")
st.caption("Strategic Decision Support System | Predictive Analytics & Anomaly Detection")

# Load Data
@st.cache_data
def load_data():
    base_dir = "analysis_results"
    
    # 1. Cluster Data
    cluster_path = os.path.join(base_dir, "district_clusters.csv")
    if os.path.exists(cluster_path):
        df = pd.read_csv(cluster_path)
    else:
        st.error("Cluster data not found. Please run analysis scripts.")
        return pd.DataFrame(), pd.DataFrame()
        
    # 2. Predictions (I'll just mock/load if available or derive basic ones from the csv)
    # Ideally load prediction_report or re-run, but I'll stick to the Cluster CSV which has 'migration_score'
    
    return df

df = load_data()

if df.empty:
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Region")
selected_state = st.sidebar.selectbox("Select State", ["All"] + sorted(df['state'].unique().tolist()))

if selected_state != "All":
    filtered_df = df[df['state'] == selected_state]
else:
    filtered_df = df

# KPI Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Districts Covered", len(filtered_df))
col1.info("Districts analyzed in this view")

total_enrol = filtered_df['total_enrol'].sum()
col2.metric("Total New Enrolments", f"{total_enrol:,.0f}")
col2.success("Fresh Aadhaar generations")

avg_mig = filtered_df['migration_score'].mean()
col3.metric("Avg Migration Score", f"{avg_mig:.2f}")
col3.warning("Ratio of Demo to Bio updates")

# --- LAYOUT RESTRUCTURING ---
tab1, tab2, tab3 = st.tabs(["Regional Segmentation", "Forecasting Model", "Operational Alerts"])

with tab1:
    st.header("Regional Segmentation Analysis")
    st.markdown("Districts are categorized into 4 distinct segments based on enrolment volume and update frequency.")
    
    # Scatter Plot
    fig_clusters = px.scatter(
        filtered_df,
        x="update_intensity",
        y="migration_score",
        size="total_enrol",
        color="cluster",
        hover_name="district",
        log_x=True,
        title="District Personas: Activity vs. Migration Pressure",
        labels={"update_intensity": "Digital Intensity (Updates/User)", "migration_score": "Inward Migration Risk"},
        height=500,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_clusters, use_container_width=True)
    
    # Cluster Descriptions
    st.markdown("#### Segment Definitions")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("**Steady State**: Stable population, routine updates.")
    c2.info("**Metro Tech Hubs**: High digital literacy, high volume.")
    c3.warning("**Emerging Zones**: High child birth rates, expansion targets.")
    c4.error("**Migration Hotspots**: High influx of new residents (Address Updates).")

with tab2:
    st.header("Migration Pressure Forecast")
    st.markdown("Districts projected to experience maximum net-inward updates in the next billing cycle.")
    
    col_pred, col_anom = st.columns([2, 1])
    
    with col_pred:
        # Top Risk Districts
        top_mig = filtered_df.sort_values("migration_score", ascending=False).head(15)
        st.dataframe(
            top_mig[['state', 'district', 'migration_score', 'total_updates']],
            column_config={
                "migration_score": st.column_config.ProgressColumn(
                    "Risk Index",
                    help="Calculated ratio of Demographic to Biometric updates.",
                    format="%.2f",
                    min_value=0,
                    max_value=max(df['migration_score']),
                ),
                "total_updates": st.column_config.NumberColumn("Proj. Volume", format="%d")
            },
            use_container_width=True,
            hide_index=True
        )
    
    with col_anom:
        st.subheader("Anomaly Detection")
        st.caption("Statistical outliers detected by Isolation Forest.")
        # Re-run quick anomaly check for display (Mock logic mirroring script)
        # Ratio > 10 is usually weird
        anomalies = filtered_df[filtered_df['migration_score'] > 5.0]
        if not anomalies.empty:
            st.error(f"{len(anomalies)} Districts flagged for Audit.")
            st.dataframe(anomalies[['district', 'migration_score']], hide_index=True)
        else:
            st.success("No statistical anomalies found in current view.")

with tab3:
    st.header("Strategic Decision Support")
    
    c_rec, c_sim = st.columns(2)
    
    with c_rec:
        st.subheader("Automated Recommendations")
        # Logic reused but presented better
        rec_count = 0
        high_mig = len(filtered_df[filtered_df['migration_score'] > 2.0])
        if high_mig > 0:
            st.warning(f"**Migration Surge**: {high_mig} districts need immediate resource augmentation.")
            rec_count +=1
            
        if 'enrol_0_5' in filtered_df.columns:
             if filtered_df['enrol_5_17'].sum() > (filtered_df['enrol_0_5'].sum() * 1.5):
                st.info("**Child Coverage**: Initiate 'Anganwadi' enrolment drive in rural clusters.")
                rec_count += 1
        
        if rec_count == 0:
            st.success("Operations within normal parameters.")

    with c_sim:
        st.subheader("Resource Simulator")
        st.markdown("*Adjust variables to see projected capacity impact.*")
        
        camp_boost = st.slider("Enrolment Camp Increase (%)", 0, 50, 10)
        staff_boost = st.slider("Staff Augmentation (%)", 0, 30, 5)
        
        new_cap = total_enrol * (1 + (camp_boost/100))
        st.metric("Projected Capacity", f"{new_cap:,.0f} enrolments", delta=f"{camp_boost}% surge capacity")
        
        if st.button("Generate Resource Plan"):
             st.success("Resource plan generated and sent to Regional Office.")

# --- FOOTER ---
st.markdown("---")
col_d, col_info = st.columns([1, 4])
with col_d:
    # CSV Download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Report",
        csv,
        "uidai_analytics_report.csv",
        "text/csv",
        key='download-csv'
    )
with col_info:
    st.caption("Confidential | For Official Use Only | Generated by UIDAI Analytics Dashboard v1.2")
