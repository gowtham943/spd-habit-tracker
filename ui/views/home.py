import streamlit as st

st.title("⚡ Welcome to SPD Habit Tracker!")
display_name = "UserX"
if st.session_state.user:
    display_name = st.session_state.user.get("display_name", "Don")
st.subheader(f"Greetings, {display_name}! Where would you like to travel today?")
st.write("Use the portals below to navigate through your productivity.")

st.divider()

# Create a 2x2 Grid Layout
col1, col2 = st.columns(2, gap="large")

# --- COLUMN 1 ---
with col1:
    # Card 1: Dashboard
    with st.container(border=True):
        st.markdown("### 🏰 Dashboard")
        st.write(
            "Get a bird's-eye view of your entire campaign. Check your monthly mastery, view the daily habits, and see urgent tasks."
        )
        st.write("") 
        if st.button("Enter Dashboard ➔", key="btn_dash", use_container_width=True):
            st.switch_page("views/dashboard.py")

    st.write("") 

    # Card 2: Tracker
    with st.container(border=True):
        st.markdown("### 📈 Habit Tracker")
        st.write(
            "Time-travel through your calendar! Log your daily habits, check past days, and view your epic yearly dominance chart."
        )
        st.write("")  # Spacer
        if st.button("Open Tracker ➔", key="btn_track", use_container_width=True):
            st.switch_page("views/tracker.py")

# --- COLUMN 2 ---
with col2:
    # Card 3: Habits
    with st.container(border=True):
        st.markdown("### 📜 Your Habits")
        st.write(
            "The core of your power. Add new daily or weekly repeating habits to your scrolls and build your foundation."
        )
        st.write("")  # Spacer
        if st.button("Manage Habits ➔", key="btn_habits", use_container_width=True):
            st.switch_page("views/habits.py")

    st.write("")  # Vertical spacer

    # Card 4: Tasks
    with st.container(border=True):
        st.markdown("### 🎯 Task Remainder")
        st.write(
            "One-off missions with deadlines. Stay on top of urgent tasks."
        )
        st.write("")  # Spacer
        if st.button("View Tasks ➔", key="btn_tasks", use_container_width=True):
            st.switch_page("views/tasks.py")
