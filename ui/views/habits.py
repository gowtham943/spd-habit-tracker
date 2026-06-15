import streamlit as st
from client import api_client
from chat.sidebar_chat import render_global_chatbot

st.set_page_config(layout="wide")

# 🚀 INJECT THE GLOBAL CHATBOT RIGHT HERE
render_global_chatbot()

st.title("📜 Your Habit Scrolls")

# Sidebar for adding habits
with st.sidebar:
    st.header("➕ Add New Habit")
    with st.form("new_habit"):
        new_name = st.text_input("Habit Name")
        new_frequency = st.text_input("Frequency (e.g., Daily, Weekly)")
        if st.form_submit_button("Create Habit"):
            if api_client.add_habit(st.session_state.token, new_name, new_frequency):
                st.success("Habit Added!")
                st.rerun()

# Main Display
habits = api_client.fetch_habits(st.session_state.token)

if not habits:
    st.info("You don't have any Habits yet! Add one from the sidebar.")

for habit in habits:
    st.markdown(
        f"""
        <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B; color: black;">
            <h3 style="margin:0;">{habit['name']}</h3>
            <p style="margin:0; color: gray;">Frequency: {habit['frequency']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
