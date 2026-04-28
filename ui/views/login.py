import streamlit as st
from client import api_client

cookie_controller = st.session_state.cookie_manager
st.title("🛡️ Welcome to Sai Priya Dharsini's Tracker!")
st.write("Enter the realm to access your quests.")

# Two tabs for a clean UI
tab_login, tab_register = st.tabs(["Login", "Register New Don"])

with tab_login:
    with st.form("login_form"):
        username = st.text_input("Don's Username")
        password = st.text_input("Don's Password", type="password")
        if st.form_submit_button("Enter Realm"):
            token = api_client.login(username, password)
            if token:
                cookie_controller.set("auth_token", token)
                st.session_state.token = token
                st.session_state.user = api_client.get_current_user(token)
                st.rerun()
            else:
                st.error("Incorrect email or password!")

with tab_register:
    with st.form("register_form"):
        new_email = st.text_input("Don's username")
        new_name = st.text_input("Don's Display Name")
        new_password = st.text_input("Don's Password", type="password")
        if st.form_submit_button("Join the Quest"):
            success = api_client.register_user(new_email, new_name, new_password)
            if success:
                st.success("Account created! You can now log in.")
                st.balloons()
            else:
                st.error("Could not create account. username might be taken!")
