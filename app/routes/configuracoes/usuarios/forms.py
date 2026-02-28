from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class NovoUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome"), Length(min=3, max=50)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Informe o email"), Email(message="Email inválido")]
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(message="Informe a senha"), Length(min=6, message="A senha deve ter pelo menos 6 caracteres")]
    )
    # 🔹 Campo Nível ajustado para trabalhar com is_admin
    is_admin = SelectField(
        "Nível",
        choices=[("true", "Administrador"), ("false", "Usuário")],
        validators=[DataRequired(message="Selecione o nível")],
        default="false"
    )
    ativo = SelectField(
        "Status",
        choices=[("true", "Ativo"), ("false", "Inativo")],
        validators=[DataRequired(message="Selecione o status")],
        default="true"
    )
    foto = FileField("Foto de Perfil")
    submit = SubmitField("Criar Usuário")


class EditarUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome"), Length(min=3, max=50)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Informe o email"), Email(message="Email inválido")]
    )
    senha = PasswordField(
        "Senha (opcional)",
        validators=[Optional(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres")]
    )
    # 🔹 Campo Nível ajustado para trabalhar com is_admin
    is_admin = SelectField(
        "Nível",
        choices=[("true", "Administrador"), ("false", "Usuário")],
        validators=[DataRequired(message="Selecione o nível")]
    )
    ativo = SelectField(
        "Status",
        choices=[("true", "Ativo"), ("false", "Inativo")],
        validators=[DataRequired(message="Selecione o status")]
    )
    foto = FileField("Foto de Perfil")
    submit = SubmitField("Salvar Alterações")
