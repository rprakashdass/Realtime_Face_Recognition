import mysql.connector
from datetime import datetime

db_connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='face_attendance'
)

db_cursor = db_connection.cursor()

data = {
    "22ML039":
        {
            "name": "Prakash Dass R",
            "rollNumber": "22ML039",
            "department": "AIML",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        },
    "22AD008":
        {
            "name": "Arasu Pandian V",
            "rollNumber": "22AD008",
            "department": "AIDS",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        },
    "22AD026":
        {
            "name": "Eshwar K",
            "rollNumber": "22AD026",
            "department": "AIDS",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        },
    "22ME040":
        {
            "name": "Elon Musk",
            "rollNumber": "22ML040",
            "department": "MECH",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        },
    "22ML041":
        {
            "name": "Emily",
            "rollNumber": "22ML041",
            "department": "IT",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        },
    "22ML042":
        {
            "name": "Zuckerberg",
            "rollNumber": "22ML042",
            "department": "IT",
            "last_attendance_time": datetime(2022, 12, 11, 0, 54, 34)
        }
}

for key, value in data.items():

    # id = key
    name = value["name"]
    rollNumber = value["rollNumber"]
    department = value["department"]
    last_attendance_time = value["last_attendance_time"]

    # Check if the roll number exists in the database
    db_cursor.execute("SELECT * FROM students WHERE rollnumber = %s", (rollNumber,))
    existing_record = db_cursor.fetchone()

    # Convert last_attendance_time to a datetime object
    # last_attendance_time = datetime(last_attendance_time, "%Y-%m-%d %H:%M:%S")

    if existing_record:
        sql_query = "UPDATE students SET name = %s, department = %s, last_attendance_time = %s WHERE rollnumber = %s"
        values = (name, department, last_attendance_time, rollNumber)
    else:
        sql_query = "INSERT INTO students (name, rollnumber, department, last_attendance_time) VALUES (%s, %s, %s, %s)"
        values = (name, rollNumber, department, last_attendance_time)

    # Execute the query
    db_cursor.execute(sql_query, values)

    # Commit the changes
    db_connection.commit()


# Function to close the database connection
def close_db_connection():
    db_cursor.close()
    db_connection.close()


# Close the database connection
close_db_connection()