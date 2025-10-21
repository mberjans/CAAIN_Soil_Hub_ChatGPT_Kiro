import os
import psycopg2

def apply_schema(db_url, schema_file):
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        with open(schema_file, 'r') as f:
            cur.execute(f.read())
        conn.commit()
        print(f"Schema from {schema_file} applied successfully.")
    except Exception as e:
        print(f"Error applying schema: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Replace with your actual database URL or environment variable
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
    SCHEMA_FILE = "/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/databases/postgresql/tissue_test_schema.sql"
    apply_schema(DATABASE_URL, SCHEMA_FILE)
