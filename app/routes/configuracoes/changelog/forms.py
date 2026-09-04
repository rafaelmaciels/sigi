from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date
from app.models.changelog import TIPOS_CHANGELOG, MODULOS_CHANGELOG

class ChangelogForm(FlaskForm):
    data_implantacao = DateField(
        "Data da Implantação",
        validators=[DataRequired(message="Informe a data da implantação")],
        default=date.today
    )
    titulo = StringField(
        "Título da Alteração",
        validators=[
            DataRequired(message="Informe o título da alteração"),
            Length(min=3, max=150, message="O título deve ter entre 3 e 150 caracteres")
        ]
    )
    modulo = SelectField(
        "Módulo",
        choices=[(m, m) for m in MODULOS_CHANGELOG],
        validators=[DataRequired(message="Selecione o módulo")],
        default="Geral / Sistema"
    )
    tipo = SelectField(
        "Tipo",
        choices=[(t, t) for t in TIPOS_CHANGELOG],
        validators=[DataRequired(message="Selecione o tipo da alteração")],
        default="Melhoria"
    )
    versao = StringField(
        "Versão / Release (opcional)",
        validators=[Optional(), Length(max=20, message="Máximo de 20 caracteres")]
    )
    descricao = TextAreaField(
        "Descrição da Alteração (O que mudou?)",
        validators=[
            DataRequired(message="Descreva detalhadamente a alteração realizada"),
            Length(min=5, message="A descrição deve ter pelo menos 5 caracteres")
        ]
    )
    finalidade = TextAreaField(
        "Finalidade / Benefício (Por que foi feito?)",
        validators=[
            DataRequired(message="Explique o motivo e o benefício gerado por esta alteração"),
            Length(min=5, message="A finalidade deve ter pelo menos 5 caracteres")
        ]
    )
    usuario_id = SelectField(
        "Responsável pela Implantação",
        coerce=int,
        validators=[Optional()]
    )
    autor_nome = StringField(
        "Nome do Responsável Manual / Histórico (opcional)",
        validators=[Optional(), Length(max=100, message="Máximo de 100 caracteres")]
    )
    submit = SubmitField("Salvar Atualização")
