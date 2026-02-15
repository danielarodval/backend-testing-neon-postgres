import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn_string = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(conn_string) as conn:
        print("Connected to the database successfully!")

        with conn.cursor() as cur:
            # fetch all records from the test_table
            cur.execute("SELECT * FROM test_table;")
            records = cur.fetchall()
            print("Fetched records from test_table:")

            # print each record
            for record in records:
                print(record)
                
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.")