import mysql.connector
import random
from datetime import date, timedelta

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
# PATIENT DATA
# =====================================

first_names = [
    "Aarav", "Ananya", "Rohan", "Kavya", "Arjun",
    "Ishita", "Vihaan", "Meera", "Aditya", "Diya",
    "Kabir", "Sara", "Reyansh", "Myra", "Dev",
    "Anika", "Vivaan", "Saanvi", "Krish", "Aadhya",
    "Dhruv", "Pari", "Yash", "Riya", "Atharv"
]

last_names = [
    "Sharma", "Patel", "Mehta", "Shah", "Desai",
    "Verma", "Rao", "Joshi", "Gupta", "Nair",
    "Singh", "Khan", "Das", "Iyer", "Kapoor",
    "Sen", "Malhotra", "Trivedi", "Soni", "Mishra"
]

genders = ["Male", "Female", "Other"]

statuses = [
    "Admitted",
    "Discharged",
    "Under Observation"
]

today = date.today()

patients = []

for i in range(250):

    name = (
        random.choice(first_names)
        + " "
        + random.choice(last_names)
    )

    age = random.randint(18, 85)
    gender = random.choices(
        genders,
        weights=[48, 48, 4]
    )[0]

    admission_date = today - timedelta(
        days=random.randint(0, 180)
    )

    status = random.choices(
        statuses,
        weights=[45, 40, 15]
    )[0]

    patients.append((
        name,
        age,
        gender,
        admission_date,
        status
    ))

cursor.executemany(
    """
    INSERT INTO patients
    (name, age, gender, admission_date, status)
    VALUES (%s, %s, %s, %s, %s)
    """,
    patients
)

conn.commit()

print("250 patients inserted successfully.")

# =====================================
# BED GENERATION
# =====================================

wards = {
    "ICU": 20,
    "General": 45,
    "Emergency": 20,
    "Private": 20,
    "Cardiac": 15
}

bed_records = []

for ward, capacity in wards.items():

    for number in range(1, capacity + 1):

        bed_number = f"{ward.upper()}-{number:03d}"

        bed_records.append((
            bed_number,
            ward,
            "Available",
            None
        ))

cursor.executemany(
    """
    INSERT INTO beds
    (bed_number, ward, status, patient_id)
    VALUES (%s, %s, %s, %s)
    """,
    bed_records
)

conn.commit()

print("120 beds inserted successfully.")

cursor.close()
conn.close()

print("PULSEGRID large dataset generation completed.")