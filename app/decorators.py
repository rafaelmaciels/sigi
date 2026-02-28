# app/decorators.py
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models import User

def permission_required(area, action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 🔹 Verifica se o usuário está autenticado
            if not current_user.is_authenticated:
                flash("Você precisa estar logado para acessar esta página.", "warning")
                return redirect(url_for("auth.login"))

            # ✅ Libera automaticamente se for admin
            if getattr(current_user, "is_admin", False):
                return f(*args, **kwargs)

            # ✅ Libera automaticamente se for o primeiro usuário criado
            primeiro_usuario = User.query.order_by(User.id.asc()).first()
            if primeiro_usuario and current_user.id == primeiro_usuario.id:
                return f(*args, **kwargs)

            # 🔹 Verifica se o usuário tem a permissão
            has_perm = False
            for up in current_user.user_permissions:
                if up.permission.area == area and up.permission.action == action:
                    has_perm = True
                    break

            if not has_perm:
                flash("Você não tem permissão para acessar esta funcionalidade.", "danger")
                return redirect(url_for("dashboard.dashboard"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
