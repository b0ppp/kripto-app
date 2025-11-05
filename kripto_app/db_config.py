import psycopg2
import streamlit as st
from psycopg2 import Error

def get_connection():
    
    try:
        conn_string = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(conn_string)
        return conn
    except Error as e:
        print(f"DB connection error: {e}")
        st.error(f"Gagal terhubung ke database. Cek 'Secrets' di Streamlit Cloud.") 
        return None
    except Exception as e:
        if "does not exist" in str(e):
            st.error("DATABASE_URL secret belum diatur di Streamlit Cloud.")
        else:
            st.error(f"Terjadi error: {e}")
        return None


def init_db():  
    """
    Inisialisasi tabel di database PostgreSQL.
    (Fungsi ini YANG DIPERBAIKI)
    """
    conn = get_connection()
    if conn is None:
        print("Gagal koneksi DB saat init.")
        return

    cursor = conn.cursor()
    try:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "users" (
            "id" SERIAL PRIMARY KEY,
            "username" VARCHAR(255) UNIQUE NOT NULL,
            "password_hash" VARCHAR(255) NOT NULL
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "history_log" (
            "id" SERIAL PRIMARY KEY,
            "user_id" INT,
            "activity_type" VARCHAR(100),
            "log_encrypted" TEXT,
            "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE
        )
        """)
        conn.commit()
        print("Inisialisasi database (PostgreSQL) berhasil.")
    except Error as e:
        print(f"Error saat init_db: {e}")
        conn.rollback() 
    finally:
        cursor.close()
        conn.close()