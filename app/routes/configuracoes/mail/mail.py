from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user
from dotenv import set_key, dotenv_values
import os
from .forms import MailConfigForm
from utils.logs import registrar_log
from app.decorators import permission_required   # usa o decorator global

# 🔹 Função utilitária para converter string em boolean
def str_to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")

# Caminho do .env
dotenv_path = os.environ.get("DOTENV_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

mail_bp = Blueprint("mail", __name__, url_prefix="/mail")

# 🔹 Rota só para visualizar (GET) → exige permissão de leitura
@mail_bp.route("/", methods=["GET"])
@permission_required("config", "view")
def configurar_mail_view():
    env_values = dotenv_values(dotenv_path)
    form = MailConfigForm()

    # Preenche os campos com valores atuais
    form.mail_server.data = env_values.get("MAIL_SERVER", "")
    form.mail_port.data = env_values.get("MAIL_PORT", "")
    form.mail_use_tls.data = str_to_bool(env_values.get("MAIL_USE_TLS", False))
    form.mail_use_ssl.data = str_to_bool(env_values.get("MAIL_USE_SSL", False))
    form.mail_username.data = env_values.get("MAIL_USERNAME", "")
    form.mail_password.data = env_values.get("MAIL_PASSWORD", "")
    form.mail_default_name.data = env_values.get("MAIL_DEFAULT_NAME", "")
    form.mail_default_email.data = env_values.get("MAIL_DEFAULT_EMAIL", "")

    return render_template("configuracoes/config_mail.html", form=form)

# 🔹 Rota só para salvar (POST) → exige permissão de edição
@mail_bp.route("/", methods=["POST"])
@permission_required("config", "edit")
def configurar_mail_edit():
    form = MailConfigForm()

    if form.validate_on_submit():
        set_key(dotenv_path, "MAIL_SERVER", form.mail_server.data)
        set_key(dotenv_path, "MAIL_PORT", str(form.mail_port.data))
        set_key(dotenv_path, "MAIL_USE_TLS", str(form.mail_use_tls.data))
        set_key(dotenv_path, "MAIL_USE_SSL", str(form.mail_use_ssl.data))
        set_key(dotenv_path, "MAIL_USERNAME", form.mail_username.data)
        set_key(dotenv_path, "MAIL_PASSWORD", form.mail_password.data)
        set_key(dotenv_path, "MAIL_DEFAULT_NAME", form.mail_default_name.data)
        set_key(dotenv_path, "MAIL_DEFAULT_EMAIL", form.mail_default_email.data)

        registrar_log(current_user.nome, "Atualizou configurações de e-mail", "sucesso")
        flash("Configurações de e-mail salvas com sucesso!", "success")

    return redirect(url_for("configuracoes.mail.configurar_mail_view"))
