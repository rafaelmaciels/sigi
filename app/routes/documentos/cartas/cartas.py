from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from app import db
from app.models import Carta, Member   # ✅ agora usamos o modelo Carta
from .forms import CartaForm
from app.decorators import permission_required	# 🔹 import do decorator

cartas_bp = Blueprint("cartas", __name__, url_prefix="/cartas")


# ------------------------------------------
# 📋 Listar cartas com paginação 
# ------------------------------------------
@cartas_bp.route("/")
@permission_required("cartas", "view")
def listar_cartas():
    page = request.args.get("page", 1, type=int)
    cartas = (
        Carta.query
        .order_by(Carta.data_emissao.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("documentos/cartas/cartas.html", cartas=cartas)


# --------------------------------------------------------- 
# 🔍 Buscar cartas por título, remetente ou destinatário 
# ---------------------------------------------------------
@cartas_bp.route("/buscar", methods=["GET"])
@permission_required("cartas", "view")
def buscar_cartas():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Carta.query

    if termo:
        query = query.filter(
            (Carta.titulo.ilike(f"%{termo}%")) |
            (Carta.remetente.ilike(f"%{termo}%")) |
            (Carta.destinatario.ilike(f"%{termo}%"))
        )

    cartas = (
        query.order_by(Carta.data_emissao.desc())
        .paginate(page=page, per_page=10)
    )

    # 🔹 Mensagens flash no mesmo padrão das atas
    if termo:
        if cartas.total == 0:
            flash("Nenhuma carta corresponde ao termo pesquisado", "warning")
        elif cartas.total == 1:
            flash("1 carta encontrada", "info")
        else:
            flash(f"{cartas.total} cartas encontradas", "info")

    return render_template("documentos/cartas/cartas.html", cartas=cartas, termo=termo)


# ---------------------------------------
# 👁️ Visualizar detalhes de uma carta 
# ---------------------------------------
@cartas_bp.route("/<int:id>")
@permission_required("cartas", "view")
def visualizar_carta(id):
    carta = Carta.query.get_or_404(id)
    return render_template("documentos/cartas/carta_detalhe.html", carta=carta)
    

# -------------------------------------- 
# ➕ Criar nova carta 
# --------------------------------------
@cartas_bp.route("/nova", methods=["GET", "POST"])
@permission_required("cartas", "create")
def nova_carta():
    form = CartaForm()
    # 🔹 Preenche o select de membros com opção inicial segura
    membros = Member.query.order_by(Member.nome).all()
    form.membro_id.choices = [(0, "Selecione um membro")] + [(m.id, m.nome) for m in membros]

    if form.validate_on_submit():
        carta = Carta(
            titulo=form.titulo.data,
            corpo=form.corpo.data,
            destinatario=form.destinatario.data,
            remetente=form.remetente.data,
            cidade=form.cidade.data,
            situacao=form.situacao.data,   # ✅ salva situação
            membro_id=form.membro_id.data if form.membro_id.data != 0 else None,
            data_emissao=form.data_emissao.data   # ✅ ajustado
        )
        db.session.add(carta)
        db.session.commit()
        flash(f"Carta {carta.titulo} criada com sucesso!", "success")
        return redirect(url_for("documentos.cartas.listar_cartas"))
    return render_template("documentos/cartas/nova_carta.html", form=form)


# ----------------------------------
# ✏️ Editar carta existente 
# ----------------------------------
@cartas_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@permission_required("cartas", "edit")
def editar_carta(id):
    carta = Carta.query.get_or_404(id)
    form = CartaForm(obj=carta)

    # Preenche novamente o select de membros
    membros = Member.query.order_by(Member.nome).all()
    form.membro_id.choices = [(0, "Selecione um membro")] + [(m.id, m.nome) for m in membros]

    if request.method == "GET":
        form.data_emissao.data = carta.data_emissao

    if form.validate_on_submit():
        carta.titulo = form.titulo.data
        carta.corpo = form.corpo.data
        carta.destinatario = form.destinatario.data
        carta.remetente = form.remetente.data
        carta.cidade = form.cidade.data
        carta.situacao = form.situacao.data   # ✅ agora vai atualizar corretamente
        carta.membro_id = form.membro_id.data if form.membro_id.data != 0 else None
        carta.data_emissao = form.data_emissao.data
        db.session.commit()
        flash(f"Carta {carta.titulo} atualizada com sucesso!", "success")
        return redirect(url_for("documentos.cartas.listar_cartas"))

    return render_template("documentos/cartas/editar_carta.html", form=form, carta=carta)


# ---------------------------
# 🗑️ Excluir carta 
# ---------------------------
@cartas_bp.route("/<int:id>/excluir", methods=["POST"])
@permission_required("cartas", "delete")
def excluir_carta(id):
    carta = Carta.query.get_or_404(id)
    db.session.delete(carta)
    db.session.commit()
    flash(f"Carta {carta.titulo} excluída com sucesso!", "danger")
    return redirect(url_for("documentos.cartas.listar_cartas"))
