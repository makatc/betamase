# Mantenimiento del Fork de Metabase

El código original de Metabase avanza todos los días. Para mantener nuestro Fork "Powered by AI & RLS" al día con los parches de seguridad y bugs que lanza Metabase OSS:

1. **Nunca programar en `main`**.
2. **Tu trabajo está en `custom`**.

### Flujo de Sincronización Mensual

```bash
# 1. Ve a la rama espejo.
git checkout main

# 2. Descarga lo último de la empresa Metabase (upstream=github/metabase/metabase).
git fetch upstream
git merge upstream/master

# 3. Empuja main.
git push origin main

# 4. Ve a nuestra rama personalizada.
git checkout custom

# 5. Trae lo de main a custom.
git rebase main

# (Resuelve conflictos aquí si afectamos el mismo archivo que Metabase).
# (Como usamos la carpeta `lw/`, esto rara vez pasará).

# 6. Publica a Github.
git push --force origin custom
```

### Recompilación Personalizada

Con los nuevos parches bajados, vuelve a correr:
`bash build_custom.sh` para generar la nueva imagen de Docker personalizada `mi-metabase-personalizado:latest`.
