import os
import requests
import json
import yaml
from pathlib import Path

METABASE_URL = os.getenv("MB_SITE_URL", "http://localhost:3000")
USERNAME = os.getenv("MB_ADMIN_USERNAME", "admin@example.com")
PASSWORD = os.getenv("MB_ADMIN_PASSWORD", "admin123")
OUTPUT_DIR = os.getenv("MB_EXPORT_DIR", "../../dashboards/dev")

def get_session_token():
    url = f"{METABASE_URL}/api/session"
    res = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
    res.raise_for_status()
    return res.json()["id"]

def export_dashboards(token):
    headers = {"X-Metabase-Session": token}
    res = requests.get(f"{METABASE_URL}/api/dashboard", headers=headers)
    res.raise_for_status()
    dashboards = res.json()

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    for dash in dashboards:
        dash_id = dash["id"]
        # Obtener detalle del dashboard con sus cards
        detail_res = requests.get(f"{METABASE_URL}/api/dashboard/{dash_id}", headers=headers)
        if detail_res.status_code == 200:
            dash_data = detail_res.json()
            # Limpiar datos dependientes de entorno (ej: IDs de BDD se deberán remapear en el importe)
            filename = f"dashboard_{dash_id}_{dash['name'].replace(' ', '_').lower()}.yaml"
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, 'w') as f:
                yaml.dump(dash_data, f, default_flow_style=False, allow_unicode=True)
            print(f"Exportado: {filename}")

if __name__ == "__main__":
    try:
        print(f"Iniciando exportación desde {METABASE_URL}...")
        token = get_session_token()
        export_dashboards(token)
        print("Exportación finalizada exitosamente.")
    except Exception as e:
        print(f"Error durante exportación: {e}")
