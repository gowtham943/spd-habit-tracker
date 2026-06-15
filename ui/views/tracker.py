import streamlit as st
from client import api_client
import pandas as pd
import plotly.express as px
from chat.sidebar_chat import render_global_chatbot

st.set_page_config(layout="wide")

# 🚀 INJECT THE GLOBAL CHATBOT RIGHT HERE
render_global_chatbot()

st.title("📈 Habit Tracker")

habits = api_client.fetch_habits(st.session_state.token)

if not habits:
    st.warning("Go to 'Your Habits' to create a habit first!")
    st.stop()

# Use Tabs to separate Today's Actions from Historical Data
# Rename the tab to reflect the new time-travel ability!
tab_log, tab_month, tab_year = st.tabs(
    ["📅 The Quest Logbook", "📊 Monthly Stats", "🏆 Yearly Dominance"]
)

# ==========================================
# THE LOGBOOK TAB (The New Calendar!)
# ==========================================
with tab_log:
    st.subheader("Time Travel Check-in 📅")
    st.write("Pick a day on the calendar to log your Habit!")

    # 1. THE CALENDAR WIDGET
    # Defaults to today, but lets the user click and open a full monthly calendar
    selected_date = st.date_input("Select Date", value=pd.to_datetime("today"))

    st.divider()
    st.markdown(f"### Habits for **{selected_date.strftime('%B %d, %Y')}**")

    # 2. THE QUEST LIST
    for habit in habits:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{habit['name']}** ({habit['frequency']})")
        with col2:
            # CRITICAL: We add the selected_date to the button's key.
            # This forces Streamlit to reset the button if the user changes the calendar day!
            button_key = f"log_{habit['id']}_{selected_date}"

            if st.button("✅ Mark Done", key=button_key):
                # Pass the selected_date to our upgraded API client
                success, msg = api_client.log_habit(
                    st.session_state.token, habit["id"], selected_date
                )

                if success:
                    st.balloons()
                    st.success(f"{msg} Logged for {selected_date.strftime('%b %d')}!")
                else:
                    st.warning(msg)
        st.divider()

with tab_month:
    st.subheader("Monthly Streak Viewer")
    st.info("Select a habit to see its history logs.")

    # Let the user pick a habit to view stats for
    habit_names = {h["name"]: h["id"] for h in habits}
    selected_habit_name = st.selectbox("Choose Habit", list(habit_names.keys()))

    if selected_habit_name:
        habit_id = habit_names[selected_habit_name]
        logs = api_client.fetch_logs(st.session_state.token, habit_id)

        st.metric("Total Times Completed", len(logs))

        # Display the raw logs (In the future, you can turn this into a calendar chart!)
        for log in logs:
            st.write(f"✅ Completed on: **{log['completed_date']}**")

with tab_year:
    st.subheader("🏆 Yearly Dominance")
    st.write("Watch your overall power level grow over the year!")

    # 1. Fetch all logs for all habits
    all_logs = []

    # st.spinner shows a cool loading animation while it fetches data
    with st.spinner("Gathering your epic history..."):
        for habit in habits:
            logs = api_client.fetch_logs(st.session_state.token, habit["id"])
            for log in logs:
                all_logs.append({"Habit": habit["name"], "Date": log["completed_date"]})

    # 2. Check if we actually have data to draw
    if not all_logs:
        st.info("No habits completed yet this year. Time to start grinding!")
    else:
        # 3. Use Pandas to crunch the numbers
        df = pd.DataFrame(all_logs)
        df["Date"] = pd.to_datetime(df["Date"])

        # Extract the month for grouping (e.g., '2026-04' for sorting, 'Apr' for displaying)
        df["Month_Sort"] = df["Date"].dt.strftime("%Y-%m")
        df["Month"] = df["Date"].dt.strftime("%b %Y")

        # Count how many times each quest was done per month
        chart_data = (
            df.groupby(["Month_Sort", "Month", "Habit"])
            .size()
            .reset_index(name="Completions")
        )
        chart_data = chart_data.sort_values("Month_Sort")

        # 4. Build a gorgeous, colorful interactive chart using Plotly Express
        fig = px.bar(
            chart_data,
            x="Month",
            y="Completions",
            color="Habit",  # Different color for each habit!
            title="Total Habits Completed per Month",
            text_auto=True,  # Prints the exact number inside the bar
            color_discrete_sequence=px.colors.qualitative.Pastel,  # Kid-friendly colors!
        )

        # Make the chart look modern and clean
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Habits Mastered",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
        )

        # 5. Inject the chart into Streamlit
        st.plotly_chart(fig, use_container_width=True)
