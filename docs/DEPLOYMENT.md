# Guía de Despliegue de Entornos

Este proyecto está preparado para 3 entornos. El Docker Compose usa perfiles y environment files.

## Entorno Local (Develop)

```bash
# Variables
cp .env.example .env

# Levantar Metabase y DB
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Entorno Staging

Asume que usas subdominios como `staging.metabase.tudominio.com`.

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml --profile active up -d
```

## Entorno Producción

Requiere configuración de Let's Encrypt o subida de certificados HTTPS a `docker/nginx/ssl/`.

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile active up -d
```

### Migración de Dashboards

El proceso a seguir cuando se crea un dashboard en Dev:

1. En tu máquina: `cd automation/serialization && python export_metabase.py`.
2. Migrar de carpeta en el repo: `python migrate_env.py dev staging`.
3. Commit al repo.
4. En el servidor staging: `python import_metabase.py`.
