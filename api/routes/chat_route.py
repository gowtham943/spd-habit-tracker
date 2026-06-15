import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from supabase_auth import User

from dependency.auth import get_current_user
from model.chat_request import ChatRequest
from protocol.agent_service import run_chatbot_agent

chat_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@chat_router.post("/chat")
async def chat_with_habit_agent(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Receives chat messages from the Streamlit UI, authorizes the user via JWT,
    and forwards their instruction to the local execution agent loop.
    """
    try:
        # Pass the message along with the securely verified Bouncer ID to the agent loop
        agent_response = await run_chatbot_agent(user_prompt=payload.message, current_user_id=str(current_user.id))
        return {"response": agent_response}
    except* Exception as eg:  # 👈 Notice the asterisk (*) for TaskGroups
        for exc in eg.exceptions:
            logging.error(f"TaskGroup sub-exception failed: {exc}")
            traceback.print_exception(type(exc), exc, exc.__traceback__)
        raise HTTPException(status_code=500, detail="Internal Agent Error")
