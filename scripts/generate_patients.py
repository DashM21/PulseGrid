
import random
import database

# Fictional sample names for the PULSEGRID demonstration
first_names = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan",
    "Ishaan", "Kabir", "Dev", "Rahul", "Karan",
    "Ananya", "Diya", "Aadhya", "Isha", "Meera",
    "Kavya", "Priya", "Riya", "Sana", "Nisha",
    "Krish", "Yash", "Manav", "Dhruv", "Reyansh"
]

last_names = [
    "Sharma", "Patel", "Mehta", "Shah", "Verma",
    "Desai", "Joshi", "Rao", "Gupta", "Singh"
]

def generate_patients():

    existing = database.fetch_data(
        "SELECT COUNT(*) AS total FROM patients"
    )

    if existing and existing[0]["total"] > 0:
        print("Patients already exist. No new records inserted.")
        return

    statuses = ["Stable", "Under Observation", "Critical"]
    genders = ["Male", "Female"]

    for i in range(50):

        name = (
            random.choice(first_names)
            + " "
            + random.choice(last_names)
        )

        age = random.randint(18, 85)
        gender = random.choice(genders)
        status = random.choices(
            statuses,
            weights=[65, 25, 10]
        )[0]

        query = """
            INSERT INTO patients (name, age, gender, status)
            VALUES (%s, %s, %s, %s)
        """

        success = database.execute_query(
            query,
            (name, age, gender, status)
        )

        if not success:
            print("Insertion failed. Stopping.")
            return

    print("50 fictional patients generated successfully!")

if __name__ == "__main__":
    generate_patients()
