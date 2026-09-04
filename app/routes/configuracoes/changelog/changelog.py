from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from sqlalchemy import or_, extract
from app.extensions import db
from app.models import User, Changelog
from app.models.changelog import TIPOS_CHANGELOG, MODULOS_CHANGELOG
from app.models.log import registrar_log
from app.decorators import permission_required
from .forms import ChangelogForm
from collections import defaultdict
from datetime import datetime

changelog_bp = Blueprint("changelog", __name__, url_prefix="/changelog")

MESES_PT_BR = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def usuario_pode_gerenciar() -> bool:
    if not current_user.is_authenticated:
        return False
    if getattr(current_user, "is_admin", False):
        return True
    if hasattr(current_user, "has_permission") and (
        current_user.has_permission("config", "edit") or current_user.has_permission("config", "create")
    ):
        return True
    return False

def usuario_pode_excluir() -> bool:
    if not current_user.is_authenticated:
        return False
    if getattr(current_user, "is_admin", False):
        return True
    if hasattr(current_user, "has_permission") and (
        current_user.has_permission("config", "delete") or current_user.has_permission("config", "edit")
    ):
        return True
    return False

@changelog_bp.route("/", methods=["GET"])
@permission_required("config", "view")
def listar_changelog():
    termo_busca = request.args.get("q", "", type=str).strip()
    modulo_filtro = request.args.get("modulo", "", type=str).strip()
    tipo_filtro = request.args.get("tipo", "", type=str).strip()
    ano_filtro = request.args.get("ano", "", type=str).strip()

    query = Changelog.query

    if termo_busca:
        filtro_termo = or_(
            Changelog.titulo.ilike(f"%{termo_busca}%"),
            Changelog.descricao.ilike(f"%{termo_busca}%"),
            Changelog.finalidade.ilike(f"%{termo_busca}%"),
            Changelog.autor_nome.ilike(f"%{termo_busca}%"),
            Changelog.versao.ilike(f"%{termo_busca}%")
        )
        query = query.filter(filtro_termo)

    if modulo_filtro and modulo_filtro in MODULOS_CHANGELOG:
        query = query.filter(Changelog.modulo == modulo_filtro)

    if tipo_filtro and tipo_filtro in TIPOS_CHANGELOG:
        query = query.filter(Changelog.tipo == tipo_filtro)

    if ano_filtro and ano_filtro.isdigit():
        query = query.filter(extract('year', Changelog.data_implantacao) == int(ano_filtro))

    page = request.args.get("page", 1, type=int)

    paginacao = query.order_by(
        Changelog.data_implantacao.desc(),
        Changelog.id.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    registros = paginacao.items

    # Estruturação hierárquica da página atual: Ano → Mês → Data → Lista de Itens
    anos_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for item in registros:
        dt = item.data_implantacao
        ano = dt.year
        mes = dt.month
        data_str = dt.strftime("%d/%m/%Y")
        anos_dict[ano][mes][data_str].append(item)

    # Conversão ordenada para listas limpas no template
    grupos_anos = []
    for ano in sorted(anos_dict.keys(), reverse=True):
        meses_lista = []
        for mes in sorted(anos_dict[ano].keys(), reverse=True):
            datas_lista = []
            for data_str in sorted(anos_dict[ano][mes].keys(), key=lambda d: datetime.strptime(d, "%d/%m/%Y"), reverse=True):
                datas_lista.append({
                    "data_formatada": data_str,
                    "itens": anos_dict[ano][mes][data_str]
                })
            meses_lista.append({
                "mes_numero": mes,
                "mes_nome": MESES_PT_BR.get(mes, f"Mês {mes}"),
                "datas": datas_lista
            })
        grupos_anos.append({
            "ano": ano,
            "meses": meses_lista
        })

    # Anos disponíveis para o filtro rápido
    anos_disponiveis = [
        int(r[0]) for r in db.session.query(extract('year', Changelog.data_implantacao).distinct())
        .order_by(extract('year', Changelog.data_implantacao).desc())
        .all() if r[0] is not None
    ]

    return render_template(
        "configuracoes/changelog/listar.html",
        grupos_anos=grupos_anos,
        paginacao=paginacao,
        total_registros=paginacao.total,
        termo_busca=termo_busca,
        termo=termo_busca,
        modulo_filtro=modulo_filtro,
        tipo_filtro=tipo_filtro,
        ano_filtro=ano_filtro,
        anos_disponiveis=anos_disponiveis,
        modulos_disponiveis=MODULOS_CHANGELOG,
        tipos_disponiveis=TIPOS_CHANGELOG,
        pode_gerenciar=usuario_pode_gerenciar(),
        pode_excluir=usuario_pode_excluir()
    )


@changelog_bp.route("/novo", methods=["GET", "POST"])
@permission_required("config", "view")
def criar_changelog():
    if not usuario_pode_gerenciar():
        flash("Você não possui permissão para cadastrar alterações no Changelog.", "danger")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    form = ChangelogForm()

    # Preenche opções de usuários do sistema
    usuarios = User.query.filter_by(ativo=True).order_by(User.nome.asc()).all()
    form.usuario_id.choices = [(0, "— Nenhum / Autor Manual / Histórico —")] + [
        (u.id, f"{u.display_name} ({u.email})") for u in usuarios
    ]

    if request.method == "GET":
        # Preenche automaticamente com o usuário autenticado
        form.usuario_id.data = current_user.id
        form.autor_nome.data = current_user.display_name

    if form.validate_on_submit():
        user_id = form.usuario_id.data if form.usuario_id.data != 0 else None
        autor_nome = form.autor_nome.data.strip() if form.autor_nome.data else None

        # Se não especificou autor_nome manual mas vinculou usuário, usa o nome do usuário
        if user_id and not autor_nome:
            u = db.session.get(User, user_id)
            if u:
                autor_nome = u.display_name

        novo = Changelog(
            titulo=form.titulo.data.strip(),
            modulo=form.modulo.data,
            tipo=form.tipo.data,
            versao=form.versao.data.strip() if form.versao.data else None,
            descricao=form.descricao.data.strip(),
            finalidade=form.finalidade.data.strip(),
            data_implantacao=form.data_implantacao.data,
            usuario_id=user_id,
            autor_nome=autor_nome
        )

        db.session.add(novo)
        db.session.commit()

        registrar_log(
            current_user.display_name,
            f"Adicionou registro ao Changelog: '{novo.titulo}' ({novo.modulo})",
            "sucesso"
        )
        flash(f"Atualização '{novo.titulo}' cadastrada com sucesso!", "success")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    return render_template(
        "configuracoes/changelog/form.html",
        form=form,
        is_edicao=False,
        titulo_pagina="Adicionar Atualização ao Changelog"
    )


@changelog_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@permission_required("config", "view")
def editar_changelog(id):
    if not usuario_pode_gerenciar():
        flash("Você não possui permissão para editar alterações no Changelog.", "danger")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    item = db.session.get(Changelog, id)
    if not item:
        flash("Registro do Changelog não encontrado.", "warning")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    form = ChangelogForm(obj=item)

    usuarios = User.query.filter_by(ativo=True).order_by(User.nome.asc()).all()
    form.usuario_id.choices = [(0, "— Nenhum / Autor Manual / Histórico —")] + [
        (u.id, f"{u.display_name} ({u.email})") for u in usuarios
    ]

    if request.method == "GET":
        form.usuario_id.data = item.usuario_id or 0

    if form.validate_on_submit():
        user_id = form.usuario_id.data if form.usuario_id.data != 0 else None
        autor_nome = form.autor_nome.data.strip() if form.autor_nome.data else None

        if user_id and not autor_nome:
            u = db.session.get(User, user_id)
            if u:
                autor_nome = u.display_name

        item.titulo = form.titulo.data.strip()
        item.modulo = form.modulo.data
        item.tipo = form.tipo.data
        item.versao = form.versao.data.strip() if form.versao.data else None
        item.descricao = form.descricao.data.strip()
        item.finalidade = form.finalidade.data.strip()
        item.data_implantacao = form.data_implantacao.data
        item.usuario_id = user_id
        item.autor_nome = autor_nome

        db.session.commit()

        registrar_log(
            current_user.display_name,
            f"Editou registro do Changelog: '{item.titulo}' (ID: {item.id})",
            "sucesso"
        )
        flash(f"Atualização '{item.titulo}' atualizada com sucesso!", "success")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    return render_template(
        "configuracoes/changelog/form.html",
        form=form,
        item=item,
        is_edicao=True,
        titulo_pagina=f"Editar Atualização: {item.titulo}"
    )


@changelog_bp.route("/<int:id>/excluir", methods=["POST"])
@permission_required("config", "view")
def excluir_changelog(id):
    if not usuario_pode_excluir():
        flash("Você não possui permissão para excluir alterações no Changelog.", "danger")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    item = db.session.get(Changelog, id)
    if not item:
        flash("Registro não encontrado para exclusão.", "warning")
        return redirect(url_for("configuracoes.changelog.listar_changelog"))

    titulo = item.titulo
    db.session.delete(item)
    db.session.commit()

    registrar_log(
        current_user.display_name,
        f"Excluiu registro do Changelog: '{titulo}' (ID: {id})",
        "sucesso"
    )
    flash(f"Registro '{titulo}' removido com sucesso!", "info")
    return redirect(url_for("configuracoes.changelog.listar_changelog"))
