import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn_string = os.getenv("DATABASE_URL")

try:
    with psycopg2.connect(conn_string) as conn:
        print("Connected to the database successfully!")

        with conn.cursor() as cur:
            # Drop the table if it already exists
            cur.execute("DROP TABLE IF EXISTS test_table;")
            print("Dropped existing test_table if it existed.")

            # Create a new table
            cur.execute("""
                CREATE TABLE test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("Created test_table successfully.")

            # insert a sample record
            cur.execute("""
                INSERT INTO test_table (name) VALUES ('Sample Name');
            """)
            print("Inserted a sample record into test_table.")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.")