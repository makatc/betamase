import os
import requests
import yaml
import glob

METABASE_URL = os.getenv("MB_SITE_URL", "http://localhost:3000")
USERNAME = os.getenv("MB_ADMIN_USERNAME", "admin@example.com")
PASSWORD = os.getenv("MB_ADMIN_PASSWORD", "admin123")
INPUT_DIR = os.getenv("MB_IMPORT_DIR", "../../dashboards/dev")

def get_session_token():
    url = f"{METABASE_URL}/api/session"
    res = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
    res.raise_for_status()
    return res.json()["id"]

def import_dashboards(token):
    headers = {"X-Metabase-Session": token}
    files = glob.glob(os.path.join(INPUT_DIR, "*.yaml"))

    for file in files:
        with open(file, 'r') as f:
            dash_data = yaml.safe_load(f)

        print(f"Importando dashboard: {dash_data.get('name')} desde {file}")

        # En una impl. completa, aquí se debe verificar si el dashboard existe
        # y re-mapear los database_id y table_id que son distintos por entorno.

        payload = {
            "name": dash_data.get("name"),
            "description": dash_data.get("description"),
            "parameters": dash_data.get("parameters", [])
        }

        res = requests.post(f"{METABASE_URL}/api/dashboard", headers=headers, json=payload)
        if res.status_code == 200:
             print("Creado correctamente.")
        else:
             print(f"Error creando: {res.text}")

if __name__ == "__main__":
    token = get_session_token()
    import_dashboards(token)
