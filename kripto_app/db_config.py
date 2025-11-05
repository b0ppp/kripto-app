# db_config.py
import psycopg2
import streamlit as st
from psycopg2 import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_kripto"
}

def get_connection():
    try:
        conn_string = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(conn_string)
        return conn
    except Error as e:
        print("DB connection error:", e)
        return None

def init_db():  
    conn = get_connection()
    if conn is None:
        print("Gagal koneksi DB saat init.")
        return

    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        activity_type VARCHAR(100),
        log_encrypted LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()
