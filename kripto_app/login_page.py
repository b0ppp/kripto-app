import streamlit as st
from db_config import init_db, get_connection
from rumus_crypto import hash_sha256

# --- Fungsi Database Anda (Murni) ---
def register_user(username: str, password: str) -> bool:
    conn = get_connection()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, hash_sha256(password)))
        conn.commit()
        return True
    except Exception as e:
        print("register error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def check_login(username: str, password: str):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, password_hash FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        if not row:
            return None
        user_id, usern, pass_hash = row
        if pass_hash == hash_sha256(password):
            return {"id": user_id, "username": usern}
        return None
    finally:
        cur.close()
        conn.close()

# --- Halaman Login (Sudah Diperbaiki) ---
def login_page():
    
    # st.title("🔐 Login") # DIHAPUS DARI SINI
    init_db()  # pastikan tabel ada saat pertama kali
    # st.write("Silakan login atau daftar akun baru.") # DIHAPUS DARI SINI

    menu = st.radio("Menu:", ["Login", "Register"], index=0, horizontal=True)
    
    if menu == "Register":
        st.title("Buat Akun Baru - 🗝️") # DIPINDAHKAN KE SINI
        uname = st.text_input("Username (baru)", key="reg_user")
        pwd = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Daftar"):
            if not uname or not pwd:
                st.warning("Isi username & password.")
            else:
                ok = register_user(uname, pwd)
                if ok:
                    st.success("Akun berhasil dibuat. Silakan login.")
                else:
                    st.error("Gagal membuat akun (mungkin username sudah ada).")
    else:
        st.title("Masuk - 🔐") 
        uname = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pass")
        if st.button("Masuk"):
            user = check_login(uname, pwd)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]
                # st.success("Login berhasil!") # DIGANTI DENGAN st.rerun()
                st.rerun() # PERBAIKAN: Paksa app.py untuk refresh
            else:
                st.error("Username atau password salah.")

