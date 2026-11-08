import streamlit as st
import pandas as pd
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / OPERATIONS</div>
    <h1>Patient Admission Analytics</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

admission_trends = database_large.fetch_data("""
    SELECT DATE_FORMAT(admission_date, '%Y-%m') AS admission_month, COUNT(*) AS total_admissions
    FROM admissions GROUP BY DATE_FORMAT(admission_date, '%Y-%m') ORDER BY admission_month
""")

status_data = database_large.fetch_data("""
    SELECT admission_status, COUNT(*) AS total_patients
    FROM admissions GROUP BY admission_status ORDER BY total_patients DESC
""")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Monthly Admission Trend**")
    if admission_trends:
        st.line_chart(pd.DataFrame(admission_trends).set_index("admission_month")["total_admissions"], width='stretch')

with c2:
    st.markdown("**Patient Admission Status**")
    if status_data:
        st.bar_chart(pd.DataFrame(status_data).set_index("admission_status")["total_patients"], horizontal=True)

st.markdown("**Admission Records Summary**")
if admission_trends:
    st.dataframe(pd.DataFrame(admission_trends), hide_index=True, width='stretch')