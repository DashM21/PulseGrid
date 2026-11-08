import streamlit as st
import pandas as pd
import altair as alt
import database_large

st.markdown("""
<div class="pg-header">
    <div class="pg-label">PULSEGRID / DIRECTORY</div>
    <h1>Patient Lookup & Medical History</h1>
</div>
""", unsafe_allow_html=True)
st.divider()

try:
    patients_list = database_large.fetch_data("SELECT * FROM patients LIMIT 50")

    if not patients_list:
        st.warning("No patient records found in the `patients` table.")
    else:
        df_patients = pd.DataFrame(patients_list)
        
        cols = df_patients.columns.tolist()
        id_col = next((c for c in cols if 'id' in c.lower()), cols[0])
        
        search_query = st.text_input(
            "Search Patient", 
            placeholder=f"Search by {id_col} or any keyword..."
        )
        
        if search_query and search_query.strip():
            mask = df_patients.astype(str).apply(
                lambda x: x.str.contains(search_query.strip(), case=False)
            ).any(axis=1)
            df_patients = df_patients[mask]

        st.caption(f"Showing {len(df_patients)} patient record(s)")

        if not df_patients.empty:
            def make_label(row):
                parts = [str(row[id_col])]
                for c in ['first_name', 'name', 'last_name']:
                    if c in row and pd.notna(row[c]):
                        parts.append(str(row[c]))
                return " - ".join(parts)

            patient_options = [make_label(row) for _, row in df_patients.iterrows()]
            selected_patient_str = st.selectbox("Select Patient for Detailed Drill-Down", patient_options)

            if selected_patient_str:
                selected_id = selected_patient_str.split(" - ")[0]
                
                # Fetch detailed patient info
                p_info = database_large.fetch_data(f"SELECT * FROM patients WHERE {id_col} = '{selected_id}'")
                
                if p_info:
                    p = p_info[0]
                    st.divider()
                    st.markdown(f"### Patient Profile (`{selected_id}`)")
                    st.dataframe(pd.DataFrame([p]), hide_index=True, width='stretch')
                    
                    # Admission history
                    st.markdown("#### 📋 Admission History")
                    try:
                        admissions = database_large.fetch_data(f"""
                            SELECT a.*, d.department_name 
                            FROM admissions a 
                            LEFT JOIN departments d ON a.department_id = d.department_id 
                            WHERE a.patient_id = '{selected_id}'
                        """)
                        if admissions:
                            st.dataframe(pd.DataFrame(admissions), hide_index=True, width='stretch')
                        else:
                            st.info("No admission records found for this patient.")
                    except Exception:
                        st.info("No matching admissions table structure found.")
                        
                    # Patient-Specific Telemetry & Vitals Charts
                    st.markdown("#### 📈 Patient Telemetry Trends")
                    try:
                        vitals = database_large.fetch_data(f"""
                            SELECT timestamp, heart_rate, spo2, blood_pressure, simulation_profile 
                            FROM vitals_logs 
                            WHERE patient_id = '{selected_id}' 
                            ORDER BY timestamp ASC
                        """)
                        
                        if vitals:
                            v_df = pd.DataFrame(vitals)
                            v_df["timestamp"] = pd.to_datetime(v_df["timestamp"])
                            v_df["heart_rate"] = pd.to_numeric(v_df["heart_rate"], errors="coerce")
                            v_df["spo2"] = pd.to_numeric(v_df["spo2"], errors="coerce")
                            
                            # Individual Heart Rate Chart
                            st.markdown("**Heart Rate (bpm)**")
                            hr_chart = alt.Chart(v_df).mark_line(color="#55DDF5", strokeWidth=2).encode(
                                x=alt.X('timestamp:T', title='Time'),
                                y=alt.Y('heart_rate:Q', title='BPM', scale=alt.Scale(zero=False)),
                                tooltip=['timestamp:T', 'heart_rate:Q', 'blood_pressure:N', 'simulation_profile:N']
                            ).properties(height=280)
                            st.altair_chart(hr_chart, width='stretch')
                            
                            # Individual SpO2 Chart
                            st.markdown("**SpO2 (%)**")
                            spo2_chart = alt.Chart(v_df).mark_line(color="#22c55e", strokeWidth=2).encode(
                                x=alt.X('timestamp:T', title='Time'),
                                y=alt.Y('spo2:Q', title='SpO2 %', scale=alt.Scale(zero=False)),
                                tooltip=['timestamp:T', 'spo2:Q', 'blood_pressure:N', 'simulation_profile:N']
                            ).properties(height=280)
                            st.altair_chart(spo2_chart, width='stretch')
                            
                            # CSV Download Button for Patient Vitals
                            csv_data = v_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Export Patient Vitals CSV",
                                data=csv_data,
                                file_name=f"pulsegrid_patient_{selected_id}_vitals.csv",
                                mime="text/csv"
                            )
                            
                            with st.expander("View Raw Vitals Logs Table"):
                                st.dataframe(v_df.sort_values("timestamp", ascending=False), hide_index=True, width='stretch')
                        else:
                            st.info("No vital logs recorded for this patient.")
                    except Exception as e:
                        st.info(f"Could not load vitals charts: {e}")
        else:
            st.warning("No patients match your search filter.")

except Exception as e:
    st.error(f"Error connecting to patient records: {e}")