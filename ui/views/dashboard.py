import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from client import api_client
from chat.sidebar_chat import render_global_chatbot

st.set_page_config(layout="wide")

# 🚀 INJECT THE GLOBAL CHATBOT RIGHT HERE
render_global_chatbot()

st.title("🏰 Don's Dashboard")

# --- 1. SETUP THE TIME FRAME ---
today = datetime.today()
current_month_str = today.strftime("%Y-%m")  # e.g., '2026-04'
display_month = today.strftime("%B %Y")  # e.g., 'April 2026'

st.subheader(f"📊 Status: {display_month}")

# --- 2. FETCH DATA ---
with st.spinner("Decoding your epic stats..."):
    # Fetch Habits and Tasks
    habits = api_client.fetch_habits(st.session_state.token)
    tasks = api_client.fetch_tasks(st.session_state.token)

    # Filter Tasks for Current Month
    month_tasks = [t for t in tasks if t["due_date"].startswith(current_month_str)]
    completed_tasks = [t for t in month_tasks if t["is_completed"]]
    pending_tasks = [t for t in month_tasks if not t["is_completed"]]

    # Fetch Logs to calculate Habit Mastery for the current month
    month_logs = []
    for habit in habits:
        logs = api_client.fetch_logs(st.session_state.token, habit["id"])
        for log in logs:
            if log["completed_date"].startswith(current_month_str):
                month_logs.append(
                    {"Quest": habit["name"], "Date": log["completed_date"]}
                )

# --- 3. TOP ROW METRICS (GAMIFIED) ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="📜 Active Habits", value=len(habits))
with col2:
    st.metric(label="🎯 Side Quests Beaten (This Month)", value=len(completed_tasks))
with col3:
    st.metric(label="⏳ Quests Pending", value=len(pending_tasks))

st.divider()
# ==========================================
# 6. MASTER DATA TABLES (The Ledger)
# ==========================================
st.markdown("### 🗄️ The Master Ledger")

# Use tabs to separate the tables cleanly
tab_habit_table, tab_task_table = st.tabs(
    ["📜 Daily Tracker Grid", "🎯 Side Quest Log"]
)

with tab_habit_table:
    if not month_logs:
        st.info("No habit data to display yet.")
    else:
        # 1. Convert logs to a DataFrame
        df_logs = pd.DataFrame(month_logs)
        df_logs["Status"] = "✅"  # Add a checkmark for completed items

        # 2. Create a Pivot Table (Matrix)
        # Rows = Quests, Columns = Dates, Values = Checkmarks
        tracker_matrix = df_logs.pivot_table(
            index="Quest", columns="Date", values="Status", aggfunc="first"
        )

        # 3. Fill missing days with a red X and sort columns by date
        tracker_matrix = tracker_matrix.fillna("❌")
        tracker_matrix = tracker_matrix.reindex(sorted(tracker_matrix.columns), axis=1)

        # 4. Display the interactive dataframe
        st.dataframe(tracker_matrix, use_container_width=True)

with tab_task_table:
    if not tasks:
        st.info("No tasks to display yet.")
    else:
        # 1. Convert raw tasks to DataFrame
        df_tasks = pd.DataFrame(tasks)

        # 2. Clean up the data for presentation
        # Filter only the columns we want to show
        df_tasks = df_tasks[["name", "description", "due_date", "is_completed"]]

        # Rename them to kid-friendly, clean headers
        df_tasks.rename(
            columns={
                "name": "Quest",
                "description": "Details",
                "due_date": "Deadline",
                "is_completed": "Status",
            },
            inplace=True,
        )

        # Convert boolean (True/False) to visual status
        df_tasks["Status"] = df_tasks["Status"].apply(
            lambda x: "✅ Done" if x else "⏳ Pending"
        )

        # 3. Display the interactive dataframe
        st.dataframe(
            df_tasks,
            use_container_width=True,
            hide_index=True,  # Hides the arbitrary 0,1,2,3 row numbers
        )
st.divider()

# --- 4. VISUAL CHARTS ROW ---
col_left, col_right = st.columns(2)

# LEFT COLUMN: Habit Mastery Chart
with col_left:
    st.markdown("### 🔥 Habit Mastery")
    if not month_logs:
        st.info("No habits logged this month yet. Time to get to work!")
    else:
        # Crunch the habit data
        df_habits = pd.DataFrame(month_logs)
        habit_counts = df_habits["Quest"].value_counts().reset_index()
        habit_counts.columns = ["Quest", "Times Completed"]

        # Draw a beautiful donut chart
        fig_habits = px.pie(
            habit_counts,
            names="Quest",
            values="Times Completed",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_habits.update_traces(textposition="inside", textinfo="percent+label")
        fig_habits.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_habits, use_container_width=True)

# RIGHT COLUMN: Task Progress Chart
with col_right:
    st.markdown("### ⚔️ Side Quest Progress")
    if not month_tasks:
        st.info("No side quests assigned for this month.")
    else:
        # Create a progress gauge/bar
        task_data = pd.DataFrame(
            {
                "Status": ["Victories", "Pending"],
                "Count": [len(completed_tasks), len(pending_tasks)],
            }
        )

        fig_tasks = px.bar(
            task_data,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map={"Victories": "#00CC96", "Pending": "#EF553B"},
            text_auto=True,
        )
        fig_tasks.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis_title="",
            yaxis_title="Total Quests",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_tasks, use_container_width=True)

# --- 5. URGENT ACTION AREA ---
if pending_tasks:
    st.divider()
    st.markdown("### 🚨 Urgent Missions")

    # Sort pending tasks by due date so the most urgent ones are on top
    pending_tasks.sort(key=lambda x: x["due_date"])

    for task in pending_tasks[:3]:  # Only show the top 3 most urgent!
        st.markdown(f"**{task['name']}** — ⏳ Due: *{task['due_date']}*")
