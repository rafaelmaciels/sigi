#!/bin/bash
# ==============================================================================
# 🏛️ SiGI — Script de Atualização para Linux / SSH / PythonAnywhere
# ==============================================================================

set -e

echo "======================================================================"
echo "  🏛️  SIGI — ATUALIZAÇÃO AUTOMATIZADA"
echo "======================================================================"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    PY_EXEC="venv/bin/python"
else
    PY_EXEC="python3"
fi

$PY_EXEC update.py "$@"
