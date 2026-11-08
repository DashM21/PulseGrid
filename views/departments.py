import streamlit as st
import pandas as pd
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / RESOURCE MANAGEMENT</div>
    <h1>Department & Equipment Intelligence</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

# Interactive Filter Bar
departments_list = database_large.fetch_data("SELECT department_name FROM departments ORDER BY department_name")
dept_options = ["All Departments"] + [d["department_name"] for d in departments_list]
selected_dept = st.selectbox("Filter by Department", dept_options)

st.divider()
st.subheader("Department Intelligence")

dept_filter_sql = f"WHERE d.department_name = '{selected_dept}'" if selected_dept != "All Departments" else ""
department_data = database_large.fetch_data(f"""
    SELECT d.department_name, COUNT(a.admission_id) AS total_admissions
    FROM departments d LEFT JOIN admissions a ON d.department_id = a.department_id
    {dept_filter_sql} GROUP BY d.department_id, d.department_name ORDER BY total_admissions DESC
""")

if department_data:
    df_dep = pd.DataFrame(department_data)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.bar_chart(df_dep.set_index("department_name")["total_admissions"], horizontal=True)
    with c2:
        st.dataframe(df_dep, hide_index=True, width='stretch')

st.divider()
st.subheader("Equipment & Resource Intelligence")

eq_filter_sql = f"WHERE d.department_name = '{selected_dept}'" if selected_dept != "All Departments" else ""
equipment_data = database_large.fetch_data(f"""
    SELECT d.department_name, SUM(e.quantity) AS total_units, 
           SUM(e.available_quantity) AS available_units,
           SUM(e.quantity - e.available_quantity) AS occupied_units
    FROM equipment e JOIN departments d ON e.department_id = d.department_id
    {eq_filter_sql} GROUP BY d.department_id, d.department_name ORDER BY total_units DESC
""")

if equipment_data:
    eq_df = pd.DataFrame(equipment_data)
    tot = int(eq_df["total_units"].sum())
    avail = int(eq_df["available_units"].sum())
    occ = int(eq_df["occupied_units"].sum())
    rate = (avail / tot * 100) if tot else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Units", f"{tot:,}")
    col2.metric("Available", f"{avail:,}")
    col3.metric("Occupied", f"{occ:,}")
    col4.metric("Availability Rate", f"{rate:.1f}%")

    st.bar_chart(eq_df.set_index("department_name")[["available_units", "occupied_units"]], horizontal=True)
    
    st.markdown("### Equipment Inventory Table")
    st.dataframe(eq_df, hide_index=True, width='stretch')

    # CSV Export Button for Equipment
    csv_eq = eq_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Equipment Inventory CSV",
        data=csv_eq,
        file_name=f"pulsegrid_equipment_{selected_dept.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )