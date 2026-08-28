from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def permission_required(area: str, action: str, fallback: str = "dashboard.dashboard"):
    """
    Decorator enterprise-grade para controle de acesso baseado em permissões (RBAC).
    - Valida autenticação
    - Concede bypass total para administradores (is_admin=True)
    - Checa permissões mapeadas de forma segura e eficiente
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Você precisa estar logado para acessar esta página.", "warning")
                return redirect(url_for("auth.login"))

            if getattr(current_user, "is_admin", False):
                return f(*args, **kwargs)

            if hasattr(current_user, "has_permission") and current_user.has_permission(area, action):
                return f(*args, **kwargs)

            flash("Você não tem permissão para acessar esta funcionalidade.", "danger")
            if area == "config":
                return redirect(url_for("dashboard.dashboard"))
            return redirect(url_for(fallback))
        return decorated_function
    return decorator
