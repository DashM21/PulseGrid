
import mysql.connector
import random
from datetime import datetime, date, time, timedelta

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

cursor.execute("SELECT COUNT(*) FROM vitals_logs")
existing_count = cursor.fetchone()[0]

if existing_count > 0:
    print(
        f"Stopped: vitals_logs already contains "
        f"{existing_count} records."
    )
    print("No additional records were inserted.")
    cursor.close()
    conn.close()
    raise SystemExit

# =====================================
# FETCH PATIENTS
# =====================================

cursor.execute("""
    SELECT patient_id, admission_date
    FROM patients
    ORDER BY patient_id
""")

patients = cursor.fetchall()

if len(patients) != 250:
    print(f"Expected 250 patients, found {len(patients)}.")
    cursor.close()
    conn.close()
    raise SystemExit

# =====================================
# SIMULATION PROFILES
# Educational synthetic data only
# =====================================

profiles = {
    "Routine": {
        "hr": (70, 90),
        "spo2": (96, 100),
        "sys": (105, 130),
        "dia": (65, 85)
    },

    "Observation": {
        "hr": (105, 115),
        "spo2": (96, 99),
        "sys": (145, 155),
        "dia": (70, 90)
    },

    "Escalation": {
        "hr": (125, 135),
        "spo2": (88, 91),
        "sys": (165, 175),
        "dia": (75, 95)
    }
}

profile_names = ["Routine", "Observation", "Escalation"]
profile_weights = [70, 20, 10]

# =====================================
# GENERATE HISTORICAL READINGS
# =====================================

now = datetime.now()
records = []

for patient_id, admission_date in patients:

    if isinstance(admission_date, str):
        admission_date = date.fromisoformat(admission_date)

    start_time = datetime.combine(
        admission_date,
        time(8, 0)
    )

    if start_time > now:
        start_time = now

    available_seconds = max(
        0,
        int((now - start_time).total_seconds())
    )

    for _ in range(40):

        profile_name = random.choices(
            profile_names,
            weights=profile_weights
        )[0]

        profile = profiles[profile_name]

        heart_rate = random.randint(*profile["hr"])
        spo2 = random.randint(*profile["spo2"])

        systolic = random.randint(*profile["sys"])
        diastolic = random.randint(*profile["dia"])

        blood_pressure = f"{systolic}/{diastolic}"

        reading_time = start_time + timedelta(
            seconds=random.randint(0, available_seconds)
        )

        records.append((
            patient_id,
            heart_rate,
            spo2,
            blood_pressure,
            reading_time,
            "Advanced",
            profile_name
        ))

# =====================================
# INSERT IN BATCHES
# =====================================

query = """
    INSERT INTO vitals_logs
    (
        patient_id,
        heart_rate,
        spo2,
        blood_pressure,
        `timestamp`,
        simulation_mode,
        simulation_profile
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

batch_size = 1000

for start in range(0, len(records), batch_size):

    batch = records[start:start + batch_size]

    cursor.executemany(query, batch)
    conn.commit()

    print(
        f"Inserted {min(start + batch_size, len(records))}"
        f" / {len(records)} readings"
    )

print("\nHistorical data generation completed!")

cursor.execute("SELECT COUNT(*) FROM vitals_logs")
total = cursor.fetchone()[0]

print(f"Total vital readings: {total}")

cursor.close()
conn.close()
