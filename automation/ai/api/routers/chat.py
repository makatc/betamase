from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from google import genai as google_genai

router = APIRouter()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_CHAT_MODEL = os.getenv("AI_CHAT_MODEL", "grok-beta")
AI_FAST_MODEL = os.getenv("AI_FAST_MODEL", "gemini-2.0-flash")

# In-memory dict to hold conversation history per user (For dev. Use Redis for PROD)
user_history: dict[str, InMemoryChatMessageHistory] = {}

class ChatMsg(BaseModel):
    message: str
    user_id: str = "default_user"

SYSTEM_PROMPT = "You are an intelligent Data Assistant embedded in Metabase. Answer questions about data directly, logically, and concisely."

@router.post("/chat")
def chat_with_data(data: ChatMsg):
    # --- Fallback strategy: try Grok first, then Gemini ---
    if not GROK_API_KEY and not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="No AI keys configured. Set GROK_API_KEY or GEMINI_API_KEY.")

    # Init or retrieve conversation history
    if data.user_id not in user_history:
        user_history[data.user_id] = InMemoryChatMessageHistory()
    history = user_history[data.user_id]

    # --- Grok path (primary) ---
    if GROK_API_KEY:
        try:
            llm = ChatOpenAI(
                api_key=GROK_API_KEY,
                base_url="https://api.x.ai/v1",
                model=AI_CHAT_MODEL
            )
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + history.messages + [HumanMessage(content=data.message)]
            if len(messages) > 11:
                messages = [messages[0]] + messages[-10:]
            response = llm.invoke(messages)
            reply = response.content.strip()
            history.add_user_message(data.message)
            history.add_ai_message(reply)
            return {"reply": reply, "provider": "grok", "sql_used": None}
        except Exception as e:
            print(f"Grok failed, trying Gemini fallback: {e}")

    # --- Gemini fallback (when Grok unavailable or fails) ---
    if GEMINI_API_KEY:
        try:
            client = google_genai.Client(api_key=GEMINI_API_KEY)

            # Build a simple conversation string for Gemini (no native history support in basic API)
            history_text = ""
            for msg in history.messages[-6:]:  # last 3 turns
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                history_text += f"{role}: {msg.content}\n"

            prompt = f"{SYSTEM_PROMPT}\n\n{history_text}User: {data.message}\nAssistant:"
            response = client.models.generate_content(model=AI_FAST_MODEL, contents=prompt)
            reply = response.text.strip()
            history.add_user_message(data.message)
            history.add_ai_message(reply)
            return {"reply": reply, "provider": "gemini-fallback", "sql_used": None}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini fallback error: {str(e)[:200]}")

    raise HTTPException(status_code=500, detail="No AI provider available.")
