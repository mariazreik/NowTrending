import psycopg2
# import sys
import os
import logging
import streamlit as st

# # Add the parent directory to Python's module search path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

# Database Credentials
DB_HOST=st.secrets["DB_HOST"]
DB_NAME=st.secrets["DB_NAME"]
DB_USER=st.secrets["DB_USER"]
DB_PASS=st.secrets["DB_PASS"]
DB_PORT=st.secrets["DB_PORT"]

# Configure logging to only show ERROR or CRITICAL messages
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Optionally, you can set specific loggers to CRITICAL, to prevent messages from specific modules
logging.getLogger("psycopg2").setLevel(logging.ERROR)  # This suppresses logs from psycopg2

def get_db_connection():
    """Establishes a database connection and returns the connection object."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        logging.info("✅ Database connection established successfully.")  # This line won't show now
        return conn
    except psycopg2.DatabaseError as e:
        logging.error(f"❌ Database connection error: {e}")
        return None


def execute_schema():
    """Reads and executes the schema.sql file to set up database tables."""
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database.")
        return False

    schema_path = "database/schema.sql"
    if not os.path.exists(schema_path):
        logging.error(f"Schema file not found: {schema_path}")
        return False

    try:
        with conn, conn.cursor() as cur:  # Ensures connection closes automatically
            with open(schema_path, "r") as file:
                sql_script = file.read()
                cur.execute(sql_script)
            logging.info("✅ Database schema executed successfully.")  # This line won't show now
            return True
    except psycopg2.DatabaseError as e:
        logging.error(f"❌ Error executing schema: {e}")
        return False


if __name__ == "__main__":
    if execute_schema():
        logging.info("Schema setup completed successfully.")  # This line won't show now
    else:
        logging.error("Schema setup failed.")
