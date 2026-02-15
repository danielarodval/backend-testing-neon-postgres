import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn_string = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(conn_string) as conn:
        print("Connected to the database successfully!")

        # Delete data from the test_table 
        with conn.cursor() as cur:
            cur.execute("DELETE FROM test_table WHERE id = 1;")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.")