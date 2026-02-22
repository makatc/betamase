from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
# Langchain can interface with Grok APIs since they mimic OpenAI API format.
# Or we can fallback to Gemini if needed.

router = APIRouter()

GROK_API_KEY = os.getenv("GROK_API_KEY")
AI_CHAT_MODEL = os.getenv("AI_CHAT_MODEL", "grok-beta")

# In-memory dictionary to hold user sessions (For dev. Use Redis for PROD)
user_memory = {}

class ChatMsg(BaseModel):
    message: str
    user_id: str = "default_user"

@router.post("/chat")
def chat_with_data(data: ChatMsg):
    if not GROK_API_KEY:
         raise HTTPException(status_code=500, detail="GROK_API_KEY not configured. To test locally, you can set it as OPENAI API format or use Gemini.")

    # Init Langchain Chat Model connected to xAI Grok Endpoint
    llm = ChatOpenAI(
        openai_api_key=GROK_API_KEY,
        openai_api_base="https://api.x.ai/v1",
        model_name=AI_CHAT_MODEL
    )

    # Init or Retrieve Memory (Keeps last 5 conversational turns)
    if data.user_id not in user_memory:
        user_memory[data.user_id] = ConversationBufferWindowMemory(k=5)

    memory = user_memory[data.user_id]

    # Retrieve previous conversation context
    history = memory.load_memory_variables({})["history"]

    prompt = f"""You are Grok, an advanced and intelligent Data Assistant embedded in Metabase.
    You answer questions directly, logically, with a hint of rebellious wit or direct truth.

    Conversation History:
    {history}

    User: {data.message}
    Grok:"""

    try:
        from langchain.schema import HumanMessage
        response = llm([HumanMessage(content=prompt)])
        reply = response.content.strip()

        # Save interaction
        memory.save_context({"input": data.message}, {"output": reply})

        return {"reply": reply, "sql_used": None}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error communicating with Chat API (Grok).")
