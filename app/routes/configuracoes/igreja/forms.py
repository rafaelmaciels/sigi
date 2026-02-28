from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, Email

class IgrejaForm(FlaskForm):
    nome = StringField("Nome da Igreja", validators=[DataRequired(), Length(max=150)])
    cnpj = StringField("CNPJ", validators=[Optional(), Length(max=20)])
    endereco = StringField("Endereço", validators=[Optional(), Length(max=200)])
    telefone = StringField("Telefone", validators=[Optional(), Length(max=20)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    site = StringField("Site", validators=[Optional(), Length(max=120)])
    pastor_responsavel = StringField("Pastor Responsável", validators=[Optional(), Length(max=120)])
    ano_fundacao = IntegerField("Ano de Fundação", validators=[Optional()])
    versiculo_tema = StringField("Versículo Tema", validators=[Optional(), Length(max=250)])

    submit = SubmitField("Salvar")
