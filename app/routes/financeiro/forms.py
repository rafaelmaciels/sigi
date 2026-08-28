from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, FileField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileAllowed, FileRequired
from app.models.financeiro import (
    CATEGORIAS_RECEITAS_PADRAO,
    CATEGORIAS_DESPESAS_PADRAO,
    DEPARTAMENTOS_PADRAO,
    CONTAS_PADRAO,
    FORMAS_PAGAMENTO_PADRAO
)

class EntradaForm(FlaskForm):
    tipo_receita = SelectField(
        "Categoria de Entrada",
        choices=[(c, c) for c in CATEGORIAS_RECEITAS_PADRAO],
        validators=[DataRequired(message="Selecione a categoria da entrada.")]
    )
    membro_id = SelectField("Membro Contribuinte (Opcional para Dízimos/Ofertas)", coerce=int, validators=[Optional()])
    valor = DecimalField("Valor (R$)", validators=[DataRequired(message="Informe o valor."), NumberRange(min=0.01, message="O valor deve ser maior que zero.")], places=2)
    data = DateField("Data do Lançamento", format='%Y-%m-%d', validators=[DataRequired(message="Data obrigatória.")])
    forma_pagamento = SelectField("Forma de Pagamento", choices=[(f, f) for f in FORMAS_PAGAMENTO_PADRAO], validators=[DataRequired()])
    conta = SelectField("Conta / Fundo de Destino", choices=[(c, c) for c in CONTAS_PADRAO], validators=[DataRequired()])
    departamento = SelectField("Departamento Beneficiário", choices=[(d, d) for d in DEPARTAMENTOS_PADRAO], default="Templo / Geral")
    descricao = StringField("Descrição / Referência (ex: Culto de Domingo, Campanha)", validators=[Optional()])
    observacoes = TextAreaField("Observações Adicionais", validators=[Optional()])
    
    comprovante = FileField("Comprovante (PIX, Recibo ou Extrato)", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'webp'], "Formatos permitidos: Imagens (JPG, PNG, WEBP) ou PDF.")
    ])
    submit = SubmitField("Salvar Entrada")


class SaidaForm(FlaskForm):
    categoria = SelectField(
        "Categoria da Despesa",
        choices=[(c, c) for c in CATEGORIAS_DESPESAS_PADRAO],
        validators=[DataRequired(message="Selecione a categoria da despesa.")]
    )
    departamento = SelectField("Departamento / Centro de Custo", choices=[(d, d) for d in DEPARTAMENTOS_PADRAO], validators=[DataRequired()])
    valor = DecimalField("Valor (R$)", validators=[DataRequired(message="Informe o valor."), NumberRange(min=0.01, message="O valor deve ser maior que zero.")], places=2)
    data = DateField("Data do Pagamento", format='%Y-%m-%d', validators=[DataRequired(message="Data obrigatória.")])
    forma_pagamento = SelectField("Forma de Pagamento", choices=[(f, f) for f in FORMAS_PAGAMENTO_PADRAO], validators=[DataRequired()])
    conta = SelectField("Conta / Fundo de Origem", choices=[(c, c) for c in CONTAS_PADRAO], validators=[DataRequired()])
    cnpj_fornecedor = StringField("CNPJ / CPF do Favorecido", validators=[Optional()])
    descricao = StringField("Descrição do Pagamento / Fornecedor", validators=[Optional()])
    observacoes = TextAreaField("Detalhes / Justificativa", validators=[Optional()])
    
    comprovante = FileField("Comprovante / Nota Fiscal", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'webp'], "Formatos permitidos: Imagens (JPG, PNG, WEBP) ou PDF.")
    ])
    submit = SubmitField("Salvar Saída")


class FiltroRelatorioForm(FlaskForm):
    inicio = DateField("Data Inicial", format='%Y-%m-%d', validators=[Optional()])
    fim = DateField("Data Final", format='%Y-%m-%d', validators=[Optional()])
    tipo = SelectField("Tipo", choices=[
        ("", "Todos os Tipos"),
        ("Entrada", "Entradas (Receitas)"),
        ("Saída", "Saídas (Despesas)")
    ], validators=[Optional()])
    categoria = SelectField("Categoria", choices=[("", "Todas as Categorias")] + [(c, c) for c in set(CATEGORIAS_RECEITAS_PADRAO + CATEGORIAS_DESPESAS_PADRAO)], validators=[Optional()])
    conta = SelectField("Conta / Fundo", choices=[("", "Todas as Contas")] + [(c, c) for c in CONTAS_PADRAO], validators=[Optional()])
    departamento = SelectField("Departamento", choices=[("", "Todos os Departamentos")] + [(d, d) for d in DEPARTAMENTOS_PADRAO], validators=[Optional()])
    submit = SubmitField("Aplicar Filtros")


class ComprovanteForm(FlaskForm):
    arquivo = FileField("Comprovante / Arquivo", validators=[
        FileRequired(message="Selecione um arquivo."),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'webp'], "Formatos permitidos: Imagens ou PDF.")
    ])
    data = DateField("Data", format='%Y-%m-%d', validators=[DataRequired()])
    descricao = StringField("Identificação do Comprovante", validators=[Optional()])
    submit = SubmitField("Fazer Upload")
