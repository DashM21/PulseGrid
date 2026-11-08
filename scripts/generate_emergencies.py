
import mysql.connector
import random
from datetime import datetime, timedelta

from config import DB_HOST, DB_USER, DB_PASSWORD

DB_NAME = "pulsegrid_large_db"

random.seed(42)

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=3306,
    use_pure=True
)

cursor = conn.cursor()

emergency_types = [
    "Cardiac Emergency",
    "Breathing Difficulty",
    "Neurological Event",
    "Trauma",
    "Severe Infection",
    "Renal Emergency",
    "Accident",
    "General Emergency"
]

priorities = [
    "Critical",
    "High",
    "Moderate",
    "Low"
]

response_statuses = [
    "Responded",
    "Under Treatment",
    "Transferred",
    "Closed"
]

priority_weights = [10, 25, 40, 25]

try:
    cursor.execute(
        "SELECT COUNT(*) FROM emergency_records"
    )

    if cursor.fetchone()[0] > 0:
        raise Exception(
            "Emergency records already exist. Stopping."
        )

    cursor.execute("""
        SELECT patient_id
        FROM patients
    """)

    patient_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT department_id
        FROM departments
    """)

    department_ids = [row[0] for row in cursor.fetchall()]

    if len(patient_ids) != 250:
        raise Exception("Patient count is not 250.")

    if len(department_ids) != 8:
        raise Exception("Department count is not 8.")

    records = []

    now = datetime.now()

    for _ in range(200):

        patient_id = random.choice(patient_ids)

        department_id = random.choice(department_ids)

        emergency_type = random.choice(emergency_types)

        priority = random.choices(
            priorities,
            weights=priority_weights
        )[0]

        response_status = random.choice(
            response_statuses
        )

        event_time = now - timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        records.append((
            patient_id,
            department_id,
            emergency_type,
            priority,
            event_time,
            response_status
        ))

    cursor.executemany(
        """
        INSERT INTO emergency_records
        (
            patient_id,
            department_id,
            emergency_type,
            priority,
            event_time,
            response_status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        records
    )

    conn.commit()

    print("Emergency dataset generated!")
    print(f"Emergency records: {len(records)}")

except Exception as error:
    conn.rollback()
    print("Operation stopped:", error)

finally:
    cursor.close()
    conn.close()
