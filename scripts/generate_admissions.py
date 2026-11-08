
import mysql.connector
import random
from datetime import datetime, date, timedelta, time

from config import DB_HOST, DB_USER, DB_PASSWORD

DB_NAME = "pulsegrid_large_db"

random.seed(42)

# =====================================
# DATABASE CONNECTION
# =====================================

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=3306,
    use_pure=True
)

cursor = conn.cursor()

# =====================================
# SAFETY CHECK
# =====================================

cursor.execute("SELECT COUNT(*) FROM admissions")
if cursor.fetchone()[0] > 0:
    print("Admission records already exist. Stopping.")
    cursor.close()
    conn.close()
    raise SystemExit

# =====================================
# FETCH DEPARTMENTS
# =====================================

cursor.execute("""
    SELECT department_id
    FROM departments
""")

department_ids = [row[0] for row in cursor.fetchall()]

if not department_ids:
    print("No departments found. Stopping.")
    cursor.close()
    conn.close()
    raise SystemExit

# =====================================
# FETCH PATIENTS
# =====================================

cursor.execute("""
    SELECT patient_id, admission_date, status
    FROM patients
    ORDER BY patient_id
""")

patients = cursor.fetchall()

today = date.today()

admissions = []

admission_types = [
    "Emergency",
    "Elective",
    "Referral"
]

for patient_id, admission_date, status in patients:

    if isinstance(admission_date, str):
        admission_date = date.fromisoformat(admission_date)

    admission_datetime = datetime.combine(
        admission_date,
        time(
            random.randint(6, 22),
            random.choice([0, 15, 30, 45])
        )
    )

    discharge_datetime = None

    if status == "Discharged":

        available_days = max(
            1,
            (today - admission_date).days
        )

        stay_days = random.randint(
            1,
            min(30, available_days)
        )

        discharge_date = min(
            admission_date + timedelta(days=stay_days),
            today
        )

        discharge_datetime = datetime.combine(
            discharge_date,
            time(10, 0)
        )

    admissions.append((
        patient_id,
        random.choice(department_ids),
        admission_datetime,
        discharge_datetime,
        random.choice(admission_types),
        status
    ))

# =====================================
# INSERT ADMISSION RECORDS
# =====================================

cursor.executemany(
    """
    INSERT INTO admissions
    (
        patient_id,
        department_id,
        admission_date,
        discharge_date,
        admission_type,
        admission_status
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    admissions
)

conn.commit()

print(f"{len(admissions)} admission records inserted.")

cursor.close()
conn.close()

print("Admission history generation completed!")
