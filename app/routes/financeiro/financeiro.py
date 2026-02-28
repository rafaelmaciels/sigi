from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, current_app
from datetime import datetime, date
from collections import defaultdict
import csv, io, os
from werkzeug.utils import secure_filename
import uuid
from sqlalchemy import or_

from app.extensions import db
from app.models import Financeiro
from app.routes.financeiro.forms import (
    EntradaForm, SaidaForm, FiltroRelatorioForm, ComprovanteForm
)
from flask_login import login_required, current_user
from utils.logs import registrar_log
from app.decorators import permission_required

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")

# ➡️ Filtro Jinja para moeda
@financeiro_bp.app_template_filter('currency')
def currency_format(value):
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# -----------------------------
# 📄 Dashboard Financeiro
# -----------------------------
@financeiro_bp.route('/')
@login_required
@permission_required("financeiro", "view")
def financeiro():
    total_entradas = db.session.query(db.func.coalesce(db.func.sum(Financeiro.valor), 0.0)).filter(Financeiro.tipo=="Entrada").scalar()
    total_saidas = db.session.query(db.func.coalesce(db.func.sum(Financeiro.valor), 0.0)).filter(Financeiro.tipo=="Saída").scalar()
    saldo = (total_entradas or 0.0) - (total_saidas or 0.0)

    def month_key(d: date):
        return d.strftime("%m-%Y")

    ultimos = sorted({month_key(r.data) for r in Financeiro.query.all()}, key=lambda x: datetime.strptime("01-"+x, "%d-%m-%Y"))[-6:]
    por_mes = {m: {"Entradas": 0.0, "Saídas": 0.0} for m in ultimos}
    for r in Financeiro.query.all():
        mk = month_key(r.data)
        if mk in por_mes:
            if r.tipo == "Entrada":
                por_mes[mk]["Entradas"] += float(r.valor)
            elif r.tipo == "Saída":
                por_mes[mk]["Saídas"] += float(r.valor)

    labels = ultimos
    entradas_data = [por_mes[m]["Entradas"] for m in labels]
    saidas_data = [por_mes[m]["Saídas"] for m in labels]

    return render_template(
        'financeiro/financeiro.html',
        total_entradas=total_entradas or 0.0,
        total_saidas=total_saidas or 0.0,
        saldo=saldo or 0.0,
        labels=labels,
        entradas_data=entradas_data,
        saidas_data=saidas_data
    )

# -----------------------------
# 📄 Entradas
# -----------------------------
@financeiro_bp.route('/entradas', methods=['GET', 'POST'])
@login_required
@permission_required("financeiro", "view")
def entradas():
    form = EntradaForm()

    # 🔹 Criação de nova entrada
    if form.validate_on_submit():
        if not current_user.has_permission("financeiro", "create"):
            flash("Você não tem permissão para criar entradas.", "danger")
            registrar_log(current_user.nome, "Tentou criar entrada sem permissão", "falha")
            return redirect(url_for("financeiro.entradas"))

        raw_valor = request.form.get('valor', '')
        valor_float = float(str(raw_valor).replace(',', '.'))

        # 🔹 Upload do comprovante com hash e pasta organizada em static/uploads/financeiro
        comprovante_file = request.files.get("comprovante")
        comprovante_path = None
        if comprovante_file and comprovante_file.filename:
            ext = os.path.splitext(comprovante_file.filename)[1].lower()
            filename = f"{uuid.uuid4().hex}{ext}"
            upload_dir = os.path.join(current_app.root_path, "static", "uploads", "financeiro")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            comprovante_file.save(filepath)
            comprovante_path = f"/static/uploads/financeiro/{filename}"

        nova = Financeiro(
            tipo="Entrada",
            categoria=form.tipo_receita.data,
            valor=valor_float,
            data=form.data.data,
            descricao=form.descricao.data,
            conta=form.conta.data,
            usuario=current_user.nome,
            comprovante=comprovante_path
        )
        db.session.add(nova)
        db.session.commit()
        registrar_log(current_user.nome, f"Registrou entrada: {nova.descricao}", "sucesso")
        flash("Entrada registrada com sucesso!", "success")
        return redirect(url_for('financeiro.entradas'))

    # 🔹 Filtros (um único campo para buscar em tipo, conta e descrição)
    filtro = request.args.get("filtro")
    filtro_data_inicio = request.args.get("inicio")
    filtro_data_fim = request.args.get("fim")

    query = Financeiro.query.filter_by(tipo="Entrada")
    if filtro:
        query = query.filter(
            or_(
                Financeiro.tipo.ilike(f"%{filtro}%"),
                Financeiro.conta.ilike(f"%{filtro}%"),
                Financeiro.descricao.ilike(f"%{filtro}%")
            )
        )
    if filtro_data_inicio and filtro_data_fim:
        query = query.filter(Financeiro.data.between(filtro_data_inicio, filtro_data_fim))

    # 🔹 Paginação
    page = request.args.get("page", 1, type=int)
    registros = query.order_by(Financeiro.data.desc()).paginate(page=page, per_page=10, error_out=False)

    # 🔹 Totais
    hoje = date.today()
    total_mes = db.session.query(db.func.sum(Financeiro.valor)).filter(
        Financeiro.tipo == "Entrada",
        db.extract("month", Financeiro.data) == hoje.month,
        db.extract("year", Financeiro.data) == hoje.year
    ).scalar() or 0

    total_ano = db.session.query(db.func.sum(Financeiro.valor)).filter(
        Financeiro.tipo == "Entrada",
        db.extract("year", Financeiro.data) == hoje.year
    ).scalar() or 0

    ultima = Financeiro.query.filter_by(tipo="Entrada").order_by(Financeiro.data.desc()).first()

    return render_template(
        "financeiro/entradas.html",
        form=form,
        entradas=registros.items,
        pagination=registros,
        total_mes=total_mes,
        total_ano=total_ano,
        ultima=ultima,
        filtro=filtro,
        filtro_data_inicio=filtro_data_inicio,
        filtro_data_fim=filtro_data_fim
    )


# -----------------------------
# 📄 Excluir Entradas
# -----------------------------
@financeiro_bp.route('/entradas/excluir/<int:id>', methods=['POST'])
@login_required
@permission_required("financeiro", "delete")
def excluir_entrada(id):
    entrada = Financeiro.query.get_or_404(id)
    if entrada.tipo != "Entrada":
        flash("Registro inválido para exclusão.", "danger")
        return redirect(url_for('financeiro.entradas'))

    try:
        db.session.delete(entrada)
        db.session.commit()
        registrar_log(current_user.nome, f"Excluiu entrada: {entrada.descricao}", "sucesso")
        flash("Entrada excluída com sucesso!", "success")
    except Exception:
        db.session.rollback()
        registrar_log(current_user.nome, f"Erro ao excluir entrada: {entrada.descricao}", "erro")
        flash("Erro ao excluir entrada.", "danger")

    return redirect(url_for('financeiro.entradas'))
    

# -----------------------------
# 📄 Excluir Comprovante
# -----------------------------
@financeiro_bp.route('/excluir_comprovante/<int:id>', methods=['POST'])
@login_required
@permission_required("financeiro", "edit")
def excluir_comprovante(id):
    entrada = Financeiro.query.get_or_404(id)

    if entrada.comprovante:
        filepath = os.path.join(current_app.root_path, entrada.comprovante.lstrip("/"))
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            flash(f"Erro ao excluir arquivo: {e}", "danger")

        entrada.comprovante = None
        db.session.commit()

        registrar_log(current_user.nome, f"Excluiu comprovante da entrada {entrada.id}", "sucesso")
        flash("Comprovante excluído com sucesso!", "success")
    else:
        flash("Nenhum comprovante para excluir.", "warning")

    return redirect(url_for("financeiro.editar_entrada", id=id))


# -----------------------------
# 📄 Editar Entrada
# -----------------------------
@financeiro_bp.route('/editar_entrada/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required("financeiro", "edit")
def editar_entrada(id):
    entrada = Financeiro.query.get_or_404(id)
    form = EntradaForm(obj=entrada)

    if form.validate_on_submit():
        entrada.tipo = "Entrada"
        entrada.categoria = form.tipo_receita.data
        entrada.valor = float(str(form.valor.data).replace(',', '.'))
        entrada.data = form.data.data
        entrada.descricao = form.descricao.data
        entrada.conta = form.conta.data
        entrada.usuario = current_user.nome  # ✅ sempre logado

        # Só adiciona comprovante se não existir
        if not entrada.comprovante:
            comprovante_file = request.files.get("comprovante")
            if comprovante_file and comprovante_file.filename:
                ext = os.path.splitext(comprovante_file.filename)[1].lower()
                filename = f"{uuid.uuid4().hex}{ext}"
                upload_dir = os.path.join(current_app.root_path, "static", "uploads", "financeiro")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                comprovante_file.save(filepath)
                entrada.comprovante = f"/static/uploads/financeiro/{filename}"

        db.session.commit()
        registrar_log(current_user.nome, f"Editou entrada: {entrada.descricao}", "sucesso")
        flash("Entrada atualizada com sucesso!", "success")
        return redirect(url_for("financeiro.entradas"))

    return render_template("financeiro/editar_entrada.html", form=form, entrada=entrada)


# -----------------------------
# 📄 Saídas
# -----------------------------
@financeiro_bp.route('/saidas', methods=['GET', 'POST'])
@login_required
@permission_required("financeiro", "view")
def saidas():
    form = SaidaForm()
    if form.validate_on_submit():
        # 🔹 exige permissão de criação
        if not current_user.has_permission("financeiro", "create"):
            flash("Você não tem permissão para criar saídas.", "danger")
            registrar_log(current_user.nome, "Tentou criar saída sem permissão", "falha")
            return redirect(url_for("financeiro.saidas"))

        raw_valor = request.form.get('valor', '')
        valor_float = float(str(raw_valor).replace(',', '.'))

        nova = Financeiro(
            tipo="Saída",
            categoria=form.categoria.data,
            valor=valor_float,
            data=form.data.data,
            descricao=form.descricao.data,
            conta=form.conta.data
        )
        db.session.add(nova)
        db.session.commit()
        registrar_log(current_user.nome, f"Registrou saída: {nova.descricao}", "sucesso")
        flash("Saída registrada com sucesso!", "success")
        return redirect(url_for('financeiro.saidas'))

    registros = Financeiro.query.filter_by(tipo="Saída").order_by(Financeiro.data.desc()).all()
    return render_template('financeiro/saidas.html', form=form, saidas=registros)


@financeiro_bp.route('/saidas/excluir/<int:id>', methods=['POST'])
@login_required
@permission_required("financeiro", "delete")
def excluir_saida(id):
    saida = Financeiro.query.get_or_404(id)
    if saida.tipo != "Saída":
        flash("Registro inválido para exclusão.", "danger")
        return redirect(url_for('financeiro.saidas'))

    try:
        db.session.delete(saida)
        db.session.commit()
        registrar_log(current_user.nome, f"Excluiu saída: {saida.descricao}", "sucesso")
        flash("Saída excluída com sucesso!", "success")
    except Exception:
        db.session.rollback()
        registrar_log(current_user.nome, f"Erro ao excluir saída: {saida.descricao}", "erro")
        flash("Erro ao excluir saída.", "danger")

    return redirect(url_for('financeiro.saidas'))
    

@financeiro_bp.route('/saidas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required("financeiro", "edit")
def editar_saida(id):
    saida = Financeiro.query.get_or_404(id)
    if saida.tipo != "Saída":
        flash("Registro inválido para edição.", "danger")
        return redirect(url_for('financeiro.saidas'))

    form = SaidaForm(obj=saida)
    if form.validate_on_submit():
        saida.categoria = form.categoria.data
        saida.valor = float(str(form.valor.data).replace(',', '.'))
        saida.valor = float(str(form.valor.data).replace(',', '.'))
        saida.data = form.data.data
        saida.descricao = form.descricao.data
        saida.conta = form.conta.data
        db.session.commit()
        registrar_log(current_user.nome, f"Editou saída: {saida.descricao}", "sucesso")
        flash("Saída atualizada com sucesso!", "success")
        return redirect(url_for('financeiro.saidas'))

    return render_template('financeiro/editar_saida.html', form=form, saida=saida)


# -----------------------------
# 📄 Relatórios
# -----------------------------
@financeiro_bp.route('/relatorios', methods=['GET', 'POST'])
@login_required
@permission_required("financeiro", "view")
def relatorios():
    form = FiltroRelatorioForm()
    query = Financeiro.query

    if form.validate_on_submit():
        if form.inicio.data:
            query = query.filter(Financeiro.data >= form.inicio.data)
        if form.fim.data:
            query = query.filter(Financeiro.data <= form.fim.data)
        if form.tipo.data:
            query = query.filter(Financeiro.tipo == form.tipo.data)
        if form.categoria.data:
            query = query.filter(Financeiro.categoria.ilike(f"%{form.categoria.data}%"))

    # 🔹 Paginação
    page = request.args.get("page", 1, type=int)
    registros = query.order_by(Financeiro.data.desc()).paginate(page=page, per_page=15, error_out=False)

    # 🔹 Totais (com base em todos os registros filtrados, não só da página atual)
    todos_registros = query.all()
    total = sum(r.valor for r in todos_registros)
    total_entradas = sum(r.valor for r in todos_registros if r.tipo == "Entrada")
    total_saidas = sum(r.valor for r in todos_registros if r.tipo == "Saída")

    por_categoria = defaultdict(float)
    for r in todos_registros:
        por_categoria[r.categoria] += float(r.valor)

    categorias_labels = list(por_categoria.keys())
    categorias_data = [por_categoria[c] for c in categorias_labels]

    registrar_log(current_user.nome, "Gerou relatório financeiro", "sucesso")
    return render_template(
        'financeiro/relatorios.html',
        form=form,
        registros=registros,   # 🔹 objeto de paginação
        total=total,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        categorias_labels=categorias_labels,
        categorias_data=categorias_data
    )


# -----------------------------
# 📄 Exportação CSV
# -----------------------------
@financeiro_bp.route('/export.csv')
@login_required
@permission_required("financeiro", "view")
def export_csv():
    inicio_str = request.args.get('inicio')
    fim_str = request.args.get('fim')
    tipo = request.args.get('tipo')
    categoria = request.args.get('categoria')

    query = Financeiro.query
    def parse_date(s):
        return datetime.strptime(s, "%d-%m-%Y").date()

    if inicio_str:
        query = query.filter(Financeiro.data >= parse_date(inicio_str))
    if fim_str:
        query = query.filter(Financeiro.data <= parse_date(fim_str))
    if tipo:
        query = query.filter(Financeiro.tipo == tipo)
    if categoria:
        query = query.filter(Financeiro.categoria.ilike(f"%{categoria}%"))

    registros = query.order_by(Financeiro.data.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Data", "Tipo", "Categoria", "Conta", "Descrição", "Valor", "CPF Membro", "CNPJ Fornecedor", "Conciliado"])
    for r in registros:
        writer.writerow([
            r.data.strftime("%d-%m-%Y"),
            r.tipo,
            r.categoria,
            r.conta,
            r.descricao or "",
            f"{r.valor:.2f}",
            r.cpf_membro or "",
            r.cnpj_fornecedor or "",
            "Sim" if r.conciliado else "Não"
        ])

    registrar_log(current_user.nome, "Exportou relatório financeiro em CSV", "sucesso")
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=relatorio_financeiro.csv"})


# -----------------------------
# 📄 Comprovantes (Consulta)
# -----------------------------
@financeiro_bp.route('/comprovantes', methods=['GET'])
@login_required
@permission_required("financeiro", "view")
def comprovantes():
    filtro = request.args.get("filtro")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    query = Financeiro.query.filter(
        Financeiro.tipo.in_(["Entrada", "Saída"]),
        Financeiro.comprovante.isnot(None)
    )

    if filtro:
        query = query.filter(Financeiro.descricao.ilike(f"%{filtro}%"))

    if inicio and fim:
        query = query.filter(Financeiro.data.between(inicio, fim))

    # 🔹 Paginação com limite de 15 por página
    page = request.args.get("page", 1, type=int)
    registros = query.order_by(Financeiro.data.desc()).paginate(page=page, per_page=15, error_out=False)

    # 🔹 Agrupar por mês/ano (apenas os itens da página atual)
    por_mes = defaultdict(list)
    for r in registros.items:
        chave = r.data.strftime("%m-%Y")
        por_mes[chave].append(r)

    return render_template(
        "financeiro/comprovantes.html",
        por_mes=por_mes,
        pagination=registros if registros.total >= 15 else None  # só mostra paginação se tiver 15 ou mais
    )

