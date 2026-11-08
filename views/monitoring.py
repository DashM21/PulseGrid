import streamlit as st
import pandas as pd
import altair as alt
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / TELEMETRY</div>
    <h1>Patient Monitoring Intelligence</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

# Fetch min and max dates available in the database
date_bounds_query = database_large.fetch_data("""
    SELECT MIN(DATE(timestamp)) AS min_date, MAX(DATE(timestamp)) AS max_date 
    FROM vitals_logs
""")

if date_bounds_query and date_bounds_query[0]["min_date"]:
    db_min = pd.to_datetime(date_bounds_query[0]["min_date"]).date()
    db_max = pd.to_datetime(date_bounds_query[0]["max_date"]).date()
    
    # Initialize session state for date range persistence & reset logic
    if "start_date" not in st.session_state:
        st.session_state.start_date = db_min
    if "end_date" not in st.session_state:
        st.session_state.end_date = db_max
        
    st.markdown("### 📅 Telemetry Time Window")
    
    col_picker, col_btn = st.columns([4, 1])
    
    with col_picker:
        date_range = st.date_input(
            "Select Date Range for Vitals Analysis",
            value=(st.session_state.start_date, st.session_state.end_date),
            min_value=db_min,
            max_value=db_max
        )
        
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Reset Window", width="stretch"):
            st.session_state.start_date = db_min
            st.session_state.end_date = db_max
            st.rerun()
            
    if len(date_range) == 2:
        start_date, end_date = date_range
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
    else:
        start_date, end_date = db_min, db_max
else:
    start_date, end_date = None, None

st.divider()

# Filtered Summary Metrics based on selected date range
date_filter_sql = ""
if start_date and end_date:
    date_filter_sql = f"WHERE DATE(timestamp) BETWEEN '{start_date}' AND '{end_date}'"

vitals_summary = database_large.fetch_data(f"""
    SELECT COUNT(*) AS total_readings, ROUND(AVG(heart_rate), 1) AS avg_heart_rate,
           ROUND(AVG(spo2), 1) AS avg_spo2, COUNT(DISTINCT patient_id) AS monitored_patients
    FROM vitals_logs
    {date_filter_sql}
""")

if vitals_summary:
    s = vitals_summary[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Readings", f"{s['total_readings']:,}")
    c2.metric("Active Patients", s["monitored_patients"] or 0)
    c3.metric("Avg Heart Rate", f"{s['avg_heart_rate'] or 0} bpm")
    c4.metric("Avg SpO2", f"{s['avg_spo2'] or 0}%")

st.divider()

# Handle single-day selection vs multi-day trends
if start_date == end_date:
    st.info(f"ℹ️ **Single-Day View ({start_date})**: Historical trend lines require a multi-day range (at least 2 distinct days). Summary metrics above reflect all logs recorded on this date.")
else:
    # Fetch trend data for multi-day ranges
    vitals_trends = database_large.fetch_data(f"""
        SELECT DATE_FORMAT(timestamp, '%Y-%m-%d') AS reading_date,
               ROUND(AVG(heart_rate), 1) AS avg_heart_rate, 
               ROUND(AVG(spo2), 1) AS avg_spo2
        FROM vitals_logs 
        {date_filter_sql}
        GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d') 
        ORDER BY reading_date
    """)

    trend_df = pd.DataFrame(vitals_trends) if vitals_trends else pd.DataFrame()

    if not trend_df.empty:
        trend_df["avg_heart_rate"] = pd.to_numeric(trend_df["avg_heart_rate"], errors="coerce")
        trend_df["avg_spo2"] = pd.to_numeric(trend_df["avg_spo2"], errors="coerce")
        trend_df["reading_date"] = pd.to_datetime(trend_df["reading_date"], errors="coerce")
        trend_df = trend_df.dropna(subset=["reading_date", "avg_heart_rate"])
        trend_df = trend_df.sort_values("reading_date")

    if not trend_df.empty and len(trend_df) > 1:
        st.subheader("Historical Vital Trends")

        st.markdown("**Average Heart Rate (bpm)**")
        hr_chart = alt.Chart(trend_df).mark_line(color="#55DDF5", strokeWidth=2).encode(
            x=alt.X('reading_date:T', title='Date'),
            y=alt.Y('avg_heart_rate:Q', title='BPM', scale=alt.Scale(zero=False)),
            tooltip=['reading_date:T', 'avg_heart_rate:Q']
        ).properties(height=300)
        st.altair_chart(hr_chart, width="stretch")
        
        st.markdown("**Average SpO2 (%)**")
        spo2_chart = alt.Chart(trend_df).mark_line(color="#22c55e", strokeWidth=2).encode(
            x=alt.X('reading_date:T', title='Date'),
            y=alt.Y('avg_spo2:Q', title='SpO2 %', scale=alt.Scale(zero=False)),
            tooltip=['reading_date:T', 'avg_spo2:Q']
        ).properties(height=300)
        st.altair_chart(spo2_chart, width="stretch")
    else:
        st.info("ℹ️ No multi-day telemetry trend records found for the selected range.")