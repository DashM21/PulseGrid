
import mysql.connector
import random

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

equipment_types = {
    "Cardiology": [
        "ECG Machine",
        "Cardiac Monitor",
        "Defibrillator",
        "Echocardiography Machine"
    ],
    "Neurology": [
        "EEG Machine",
        "Neuro Monitor",
        "CT Scanner"
    ],
    "Emergency Medicine": [
        "Portable Monitor",
        "Defibrillator",
        "Ventilator"
    ],
    "General Medicine": [
        "Patient Monitor",
        "Infusion Pump",
        "Nebulizer"
    ],
    "Orthopedics": [
        "X-Ray Machine",
        "Traction Equipment",
        "C-Arm Machine"
    ],
    "Nephrology": [
        "Dialysis Machine",
        "Renal Monitor",
        "Water Treatment Unit"
    ],
    "Radiology": [
        "MRI Scanner",
        "CT Scanner",
        "X-Ray Machine",
        "Ultrasound Machine"
    ],
    "Intensive Care Unit": [
        "Ventilator",
        "Multiparameter Monitor",
        "Infusion Pump"
    ]
}

try:
    cursor.execute("SELECT COUNT(*) FROM equipment")

    if cursor.fetchone()[0] > 0:
        raise Exception(
            "Equipment records already exist. Stopping."
        )

    cursor.execute("""
        SELECT department_id, department_name
        FROM departments
    """)

    departments = cursor.fetchall()

    records = []

    for department_id, department_name in departments:

        names = equipment_types[department_name]

        for i in range(10):

            equipment_name = random.choice(names)

            quantity = random.randint(3, 15)

            available_quantity = random.randint(
                0, quantity
            )

            maintenance_status = random.choices(
                ["Operational", "Under Maintenance", "Needs Inspection"],
                weights=[75, 15, 10]
            )[0]

            records.append((
                equipment_name,
                department_id,
                quantity,
                available_quantity,
                maintenance_status
            ))

    cursor.executemany(
        """
        INSERT INTO equipment
        (
            equipment_name,
            department_id,
            quantity,
            available_quantity,
            maintenance_status
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        records
    )

    conn.commit()

    print("Equipment inventory generated!")
    print(f"Equipment records: {len(records)}")

except Exception as error:
    conn.rollback()
    print("Operation stopped:", error)

finally:
    cursor.close()
    conn.close()
