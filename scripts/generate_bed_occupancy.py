
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD

DB_NAME = "pulsegrid_large_db"

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=3306,
    use_pure=True
)

cursor = conn.cursor()

try:
    # Safety checks
    cursor.execute("SELECT COUNT(*) FROM beds WHERE patient_id IS NOT NULL")
    assigned_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bed_history")
    history_count = cursor.fetchone()[0]

    if assigned_count > 0 or history_count > 0:
        raise Exception(
            "Existing bed assignments or history found. "
            "No changes made."
        )

    # Fetch active patients
    cursor.execute("""
        SELECT patient_id
        FROM patients
        WHERE status IN ('Admitted', 'Under Observation')
        ORDER BY patient_id
    """)

    active_patients = [row[0] for row in cursor.fetchall()]

    # Fetch available beds
    cursor.execute("""
        SELECT bed_id
        FROM beds
        WHERE status = 'Available'
        ORDER BY bed_id
    """)

    available_beds = [row[0] for row in cursor.fetchall()]

    if len(active_patients) != 139:
        raise Exception(
            f"Expected 139 active patients, found {len(active_patients)}"
        )

    if len(available_beds) != 120:
        raise Exception(
            f"Expected 120 available beds, found {len(available_beds)}"
        )

    # Assign first 120 active patients
    assignments = []

    for bed_id, patient_id in zip(
        available_beds,
        active_patients
    ):
        assignments.append((patient_id, bed_id))

    for patient_id, bed_id in assignments:

        cursor.execute("""
            UPDATE beds
            SET status = 'Occupied',
                patient_id = %s
            WHERE bed_id = %s
        """, (patient_id, bed_id))

        cursor.execute("""
            INSERT INTO bed_history
            (bed_id, patient_id, status, recorded_at)
            VALUES (%s, %s, 'Occupied', NOW())
        """, (bed_id, patient_id))

    conn.commit()

    print("Bed occupancy generation completed!")
    print(f"Occupied beds: {len(assignments)}")
    print(f"Patients without beds: {len(active_patients) - len(assignments)}")

except Exception as error:
    conn.rollback()
    print("Operation stopped:", error)

finally:
    cursor.close()
    conn.close()
