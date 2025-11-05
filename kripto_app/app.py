import streamlit as st

# WAJIB paling atas sebelum import modul lain yang pakai Streamlit
st.set_page_config(page_title="Kripto App - Kelompok 8", page_icon="🔐")

# Baru import modul lainnya
from login_page import login_page
from home_page import home_page
from history_manager import fetch_history

# --- sisa kode kamu tetap sama ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""

if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title("Home Page\n\n")
    logout_button = st.sidebar.button("🚪 Logout")

    if logout_button:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.success("Berhasil logout.")
        
    else:
        home_page()
