from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
import os

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_FAST_MODEL = os.getenv("AI_FAST_MODEL", "gemini-2.0-flash")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

class InsightData(BaseModel):
    dashboard_id: int
    data_json: str

@router.post("/insights")
def get_insights(data: InsightData):
    if not GEMINI_API_KEY or not client:
         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")

    prompt = f"""
You are an expert data analyst. Read the following JSON output containing data points from a business intelligence chart.
Extract 1 crisp, highly valuable, and very short business insight (max 2 sentences).
Point out any anomaly, up/down trend, or outlier. Do not greet or say "Here is the insight".

Data JSON representation:
{data.data_json}

Insight:
"""
    try:
        response = client.models.generate_content(
            model=AI_FAST_MODEL,
            contents=prompt
        )
        return {"text": response.text.strip(), "confidence": 0.9}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error generating insight via AI.")
