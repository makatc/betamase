#!/bin/bash
# Re-compila la aplicación Open Source inyectando nuestros cambios de frontend y backend
echo "Construyendo Fork Personalizado de Metabase (v0.48.x) con Branding / AI..."

set -e

# Se recomienda tener Docker con al menos 6GB de RAM asigandos.
docker build -t mi-metabase-personalizado:latest -f Dockerfile.custom .

echo "Build listo. Empieza la instancia local corriendo:"
echo "docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d"
