
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🛠️ Lightweight Drilling Dashboard")

st.sidebar.header("Upload Sensor CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    st.sidebar.markdown("---")
    max_rows = st.sidebar.slider("Max rows to load", 5000, 200000, 30000, step=5000)
    with st.spinner("Loading sample..."):
        usecols = [
            'YYYY/MM/DD', 'HH:MM:SS',
            'Rate Of Penetration (ft_per_hr)',
            'Hook Load (klbs)', 'Standpipe Pressure (psi)',
            'DAS Vibe Lateral Max (g_force)', 'SHAKER #3 (PERCENT)',
            'Flow (flow_percent)', 'Total Pump Output (gal_per_min)'
        ]
        df = pd.read_csv(uploaded_file, usecols=usecols, nrows=max_rows)
        df['Timestamp'] = pd.to_datetime(df['YYYY/MM/DD'] + ' ' + df['HH:MM:SS'], format='%m/%d/%Y %H:%M:%S')
        df.set_index('Timestamp', inplace=True)
        df.drop(columns=['YYYY/MM/DD', 'HH:MM:SS'], inplace=True)

    st.success(f"Loaded {len(df)} rows.")
    st.subheader("🔍 Preview (Downsampled)")
    df_sample = df.iloc[::10]
    st.dataframe(df_sample.head(10))

    tab = st.selectbox("Select View", ["Overview", "Diagnostics (Lite)"])

    if tab == "Overview":
        st.line_chart(df_sample[['Rate Of Penetration (ft_per_hr)', 'SHAKER #3 (PERCENT)']])

    elif tab == "Diagnostics (Lite)":
        mode = st.selectbox("Diagnostic Focus", [
            "Screen Load", "Shaker Efficiency", "Screen Utilization", "Washout Risk"
        ])

        if mode == "Screen Load":
            df['Screen Load Index (%)'] = (df['Flow (flow_percent)'] + df['SHAKER #3 (PERCENT)']) / 2
            st.line_chart(df['Screen Load Index (%)'].iloc[::10])

        elif mode == "Shaker Efficiency":
            df['Shaker Performance (%)'] = (100 - df['DAS Vibe Lateral Max (g_force)'] * 3).clip(0, 100)
            st.line_chart(df['Shaker Performance (%)'].iloc[::10])

        elif mode == "Screen Utilization":
            df['Screen Utilization (%)'] = (df['SHAKER #3 (PERCENT)'] / df['Flow (flow_percent)']) * 100
            df['Screen Utilization (%)'] = df['Screen Utilization (%)'].clip(0, 150)
            st.line_chart(df['Screen Utilization (%)'].iloc[::10])

        elif mode == "Washout Risk":
            df['Washout Flag'] = ((df['Rate Of Penetration (ft_per_hr)'] > 60) & (df['Standpipe Pressure (psi)'] < 500)).astype(int)
            st.line_chart(df['Washout Flag'].iloc[::10])

    st.sidebar.download_button("Download Sampled CSV", df.to_csv().encode(), "sampled_output.csv")
