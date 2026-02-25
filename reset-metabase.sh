#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  reset-metabase.sh — Reset Completo de Metabase + Inicio                 ║
# ║  Uso: bash reset-metabase.sh                                              ║
# ╚════════════════════════════════════════════════════════════════════════════╝

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  🔄 Reseteando Metabase completamente...                              ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Navigate to project
echo "📍 Navegando al proyecto..."
cd /home/makatc/PROYECTOS/betamase

# Step 2: Kill any running Metabase process
echo "⏹️  Deteniendo cualquier proceso de Metabase..."
pkill -f "clojure.*dev-start" 2>/dev/null || true
sleep 2

# Step 3: Delete Metabase databases
echo "🗑️  Eliminando bases de datos viejas de Metabase..."
rm -rf ~/.metabase.db 2>/dev/null || true
rm -rf ~/.metabase.db* 2>/dev/null || true
rm -rf ~/.metabase 2>/dev/null || true
rm -rf /tmp/metabase* 2>/dev/null || true

# Step 4: Clean build artifacts
echo "🧹 Limpiando build artifacts..."
rm -rf target/ 2>/dev/null || true
rm -rf .babel_cache/ 2>/dev/null || true

# Step 5: Verify cleanup
echo ""
echo "✅ Cleanup completado"
echo ""

# Step 6: Start Metabase
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Iniciando Metabase con Feature Flags habilitados                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true

echo "⚙️  Exportadas feature flags:"
echo "  • LW_FEATURE_AI_SQL_GENERATION=true"
echo "  • LW_FEATURE_AI_CHAT_WIDGET=true"
echo "  • LW_FEATURE_AI_INSIGHTS=true"
echo ""

echo "🔧 Activando mise..."
eval "$(mise activate bash)"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  📡 METABASE INICIANDO...                                             ║"
echo "║  Abre: http://localhost:3000                                           ║"
echo "║  Email: admin@metabase.com                                            ║"
echo "║  Password: metabase                                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
