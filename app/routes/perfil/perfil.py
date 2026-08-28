from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from .forms import EditarPerfilForm, AlterarSenhaForm
from utils.logs import registrar_log            # ✅ importar o logger
from app.decorators import permission_required  # 👈 importa o decorator

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")

@perfil_bp.route("/", methods=["GET", "POST"])
@login_required
@permission_required("perfil", "view")      # 👈 agora protege visualização de perfil
def meu_perfil():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_password(form.senha_atual.data):
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            registrar_log(current_user.nome, "Alterou a própria senha", "sucesso")
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("perfil.meu_perfil"))
        else:
            registrar_log(current_user.nome, "Tentativa de alterar senha com senha atual incorreta", "erro")
            flash("Senha atual incorreta.", "danger")

    return render_template("perfil/meu_perfil.html", usuario=current_user, form=form)

@perfil_bp.route("/editar", methods=["GET", "POST"])
@login_required
@permission_required("perfil", "edit")
def editar_perfil():
    form = EditarPerfilForm(obj=current_user)
    if request.method == "GET":
        form.ativo.data = "1" if current_user.ativo else "0"
        form.role.data = "admin" if current_user.is_admin else "user"

    if form.validate_on_submit():
        # Validação de e-mail duplicado
        email_novo = form.email.data.strip().lower()
        existente = User.query.filter(User.email == email_novo, User.id != current_user.id).first()
        if existente:
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("perfil/editar_perfil.html", form=form, usuario=current_user)

        current_user.nome = form.nome.data.strip()
        current_user.email = email_novo
        if current_user.is_admin:
            current_user.ativo = (form.ativo.data == "1")
            current_user.is_admin = (form.role.data == "admin")

        db.session.commit()
        registrar_log(current_user.nome, "Editou o próprio perfil", "sucesso")
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil.meu_perfil"))

    return render_template("perfil/editar_perfil.html", form=form, usuario=current_user)

@perfil_bp.route("/senha", methods=["GET", "POST"])
@login_required
@permission_required("perfil", "password")   # 👈 protege alteração de senha
def alterar_senha():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_password(form.senha_atual.data):
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            registrar_log(current_user.nome, "Alterou a senha no perfil do usuário", "sucesso")
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("perfil.meu_perfil"))
        else:
            registrar_log(current_user.nome, "Tentativa de alterar senha no perfil do usuário com senha atual incorreta", "erro")
            flash("Senha atual incorreta.", "danger")
    return render_template("perfil/alterar_senha.html", form=form, usuario=current_user)
