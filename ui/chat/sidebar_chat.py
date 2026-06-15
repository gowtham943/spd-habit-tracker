import streamlit as st
import requests
from config.app_config import settings

BACKEND_CHAT_URL = f"{settings.API_BASE_URL}/chatbot/chat"


def render_global_chatbot():
    """
    Renders a persistent, scrollable AI chatbot inside the Streamlit sidebar.
    Pulls real authenticated credentials from st.session_state.
    """
    # 1. Gatecheck: If the user hasn't successfully logged in yet, do not show the chatbot
    if "token" not in st.session_state or "user" not in st.session_state:
        return

    # Extract clean profile metadata from your session state
    current_token = st.session_state.token
    current_user_data = st.session_state.user
    display_name = current_user_data.get("display_name", "Don")

    with st.sidebar:
        st.header(f"🤖 {display_name}'s Coach")
        st.caption("Ask me to manage your tasks or log habits.")
        st.divider()

        # Initialize a unique message log space for the sidebar
        if "sidebar_chat_messages" not in st.session_state:
            st.session_state.sidebar_chat_messages = []

        # Create a scrollable container for the chat history inside the sidebar
        chat_container = st.container(height=400)

        # Render past history turns inside the scrollable container
        with chat_container:
            for msg in st.session_state.sidebar_chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat Input explicitly targeting the sidebar placement
        if user_input := st.chat_input("Tell me what you achieved..."):
            # Display user input inside the container instantly
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(user_input)

            # Save to global message history so it persists across page switches
            st.session_state.sidebar_chat_messages.append(
                {"role": "user", "content": user_input}
            )

            # 2. Build HTTP request headers passing the real token string
            # In OAuth2PasswordRequestForm layouts, tokens require the "Bearer " prefix
            headers = {
                "Authorization": f"Bearer {current_token}",
                "Content-Type": "application/json",
            }
            payload = {"message": user_input}

            with chat_container:
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    response_placeholder.markdown("*Analyzing database records...*")

                    try:
                        # Pushing the request payload directly to your secure endpoint
                        response = requests.post(
                            BACKEND_CHAT_URL, json=payload, headers=headers
                        )

                        if response.status_code == 200:
                            agent_reply = response.json().get("response")
                            response_placeholder.markdown(agent_reply)
                            st.session_state.sidebar_chat_messages.append(
                                {"role": "assistant", "content": agent_reply}
                            )
                        elif response.status_code == 401:
                            response_placeholder.markdown(
                                "❌ Session expired. Please log in again."
                            )
                        else:
                            error_detail = response.json().get(
                                "detail", "Unknown Error"
                            )
                            response_placeholder.markdown(f"❌ Error: {error_detail}")
                    except Exception as e:
                        response_placeholder.markdown(
                            f"❌ Server unreachable: {str(e)}"
                        )
