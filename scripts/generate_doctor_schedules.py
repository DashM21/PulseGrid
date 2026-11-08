
import mysql.connector
import random
from datetime import date, timedelta, time

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

try:
    cursor.execute("SELECT COUNT(*) FROM doctor_schedules")

    if cursor.fetchone()[0] > 0:
        raise Exception(
            "Schedules already exist. No records inserted."
        )

    cursor.execute("""
        SELECT doctor_id
        FROM doctors
        ORDER BY doctor_id
    """)

    doctors = [row[0] for row in cursor.fetchall()]

    if len(doctors) != 40:
        raise Exception(
            f"Expected 40 doctors, found {len(doctors)}"
        )

    shifts = {
        "Morning": (time(6, 0), time(14, 0)),
        "Evening": (time(14, 0), time(22, 0)),
        "Night": (time(22, 0), time(6, 0))
    }

    shift_names = list(shifts.keys())

    schedules = []

    today = date.today()

    for doctor_id in doctors:

        for day_number in range(30):

            shift_date = today - timedelta(
                days=day_number
            )

            shift_name = random.choice(shift_names)

            start_time, end_time = shifts[shift_name]

            duty_status = random.choices(
                ["Scheduled", "Completed", "On Leave"],
                weights=[20, 70, 10]
            )[0]

            schedules.append((
                doctor_id,
                shift_date,
                shift_name,
                start_time,
                end_time,
                duty_status
            ))

    cursor.executemany(
        """
        INSERT INTO doctor_schedules
        (
            doctor_id,
            shift_date,
            shift_type,
            start_time,
            end_time,
            duty_status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        schedules
    )

    conn.commit()

    print("Doctor schedule generation completed!")
    print(f"Doctors: {len(doctors)}")
    print(f"Schedule records: {len(schedules)}")

except Exception as error:
    conn.rollback()
    print("Operation stopped:", error)

finally:
    cursor.close()
    conn.close()
