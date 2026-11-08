import streamlit as st
import pandas as pd
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / DISPATCH</div>
    <h1>Emergency Triage & Active Alerts</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

try:
    # Try fetching from an emergencies or critical alerts table dynamically
    # Falls back gracefully if table names differ
    emergencies_data = database_large.fetch_data("""
        SELECT * FROM emergencies 
        ORDER BY timestamp DESC LIMIT 100
    """) if "emergencies" in str(database_large.fetch_data("SHOW TABLES")) else []
    
    if not emergencies_data:
        # Fallback: pull critical vitals logs where heart rate or spo2 indicates an emergency
        emergencies_data = database_large.fetch_data("""
            SELECT v.patient_id, p.first_name, p.last_name, v.heart_rate, v.spo2, v.blood_pressure, v.timestamp
            FROM vitals_logs v
            JOIN patients p ON v.patient_id = p.patient_id
            WHERE v.heart_rate > 120 OR v.heart_rate < 50 OR v.spo2 < 90
            ORDER BY v.timestamp DESC LIMIT 100
        """)

    if emergencies_data:
        df_emergencies = pd.DataFrame(emergencies_data)
        
        # Summary Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Critical Alerts", len(df_emergencies))
        c2.metric("Response Status", "Active Triage", "Operational")
        c3.metric("Command Center Node", "Port 8503", "Online")
        
        st.divider()
        st.subheader("Live Emergency Stream")
        
        # Filter by severity or search
        search_term = st.text_input("Filter Alerts by Patient ID or Keyword", placeholder="e.g., P1042 or Critical")
        if search_term and search_term.strip():
            mask = df_emergencies.astype(str).apply(
                lambda x: x.str.contains(search_term.strip(), case=False)
            ).any(axis=1)
            df_emergencies = df_emergencies[mask]

        st.dataframe(df_emergencies, hide_index=True, width='stretch')
        
        # CSV Export for Emergency Log
        csv_emergencies = df_emergencies.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Emergency Logs CSV",
            data=csv_emergencies,
            file_name="pulsegrid_emergency_audit.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ No active critical emergencies detected in the current telemetry logs.")

except Exception as e:
    st.error(f"Error loading emergency dispatch stream: {e}")