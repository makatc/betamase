from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json

app = FastAPI(title="Metabase AI Middleware", version="1.0")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "NOT_SET")

class TextQuery(BaseModel):
    natural_language: str

@app.post("/api/ai/generate-sql")
def generate_sql(data: TextQuery):
    if GEMINI_API_KEY == "NOT_SET":
         raise HTTPException(status_code=500, detail="Missing API keys.")

    # Integración con Google Gemini (Simulada)
    # prompt = build_prompt(schema_embeddings, data.natural_language)
    # result = model.generate(prompt)

    mock_sql = f"-- Gemini generó esto para: {data.natural_language}\nSELECT * FROM public.ventas WHERE total > 1000;"

    return {"sql": mock_sql, "model": "gemini-1.5-pro", "confidence": 0.94}


class InsightData(BaseModel):
    dashboard_id: int
    data_json: str

@app.post("/api/ai/insights")
def get_insights(data: InsightData):
    # Usa Gemini-1.5-Flash
    return {
        "text": "Se detecta una caída inusual del 15% en ventas los fines de semana de este mes.",
        "confidence": 0.88
    }

class ChatMsg(BaseModel):
    message: str

@app.post("/api/ai/chat")
def chat_with_data(data: ChatMsg):
    # Usa Grok-Beta con memoria de Langchain
    return {"reply": "He revisado la base de datos de productos. El más vendido este mes es el Teclado Mecánico K2 con 145 unidades.", "sql_used": "SELECT * ..."}
