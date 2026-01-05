#!/bin/bash

# Script para iniciar el backend de CAMPUS360

echo "🚀 Iniciando Backend CAMPUS360..."

# Ir al directorio del backend
cd "$(dirname "$0")"

# Activar entorno virtual
if [ -d ".venv" ]; then
    echo "✅ Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "❌ Error: No se encontró el entorno virtual .venv"
    echo "   Ejecuta: python -m venv .venv"
    exit 1
fi

# Agregar PATH para Prisma
export PATH="$HOME/.local/bin:$PATH"

# Verificar que exista .env
if [ ! -f ".env" ]; then
    echo "⚠️  Advertencia: No se encontró archivo .env"
    echo "   Copia .env.example a .env y configura tus variables"
fi

# Iniciar servidor
echo "🔥 Iniciando servidor en http://localhost:8000"
echo "📚 Documentación en http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
