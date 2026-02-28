from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps

# Blueprint principal de Configurações
config_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")

# Decorator para verificar permissões específicas
def permission_required(area, action, fallback="dashboard.dashboard"):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # 🔹 Se não estiver autenticado
            if not current_user.is_authenticated:
                flash("Você precisa estar logado para acessar esta página.", "warning")
                return redirect(url_for("auth.login"))

            # 🔹 libera automaticamente se for admin
            if getattr(current_user, "is_admin", False):
                return f(*args, **kwargs)

            # 🔹 senão, checa permissões vinculadas
            has_perm = any(
                p.permission.area == area and p.permission.action == action
                for p in current_user.user_permissions
            )

            if not has_perm:
                flash("Você não tem permissão para acessar esta funcionalidade.", "danger")

                # 🔹 Se for área de configurações → volta para dashboard (evita loop)
                if area == "config":
                    return redirect(url_for("dashboard.dashboard"))

                # 🔹 Caso contrário → usa fallback (por padrão dashboard)
                return redirect(url_for(fallback))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# importa os submódulos
from .usuarios.usuarios import usuarios_bp
from .backup.backup import backup_bp
from .mail.mail import mail_bp  
from .logs.logs import logs_bp
from .permissoes.permissoes import permissoes_bp
from .igreja.igreja import igreja_bp

# registra os sub-blueprints dentro do config_bp
config_bp.register_blueprint(usuarios_bp)
config_bp.register_blueprint(backup_bp)
config_bp.register_blueprint(mail_bp)  
config_bp.register_blueprint(logs_bp)
config_bp.register_blueprint(permissoes_bp)
config_bp.register_blueprint(igreja_bp)

# rota de configurações
@config_bp.route("/")
@permission_required("config", "view")
def configuracoes():
    return render_template("configuracoes/configuracoes.html")
