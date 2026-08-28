import os
import sys

# -----------------------------------------------------------------------------
# 🌐 SiGI — Ponto de Entrada WSGI (Produção / PythonAnywhere / cPanel Passenger)
# -----------------------------------------------------------------------------

# Determina dinamicamente a pasta raiz do projeto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Insere a pasta do projeto no sys.path para importação dos módulos internos
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Carrega variáveis do arquivo .env
from dotenv import load_dotenv
env_path = os.path.join(PROJECT_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

from app import create_app
from config import get_config

# Cria e exporta a instância do aplicativo WSGI para o servidor web
application = create_app(get_config())

if __name__ == "__main__":
    application.run()
