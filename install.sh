#!/bin/bash
# ==============================================================================
# 🏛️ SiGI — Script de Instalação para Linux / SSH / PythonAnywhere / cPanel
# ==============================================================================

set -e

echo "======================================================================"
echo "  🏛️  SIGI — INSTALADOR PARA SERVIDORES LINUX E PYTHONANYWHERE"
echo "======================================================================"

# 1. Detectar comando do Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "❌ [ERRO] Python não encontrado no sistema. Por favor, instale o Python 3.10+."
    exit 1
fi

echo "🔍 Detectado interpretador: $($PYTHON_CMD --version)"

# 2. Criar ambiente virtual caso não exista
if [ ! -d "venv" ]; then
    echo "⚙️  Criando ambiente virtual em 'venv/'..."
    $PYTHON_CMD -m venv venv || true
fi

# 3. Ativar venv se existir
if [ -f "venv/bin/activate" ]; then
    echo "🔌 Ativando ambiente virtual venv..."
    source venv/bin/activate
    PY_EXEC="venv/bin/python"
else
    PY_EXEC=$PYTHON_CMD
fi

# 4. Executar instalador principal em Python
echo "🚀 Executando install.py..."
$PY_EXEC install.py "$@"
