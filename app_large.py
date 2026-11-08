import streamlit as st

st.set_page_config(
    page_title="PULSEGRID Analytics",
    page_icon="📊",
    layout="wide"
)

# Global custom dark theme styling
st.markdown("""
<style>
    .main {
        background-color: #0B1220;
    }
    .pg-header {
        padding: 10px 0 10px 0;
    }
    .pg-label {
        color: #55DDF5;
        font-size: 13px;
        letter-spacing: 3px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Define pages
overview_page = st.Page("views/overview.py", title="Overview & Emergencies", icon="🏠")
dept_page = st.Page("views/departments.py", title="Departments & Equipment", icon="🏥")
monitoring_page = st.Page("views/monitoring.py", title="Patient Monitoring", icon="📈")
admissions_page = st.Page("views/admissions.py", title="Admission Analytics", icon="📋")
patients_page = st.Page("views/patients.py", title="Patient Directory", icon="🔍")
emergencies_page = st.Page("views/emergencies.py", title="Emergency Dispatch", icon="🚨")
control_page = st.Page("views/control_panel.py", title="System Diagnostics", icon="⚙️")

# Group pages into dictionary sections for top-bar dropdown categories
pg = st.navigation({
    "Command & Triage": [overview_page, emergencies_page],
    "Operations": [dept_page, admissions_page],
    "Clinical Intelligence": [monitoring_page, patients_page],
    "System": [control_page]
}, position="top")

pg.run()