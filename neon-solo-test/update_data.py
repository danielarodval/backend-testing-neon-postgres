import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
conn_string = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(conn_string) as conn:
        print("Connected to the database successfully!")
        with conn.cursor() as cur:
            # update the data in the table
            cur.execute(
                "UPDATE test_table SET name = 'Updated Name' WHERE id = 1"
            )

            print("Updated the record in test_table successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.")
