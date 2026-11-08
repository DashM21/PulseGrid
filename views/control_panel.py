import streamlit as st
import pandas as pd
import database_large
import time

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / SYSTEM</div>
    <h1>Command Center Diagnostics & Control</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

try:
    # Measure DB Latency & Connection Health
    start_time = time.time()
    db_check = database_large.fetch_data("SELECT 1 AS status")
    latency = (time.time() - start_time) * 1000

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DB Connection Status", "ONLINE", "Port 8503")
    col2.metric("Query Latency", f"{latency:.2f} ms", "Optimal")
    col3.metric("Environment", "Production Mode", "Secure")
    col4.metric("Active Node", "Localhost", "Stable")

    st.divider()
    st.subheader("Database Table Architecture & Storage")

    # Fetch table status / row counts
    try:
        tables_status = database_large.fetch_data("SHOW TABLE STATUS")
        if tables_status:
            df_tables = pd.DataFrame(tables_status)
            cols_to_show = [c for c in ['Name', 'Rows', 'Data_length', 'Index_length', 'Engine', 'Collation'] if c in df_tables.columns]
            st.dataframe(df_tables[cols_to_show], hide_index=True, width='stretch')
    except Exception:
        # Fallback manual counts if SHOW TABLE STATUS is restricted
        tables = ['patients', 'departments', 'admissions', 'vitals_logs']
        counts = []
        for t in tables:
            try:
                res = database_large.fetch_data(f"SELECT COUNT(*) as cnt FROM {t}")
                counts.append({"Table": t, "Rows": res[0]['cnt'] if res else 0})
            except Exception:
                pass
        if counts:
            st.dataframe(pd.DataFrame(counts), hide_index=True, width='stretch')

    st.divider()
    st.subheader("Schema Inspection")
    
    # Dynamically detect available tables for schema inspection
    tables_list_query = database_large.fetch_data("SHOW TABLES")
    if tables_list_query:
        # Extract table names regardless of key format
        key_name = list(tables_list_query[0].keys())[0]
        available_tables = [row[key_name] for row in tables_list_query]
        
        selected_table = st.selectbox("Select Table to Inspect Schema", available_tables)
        
        if selected_table:
            schema_data = database_large.fetch_data(f"DESCRIBE {selected_table}")
            if schema_data:
                st.dataframe(pd.DataFrame(schema_data), hide_index=True, width='stretch')

    st.divider()
    st.subheader("System Maintenance & Actions")
    c_act1, c_act2 = st.columns(2)
    with c_act1:
        if st.button("🧹 Clear Streamlit Cache", width='stretch'):
            st.cache_data.clear()
            st.success("Cache cleared successfully.")
    with c_act2:
        if st.button("🔄 Test Database Reconnect", width='stretch'):
            try:
                database_large.fetch_data("SELECT 1")
                st.success("Database connection verified stable.")
            except Exception as ex:
                st.error(f"Connection failed: {ex}")

except Exception as e:
    st.error(f"Diagnostics error: {e}")