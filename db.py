import os
import psycopg2
from dotenv import load_dotenv



load_dotenv("proj.env")



def get_db_connection():
    """Returns a database connection using environment variables."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
def create_tables():
    """Executes schema.sql to create tables in PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        sql_statements = f.read().split(";")  # Split SQL file at each semicolon
        for statement in sql_statements:
            if statement.strip():  # Ignore empty statements
                cursor.execute(statement)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()