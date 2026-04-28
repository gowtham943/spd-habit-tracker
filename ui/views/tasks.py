import streamlit as st
from datetime import date
from client import api_client

st.title("🎯 Task remainder")

# 1. Fetch data
tasks = api_client.fetch_tasks(st.session_state.token)
today = date.today()

# 2. Check for "Due Today" and trigger popups!
due_today_tasks = [
    t for t in tasks if t["due_date"] == today.isoformat() and not t["is_completed"]
]
if due_today_tasks:
    # Triggers a sleek slide-in notification at the bottom right
    st.toast("🚨 You have Task due TODAY! Check your list!", icon="⚠️")

    # Also display a big warning box at the top
    st.warning(
        f"**Attention Hero!** You have {len(due_today_tasks)} Task expiring today!"
    )

# 3. Sidebar to Add New Task
with st.sidebar:
    st.header("📝 New Task")
    with st.form("new_task_form"):
        task_name = st.text_input("Task Name")
        task_desc = st.text_input("Description")
        due_date = st.date_input("Expected Completion Date")
        if st.form_submit_button("Add Task"):
            if api_client.add_task(
                st.session_state.token, task_name, task_desc, due_date
            ):
                st.success("Task Added!")
                st.rerun()

# 4. Display Active Tasks
st.subheader("⚔️ Active Tasks")
active_tasks = [t for t in tasks if not t["is_completed"]]

if not active_tasks:
    st.info("No active Task! You are all caught up.")

for task in active_tasks:
    # Add a red border if it's due today, otherwise normal
    is_due_today = task["due_date"] == today.isoformat()
    border_color = "#FF2B2B" if is_due_today else "#4B4BFF"

    st.markdown(
        f"""
        <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid {border_color}; color: black;">
            <h3 style="margin:0;">{task['name']}</h3>
            <p style="margin:0; color: gray;">{task['description']}</p>
            <p style="margin:0; font-weight: bold; color: {'red' if is_due_today else 'black'};">⏳ Due: {task['due_date']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action Button
    if st.button("🏆 Claim Victory", key=f"complete_{task['id']}"):
        if api_client.complete_task(st.session_state.token, task["id"]):
            st.balloons()
            st.rerun()

# 5. Display Completed Tasks (Hidden in an expander to keep UI clean)
completed_tasks = [t for t in tasks if t["is_completed"]]
if completed_tasks:
    st.divider()
    with st.expander("🏰 Hall of Triumphs (Completed)"):
        for task in completed_tasks:
            st.markdown(f"~~{task['name']} (Due: {task['due_date']})~~ ✅")
