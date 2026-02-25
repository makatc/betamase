from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sql_generation, insights, chat, query

app = FastAPI(
    title="Metabase Pro-OSS AI Middleware",
    version="2.0",
    description="FastAPI service serving as the AI Brain for the Metabase UI. Powers Natural Language SQL, Automated Insights, Conversational data, and AI Copilot via Gemini & Grok."
)

# Allow requests from the Metabase frontend (localhost:3000 / 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sql_generation.router, prefix="/api/ai", tags=["SQL Generation"])
app.include_router(insights.router, prefix="/api/ai", tags=["Automated Insights"])
app.include_router(chat.router, prefix="/api/ai", tags=["Conversational Chatbot"])
app.include_router(query.router, prefix="/api/ai", tags=["AI Copilot NL Query"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Subsystem Online"}

# Entry point for running locally:
# uvicorn main:app --host 0.0.0.0 --port 8001 --reload
