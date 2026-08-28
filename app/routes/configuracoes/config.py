from flask import Blueprint, render_template
from app.decorators import permission_required

# Blueprint principal de Configurações
config_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")

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
