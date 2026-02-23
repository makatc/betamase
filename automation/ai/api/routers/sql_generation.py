from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from models.schema_embeddings import get_database_schema

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_PRIMARY_MODEL = os.getenv("AI_PRIMARY_MODEL", "gemini-2.0-flash")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

class TextQuery(BaseModel):
    natural_language: str

@router.post("/generate-sql")
def generate_sql(data: TextQuery):
    if not GEMINI_API_KEY or not client:
         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")

    schema_context = get_database_schema()

    prompt = f"""
You are an expert PostgreSQL database architect in charge of translating Natural Language to raw SQL queries.
Return ONLY the raw SQL query, without any markdown formatting like ```sql, without explanations.

Context:
{schema_context}

User question: {data.natural_language}
SQL:
"""
    try:
        response = client.models.generate_content(
            model=AI_PRIMARY_MODEL,
            contents=prompt
        )
        sql_query = response.text.replace("```sql", "").replace("```", "").strip()

        # Basic SQL injection prevention logic (block destructive operations)
        lower_sql = sql_query.lower()
        if any(keyword in lower_sql for keyword in ["drop", "delete", "truncate", "update", "insert", "alter"]):
             raise HTTPException(status_code=400, detail="Destructive SQL queries are not permitted via AI.")

        return {"sql": sql_query, "model": AI_PRIMARY_MODEL, "confidence": 0.95}

    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        print(f"Gemini error: {error_str}")
        # Expose rate limit errors clearly
        if "RESOURCE_EXHAUSTED" in error_str or "FreeTier" in error_str or "quota" in error_str.lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit reached on Gemini Free Tier. Wait ~60s and try again, or enable billing at console.cloud.google.com."
            )
        raise HTTPException(status_code=500, detail=f"Gemini error: {error_str[:300]}")
