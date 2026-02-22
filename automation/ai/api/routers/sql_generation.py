from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from models.schema_embeddings import get_database_schema

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_PRIMARY_MODEL = os.getenv("AI_PRIMARY_MODEL", "gemini-1.5-pro")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class TextQuery(BaseModel):
    natural_language: str

@router.post("/generate-sql")
def generate_sql(data: TextQuery):
    if not GEMINI_API_KEY:
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
        model = genai.GenerativeModel(AI_PRIMARY_MODEL)
        response = model.generate_content(prompt)

        sql_query = response.text.replace("```sql", "").replace("```", "").strip()

        # Basic SQL injection prevention logic (block destructive operations)
        lower_sql = sql_query.lower()
        if any(keyword in lower_sql for keyword in ["drop", "delete", "truncate", "update", "insert", "alter"]):
             raise HTTPException(status_code=400, detail="Destructive SQL queries are not permitted via AI.")

        return {"sql": sql_query, "model": AI_PRIMARY_MODEL, "confidence": 0.95}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to AI Provider to generate SQL.")
