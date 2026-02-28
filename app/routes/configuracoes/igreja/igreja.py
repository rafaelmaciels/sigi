from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models import Igreja              # 🔹 modelo que você deve criar em app/models
from .forms import IgrejaForm
from app.decorators import permission_required # 🔹 importa o decorator

igreja_bp = Blueprint("igreja", __name__, url_prefix="/igreja")

# Página principal - visualizar dados da igreja
@igreja_bp.route("/", methods=["GET"])
@login_required
@permission_required("config", "view")
def igreja_page():
    dados = Igreja.query.first()
    # 🔹 Não precisa montar dicionário de permissões, pois usaremos has_permission() no template
    return render_template("configuracoes/igreja.html", dados=dados)


# Editar dados da igreja
@igreja_bp.route("/editar", methods=["GET", "POST"])
@login_required
@permission_required("config", "edit")
def editar_igreja():
    dados = Igreja.query.first()
    form = IgrejaForm(obj=dados)

    if form.validate_on_submit():
        if not dados:
            dados = Igreja()
            db.session.add(dados)

        dados.nome = form.nome.data
        dados.cnpj = form.cnpj.data
        dados.endereco = form.endereco.data
        dados.telefone = form.telefone.data
        dados.email = form.email.data
        dados.site = form.site.data
        dados.pastor_responsavel = form.pastor_responsavel.data
        dados.ano_fundacao = form.ano_fundacao.data
        dados.versiculo_tema = form.versiculo_tema.data

        db.session.commit()
        flash("Dados da igreja atualizados com sucesso!", "success")
        return redirect(url_for("configuracoes.igreja.igreja_page"))

    return render_template("configuracoes/editar_igreja.html", form=form, dados=dados)


# Deletar dados da igreja
@igreja_bp.route("/deletar", methods=["POST", "GET"])
@login_required
@permission_required("config", "delete")
def deletar_igreja():
    dados = Igreja.query.first()
    if dados:
        db.session.delete(dados)
        db.session.commit()
        flash("Dados da igreja foram excluídos com sucesso!", "success")
    else:
        flash("Nenhum dado encontrado para excluir.", "warning")

    return redirect(url_for("configuracoes.igreja.igreja_page"))
