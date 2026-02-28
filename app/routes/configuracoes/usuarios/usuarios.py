from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage   # ✅ valida uploads
from app.extensions import db
from app.models import User
from .forms import NovoUsuarioForm, EditarUsuarioForm
from utils.logs import registrar_log
from app.decorators import permission_required   # 👈 importa o decorator global
import os
from sqlalchemy.exc import IntegrityError

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

# Pasta de upload dentro de app/static/uploads
def get_upload_folder():
    return os.path.join(current_app.root_path, "static", "uploads")

@usuarios_bp.route("/")
@permission_required("usuarios", "view")   # 👈 exige permissão de leitura
def usuarios_page():
    page = request.args.get("page", 1, type=int)
    usuarios = User.query.order_by(User.nome).paginate(page=page, per_page=5)
    return render_template("configuracoes/usuarios.html", usuarios=usuarios)

@usuarios_bp.route("/novo", methods=["GET", "POST"])
@permission_required("usuarios", "create")   # 👈 exige permissão de criação
def novo_usuario():
    form = NovoUsuarioForm()
    if form.validate_on_submit():
        existente = User.query.filter_by(email=form.email.data).first()
        if existente:
            flash("Já existe um usuário com este e-mail.", "danger")
            return redirect(url_for("configuracoes.usuarios.novo_usuario"))

        usuario = User(
            nome=form.nome.data,
            email=form.email.data,
            ativo=(form.ativo.data == "true"),
            is_admin=(form.is_admin.data == "true")
        )
        usuario.set_password(form.senha.data)

        try:
            db.session.add(usuario)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Erro ao criar usuário. E-mail duplicado ou inválido.", "danger")
            return redirect(url_for("configuracoes.usuarios.novo_usuario"))

        if form.foto.data and isinstance(form.foto.data, FileStorage):
            foto = form.foto.data
            ext = os.path.splitext(foto.filename)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                flash("Formato inválido. Use JPG ou PNG.", "danger")
                return redirect(url_for("configuracoes.usuarios.novo_usuario"))
            else:
                filename = secure_filename(f"user_{usuario.id}{ext}")
                upload_folder = get_upload_folder()
                os.makedirs(upload_folder, exist_ok=True)
                path = os.path.join(upload_folder, filename)
                foto.save(path)
                usuario.foto = filename
                db.session.commit()

        registrar_log(current_user.nome, f"Criou usuário: {usuario.email}", "sucesso")
        flash(f"Usuário {usuario.nome} criado com sucesso!", "success")
        return redirect(url_for("configuracoes.usuarios.usuarios_page"))
    return render_template("configuracoes/novo_usuario.html", form=form)

@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@permission_required("usuarios", "edit")   # 👈 exige permissão de edição
def editar_usuario(id):
    usuario = User.query.get_or_404(id)
    form = EditarUsuarioForm(obj=usuario)
    if request.method == "GET":
        form.ativo.data = "true" if usuario.ativo else "false"
        form.is_admin.data = "true" if usuario.is_admin else "false"

    if form.validate_on_submit():
        existente = User.query.filter(User.email == form.email.data, User.id != usuario.id).first()
        if existente:
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return redirect(url_for("configuracoes.usuarios.editar_usuario", id=id))

        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.ativo = (form.ativo.data == "true")
        usuario.is_admin = (form.is_admin.data == "true")
        if form.senha.data:
            usuario.set_password(form.senha.data)

        if form.foto.data and isinstance(form.foto.data, FileStorage):
            foto = form.foto.data
            ext = os.path.splitext(foto.filename)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                flash("Formato inválido. Use JPG ou PNG.", "danger")
                return redirect(url_for("configuracoes.usuarios.editar_usuario", id=id))
            else:
                upload_folder = get_upload_folder()
                os.makedirs(upload_folder, exist_ok=True)

                if usuario.foto:
                    old_path = os.path.join(upload_folder, usuario.foto)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(f"user_{usuario.id}{ext}")
                path = os.path.join(upload_folder, filename)
                foto.save(path)
                usuario.foto = filename

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Erro ao atualizar usuário. E-mail duplicado ou inválido.", "danger")
            return redirect(url_for("configuracoes.usuarios.editar_usuario", id=id))

        registrar_log(current_user.nome, f"Editou usuário: {usuario.email}", "sucesso")
        flash(f"Usuário {usuario.nome} atualizado com sucesso!", "success")
        return redirect(url_for("configuracoes.usuarios.usuarios_page"))
    return render_template("configuracoes/editar_usuario.html", form=form, usuario=usuario)

@usuarios_bp.route("/<int:id>/excluir", methods=["POST"])
@permission_required("usuarios", "delete")   # 👈 exige permissão de exclusão
def excluir_usuario(id):
    usuario = User.query.get_or_404(id)

    if usuario.foto:
        upload_folder = get_upload_folder()
        path = os.path.join(upload_folder, usuario.foto)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(usuario)
    db.session.commit()

    registrar_log(current_user.nome, f"Excluiu usuário: {usuario.email}", "sucesso")
    flash(f"Usuário {usuario.nome} excluído com sucesso!", "danger")
    return redirect(url_for("configuracoes.usuarios.usuarios_page"))

@usuarios_bp.route("/<int:id>/toggle", methods=["POST"])
@permission_required("usuarios", "edit")   # 👈 exige permissão de edição
def toggle_usuario(id):
    usuario = User.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    registrar_log(current_user.nome, f"Trocou status do usuário: {usuario.email} para {'ativo' if usuario.ativo else 'inativo'}", "sucesso")
    flash(
        f"Usuário {usuario.nome} foi {'ativado' if usuario.ativo else 'desativado'}.",
        "success" if usuario.ativo else "warning"
    )
    return redirect(url_for("configuracoes.usuarios.usuarios_page"))

@usuarios_bp.route("/<int:id>/remover_foto", methods=["POST"])
@permission_required("usuarios", "edit")   # 👈 exige permissão de edição
def remover_foto(id):
    usuario = User.query.get_or_404(id)

    if usuario.foto:
        upload_folder = get_upload_folder()
        path = os.path.join(upload_folder, usuario.foto)

        if os.path.exists(path):
            os.remove(path)

        usuario.foto = None
        db.session.commit()

        registrar_log(current_user.nome, f"Removeu foto do usuário: {usuario.email}", "sucesso")
        flash("Foto removida com sucesso!", "info")
    else:
        flash("Este usuário não possui foto cadastrada.", "warning")

    return redirect(url_for("configuracoes.usuarios.editar_usuario", id=id))
