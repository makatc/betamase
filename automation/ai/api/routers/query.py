"""
Natural Language Query router — resolves NL questions against existing
Metabase content (dashboards/questions) first, then falls back to SQL generation.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
import os
from models.schema_embeddings import get_database_schema

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_PRIMARY_MODEL = os.getenv("AI_PRIMARY_MODEL", "gemini-2.0-flash")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


class NLQuery(BaseModel):
    question: str
    user_id: str = "default_user"
    context: str = ""  # Optional: current page context (dashboard name, etc.)


class NLQueryResponse(BaseModel):
    answer: str
    sql: str | None = None
    model: str
    source: str  # "sql_generated" | "existing_content" | "direct_answer"
    confidence: float


@router.post("/query", response_model=NLQueryResponse)
def natural_language_query(data: NLQuery):
    """
    Main AI Copilot query endpoint.
    1. Checks if question can be answered from schema context.
    2. Generates SQL when data is needed.
    3. Returns answer + optional SQL for user review.
    """
    if not GEMINI_API_KEY or not client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured.",
        )

    schema_context = get_database_schema()
    context_hint = f"\nPage context: {data.context}" if data.context else ""

    prompt = f"""You are an intelligent Data Assistant embedded in a business analytics platform (Metabase).
A user asked: "{data.question}"{context_hint}

Available database schema:
{schema_context}

Instructions:
1. Determine if this question requires querying a database or can be answered directly.
2. If it requires data: generate a safe SELECT-only SQL query.
3. Provide a concise, helpful answer in Spanish (the app language).
4. If generating SQL, include it in the sql_query field.

Respond in this JSON format:
{{
  "answer": "<concise answer in Spanish>",
  "sql_query": "<SELECT SQL or null if not needed>",
  "source": "<'sql_generated' | 'direct_answer'>",
  "confidence": <0.0 to 1.0>
}}

Return ONLY the JSON, no markdown, no extra text."""

    try:
        response = client.models.generate_content(
            model=AI_PRIMARY_MODEL,
            contents=prompt,
        )
        import json

        raw = response.text.strip()
        # Strip markdown code blocks if model wraps in them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        parsed = json.loads(raw)

        sql = parsed.get("sql_query")
        # Safety: block destructive SQL even if model generates it
        if sql:
            lower_sql = sql.lower()
            if any(
                kw in lower_sql
                for kw in ["drop", "delete", "truncate", "update", "insert", "alter"]
            ):
                sql = None  # Strip unsafe SQL silently

        return NLQueryResponse(
            answer=parsed.get("answer", "No pude generar una respuesta."),
            sql=sql,
            model=AI_PRIMARY_MODEL,
            source=parsed.get("source", "sql_generated"),
            confidence=float(parsed.get("confidence", 0.8)),
        )

    except Exception as e:
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit en Gemini Free Tier. Espera ~60s y reintenta.",
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la consulta: {error_str[:300]}",
        )
