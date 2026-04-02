import mysql.connector


def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="school_db"
    )


def initialize_database():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS school_db")
    cursor.execute("USE school_db")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            subject_id INT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()