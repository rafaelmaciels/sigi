import os
from datetime import datetime, date
import pytz

def get_system_timezone():
    """
    Retorna o objeto de timezone baseado na variável de ambiente APP_TIMEZONE
    ou fallback padrão para America/Sao_Paulo.
    """
    tz_name = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
    try:
        return pytz.timezone(tz_name)
    except Exception:
        return pytz.timezone("America/Sao_Paulo")

def get_current_datetime() -> datetime:
    """
    Retorna o datetime atual no fuso horário configurado no sistema como naive datetime,
    permitindo comparações diretas e consistentes com campos DateTime do banco de dados.
    """
    tz = get_system_timezone()
    return datetime.now(tz).replace(tzinfo=None)

def get_current_date() -> date:
    """
    Retorna o objeto date atual no fuso horário configurado no sistema.
    """
    return get_current_datetime().date()
