import os
from dotenv import load_dotenv
from datetime import timedelta

# Carrega variáveis do arquivo .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # -----------------------------
    # 🔒 Segurança
    # -----------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # -----------------------------
    # 🗄️ Banco de Dados
    # -----------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///sigi.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # -----------------------------
    # 📂 Uploads
    # -----------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'app/static/uploads'))
    TEMPLATES_AUTO_RELOAD = True
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 5)) * 1024 * 1024

    # -----------------------------
    # 📧 Configuração de E-mail
    # -----------------------------
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'mail.riseup.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_DEFAULT_NAME', 'SiGI'),
        os.environ.get('MAIL_DEFAULT_EMAIL', 'mail@mail.com')
    )

    # -----------------------------
    # ⏱️ Sessão e Cookies
    # -----------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT', 60)))
    REMEMBER_COOKIE_DURATION = timedelta(days=int(os.environ.get('REMEMBER_DAYS', 7)))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

    # 🔒 Cookies via HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # 🔒 Proteção contra CSRF rigorosa
    WTF_CSRF_SSL_STRICT = True

    # 🔒 SameSite
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # 🔒 Cookies HttpOnly
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
