from fastapi import FastAPI
from routers import sql_generation, insights, chat

app = FastAPI(
    title="Metabase Pro-OSS AI Middleware",
    version="1.0",
    description="FastAPI service serving as the AI Brain for the Metabase UI. Powers Natural Language SQL, Automated Insights, and Conversational data via Gemini & Grok."
)

app.include_router(sql_generation.router, prefix="/api/ai", tags=["SQL Generation"])
app.include_router(insights.router, prefix="/api/ai", tags=["Automated Insights"])
app.include_router(chat.router, prefix="/api/ai", tags=["Conversational Chatbot"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Subsystem Online"}

# Entry point for running locally:
# uvicorn main:app --host 0.0.0.0 --port 8000
