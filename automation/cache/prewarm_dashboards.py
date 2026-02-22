import os
import requests

MB_URL = os.getenv("MB_SITE_URL_PROD", "http://localhost:3000")
DASHBOARDS_TO_PREWARM = [1, 5, 12, 18] # Lista de los dashboards top

def prewarm():
    # El pre-warming puede hacerse haciendo peticiones a la API publica,
    # O peticiones autenticadas para disparar el render del backend.
    for dash_id in DASHBOARDS_TO_PREWARM:
        url = f"{MB_URL}/api/dashboard/{dash_id}/dashcard" # Endpoint fake para ejemplificar el tiro
        print(f"[Prewarm] Solicitando carga para Dasbhaord {dash_id} en {MB_URL}")
        # dummy res = request.get(...)

if __name__ == "__main__":
    print("Iniciando cronjob de calentamiento a Metabase API...")
    prewarm()
