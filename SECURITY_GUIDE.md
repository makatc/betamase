# 🔒 Guía de Seguridad — API Keys y Credenciales

## ⚠️ NUNCA COMPARTAS

- ❌ API Key de Gemini
- ❌ API Key de Grok
- ❌ Credenciales de Aiven (usuario/contraseña)
- ❌ DATABASE_URL completo
- ❌ Cualquier secreto en conversaciones públicas

---

## ✅ CÓMO MANEJAR CREDENCIALES (SEGURO)

### 1. Variables de Entorno Locales (Terminal)

```bash
# NUNCA escribir en archivos o compartir
export GEMINI_API_KEY="AIza..."
export DATABASE_URL="postgresql://..."
export GROK_API_KEY="xai-..."

# Ejecutar el comando
uvicorn main:app --port 8001 --reload

# Después cerrar terminal (se olvidan automáticamente)
```

### 2. Archivo .env Local (NUNCA en Git)

```bash
# Crear archivo local (solo en tu máquina)
nano ~/.betamase_env

# Contenido:
GEMINI_API_KEY=AIza...
DATABASE_URL=postgresql://...
GROK_API_KEY=xai-...

# Cargar en terminal:
source ~/.betamase_env
```

**Importante**: Asegurate que `.env` está en `.gitignore`:
```bash
# En /home/makatc/PROYECTOS/betamase
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".betamase_env" >> .gitignore
git add .gitignore && git commit -m "Add .gitignore for secrets"
```

### 3. Variables de Entorno en el Sistema

```bash
# Agregar a tu ~/.bashrc o ~/.zshrc (permanente)
export GEMINI_API_KEY="AIza..."
export DATABASE_URL="postgresql://..."

# Recargar terminal
source ~/.bashrc
```

---

## 🔐 Si Accidentalmente Compartiste una Credencial

### INMEDIATAMENTE:

**1. Gemini API Key**
```
1. Ir a https://aistudio.google.com
2. Click "API keys"
3. Eliminar la key comprometida
4. Crear una nueva
5. Usar la nueva key
```

**2. Aiven Credenciales**
```
1. Ir a https://console.aiven.io
2. Tu servicio PostgreSQL
3. Users → Cambiar contraseña
4. Crear nuevo usuario si es necesario
```

**3. Grok API Key (opcional)**
```
1. Ir a https://console.x.ai
2. Eliminar key comprometida
3. Crear nueva
```

---

## 📋 Checklist de Seguridad

- [ ] `.env` está en `.gitignore`
- [ ] Nunca compartir API keys públicamente
- [ ] Variables de entorno solo en terminal local
- [ ] `.git/config` no tiene credenciales
- [ ] `git log` no muestra secrets
- [ ] Las credenciales están rotadas regularmente

---

## 🎯 Cómo Pedir Ayuda SIN Compartir Credenciales

**Si necesitas ayuda conmigo:**

### ❌ NO HACER:
```
Mi DATABASE_URL es: postgresql://avnadmin:pass123@xxx.aivencloud.com:12345/defaultdb
Mi GEMINI_API_KEY es: AIzaXYZ...
```

### ✅ HACER:
```
Necesito ayuda con la conexión a Aiven.
Cuando exporto DATABASE_URL y corro uvicorn, obtengo este error: [MENSAJE DE ERROR]

He verificado que:
- El Service URI es válido (probado con psql)
- Las credenciales son correctas
- Mi IP está en whitelist de Aiven
```

---

## 🚀 Setup Seguro Completo

```bash
# 1. Crear archivo .env local (NUNCA en Git)
cat > ~/.betamase_env << 'EOF'
# ⚠️ NUNCA COMPARTIR ESTE ARCHIVO
GEMINI_API_KEY="tu_key_aqui"
DATABASE_URL="postgresql://user:pass@host:port/db"
GROK_API_KEY="tu_key_opcional"
LW_FEATURE_AI_SQL_GENERATION=true
LW_FEATURE_AI_CHAT_WIDGET=true
LW_FEATURE_AI_INSIGHTS=true
EOF

# 2. Asegurar permisos (solo tu usuario puede leerlo)
chmod 600 ~/.betamase_env

# 3. Cargar en terminal
source ~/.betamase_env

# 4. Verificar que se cargó
echo $GEMINI_API_KEY  # Debería mostrar tu key

# 5. Ejecutar el proyecto
cd /home/makatc/PROYECTOS/betamase/automation/ai/api
uvicorn main:app --port 8001 --reload
```

---

## 🔒 Buenas Prácticas de Seguridad

### 1. Nunca Commitear Secrets
```bash
# ❌ NUNCA hacer esto
git add .env
git commit -m "Add credentials"
git push

# ✅ HACER ESTO
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .gitignore"
```

### 2. Rotar Credenciales Regularmente
```bash
# Cada 3 meses (o si sospecha compromiso)
# Cambiar API keys
# Cambiar contraseña Aiven
# Regenerar tokens
```

### 3. Usar Secretos Diferentes por Entorno
```bash
# Development
GEMINI_API_KEY="dev-key-123"

# Staging
GEMINI_API_KEY="staging-key-456"

# Production
GEMINI_API_KEY="prod-key-789"
```

### 4. Limitar Permisos de APIs
```
Gemini API:
  - Crear key solo para este proyecto
  - Limitar a modelos necesarios (gemini-2.0-flash)

Aiven:
  - Crear usuario específico para Betamase
  - Limitar a tabla necesarias
  - Usar IP whitelist
```

---

## 📞 ¿Necesitas Ayuda?

Puedes compartir:
- ✅ Mensajes de error (sin credenciales)
- ✅ Logs (sin secrets)
- ✅ Código (sin variables con valores)
- ✅ Configuraciones genéricas

No compartas:
- ❌ API keys
- ❌ Contraseñas
- ❌ URLs con credenciales
- ❌ Contenido de .env

---

**Seguridad primero. Credenciales nunca se comparten. ✅**
