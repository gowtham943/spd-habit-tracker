import streamlit as st
from streamlit_cookies_controller import CookieController
from client import api_client

st.set_page_config(page_title="SPD Habit Tracker", page_icon="⚡", layout="wide")

# 1. INITIALIZE ONCE AND SHARE IT globally via session state
cookie_controller = CookieController()
if "cookie_manager" not in st.session_state:
    st.session_state.cookie_manager = cookie_controller

# 2. Session Recovery
saved_token = cookie_controller.get("auth_token")

if saved_token:
    st.session_state.token = saved_token
    if "user" not in st.session_state or st.session_state.user is None:
        st.session_state.user = api_client.get_current_user(saved_token)
elif "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None

# 3. Define the Pages
login_page = st.Page("views/login.py", title="Login / Register", icon="🛡️")
home_page = st.Page("views/home.py", title="Home", icon="🏠", default=True)
dashboard_page = st.Page("views/dashboard.py", title="Dashboard", icon="🏰")
habits_page = st.Page("views/habits.py", title="Your Habits", icon="📜")
tracker_page = st.Page("views/tracker.py", title="Habits Tracker", icon="📈")
tasks_page = st.Page("views/tasks.py", title="Task remainder", icon="🎯")

# 4. The Magic Router
if st.session_state.token is None:
    pg = st.navigation([login_page])
else:
    pg = st.navigation(
        [home_page, dashboard_page, habits_page, tracker_page, tasks_page]
    )

    # Add the Logout button safely
    with st.sidebar:
        st.divider()

        # DEFENSIVE CHECK FOR USER DATA
        user_name = "Hello User"
        if st.session_state.user:
            user_name = st.session_state.user.get("display_name", "Hello User")

        st.write(f"Don: **{user_name}**")

        if st.button("Log Out"):
            # Safely try to remove the cookie (ignore if it's already gone)
            try:
                if st.session_state.cookie_manager.get("auth_token"):
                    st.session_state.cookie_manager.remove("auth_token")
            except KeyError:
                pass  # The cookie was already missing, no problem!

            # Clear the session state
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

# 5. Execute the selected page
pg.run()
