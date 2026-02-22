import os
import psycopg2
import pandas as pd
from prophet import Prophet
import requests
from datetime import datetime
import google.generativeai as genai

DB_HOST = os.getenv("POSTGRES_DW_HOST", "metabase-db")
DB_NAME = os.getenv("POSTGRES_DW_NAME", "metabaseappdb")
DB_USER = os.getenv("POSTGRES_DW_USER_ADMIN", "metabase_user")
DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "metabase_password")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_alerts():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    cur.execute("SELECT alert_id, target_table, time_column, value_column, condition_nl, target_webhook_url FROM ai_alerts WHERE is_active = TRUE;")
    alerts = cur.fetchall()
    cur.close()
    conn.close()
    return alerts

def fetch_time_series_data(table, time_col, val_col):
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    # Warning: In production, parameterize names or whitelist them to avoid SQLi
    query = f"""
        SELECT DATE({time_col}) as ds, SUM({val_col}) as y
        FROM {table}
        GROUP BY DATE({time_col})
        ORDER BY ds ASC
        LIMIT 365;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def analyze_anomaly_and_predict(df):
    m = Prophet(daily_seasonality=False, yearly_seasonality=True)
    m.fit(df)

    # Predecir 7 días en el futuro
    future = m.make_future_dataframe(periods=7)
    forecast = m.predict(future)

    # Extraer los últimos 7 días de predicción vs realidad (si existe) y tendencias
    recent_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)
    return recent_forecast

def eval_condition_nlp(condition_nl, forecast_data_str):
    # Usa IA para evaluar si la condición en NLP se cumple según los datos proyectados
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Evalúa estrictamente si la condición del usuario se va a cumplir basándote en la proyección de 7 días.
    Condición NLP: "{condition_nl}"

    Datos proyectados (fecha, predicción):
    {forecast_data_str}

    Responde ÚNICAMENTE "TRIGGER: YES" o "TRIGGER: NO". Sin explicaciones extras.
    """
    resp = model.generate_content(prompt).text.strip()
    return "YES" in resp.upper()

def send_alert(webhook_url, alert_id, condition, forecast_str):
    payload = {
        "text": f"🚨 *Alerta Predictiva de AI (ID {alert_id})* 🚨\nSe prevé que se cumpla la condición: _{condition}_\n\n*Proyección próximos días:*\n```{forecast_str}```"
    }
    try:
        requests.post(webhook_url, json=payload)
        print(f"Sent alert {alert_id} to webhook.")
    except Exception as e:
        print(f"Failed to send webhook for {alert_id}: {e}")

def run_engine():
    alerts = get_alerts()
    print(f"[{datetime.now()}] Procesando {len(alerts)} alertas de inteligencia predictiva...")

    for (alert_id, table, time_col, val_col, condition_nl, webhook) in alerts:
        try:
            df = fetch_time_series_data(table, time_col, val_col)
            if len(df) < 10:
                print(f"Pocos datos para la alerta {alert_id}")
                continue

            forecast_df = analyze_anomaly_and_predict(df)
            forecast_str = forecast_df.to_string(index=False)

            if eval_condition_nlp(condition_nl, forecast_str):
                # Se dispara la condición (ej: "Avisa si cae de 10k")
                send_alert(webhook, alert_id, condition_nl, forecast_str)

        except Exception as e:
            print(f"Error procesando alerta {alert_id}: {e}")

if __name__ == "__main__":
    run_engine()
