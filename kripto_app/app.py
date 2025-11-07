import streamlit as st

st.set_page_config(page_title="Crypton - 115, 231", page_icon="🔐")

from login_page import login_page
from home_page import home_page
from history_manager import fetch_history

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
