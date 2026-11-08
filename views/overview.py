import streamlit as st
import pandas as pd
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / COMMAND CENTRE</div>
    <h1>Hospital Overview & Emergencies</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

def get_count(table):
    res = database_large.fetch_data(f"SELECT COUNT(*) AS total FROM {table}")
    return res[0]["total"] if res else 0

try:
    patients = get_count("patients")
    doctors = get_count("doctors")
    departments = get_count("departments")
    beds = get_count("beds")
    vitals = get_count("vitals_logs")
    emergencies = get_count("emergency_records")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients", f"{patients:,}")
    col2.metric("Medical Staff", f"{doctors:,}")
    col3.metric("Departments", f"{departments:,}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Beds", f"{beds:,}")
    col5.metric("Vital Readings", f"{vitals:,}")
    col6.metric("Emergency Records", f"{emergencies:,}")

    st.success("Connected to PULSEGRID Large Database")
except Exception as e:
    st.error(f"Error loading overview: {e}")

st.divider()
st.subheader("Emergency Intelligence")

emergency_priority = database_large.fetch_data("""
    SELECT priority, COUNT(*) AS total FROM emergency_records 
    GROUP BY priority ORDER BY FIELD(priority, 'Critical', 'High', 'Moderate', 'Low')
""")
emergency_status = database_large.fetch_data("""
    SELECT response_status, COUNT(*) AS total FROM emergency_records 
    GROUP BY response_status ORDER BY total DESC
""")

c1, c2 = st.columns(2)
if emergency_priority:
    with c1:
        st.markdown("**Emergency Priority Distribution**")
        st.bar_chart(pd.DataFrame(emergency_priority).set_index("priority"), horizontal=True)
if emergency_status:
    with c2:
        st.markdown("**Emergency Response Status**")
        st.bar_chart(pd.DataFrame(emergency_status).set_index("response_status"), horizontal=True)