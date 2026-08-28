from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

# -----------------------------
# 🏫 Formulário de Configuração da EBD
# -----------------------------
class EbdConfigForm(FlaskForm):
    nome = StringField("Nome da Escola Dominical*", validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField("Descrição Institucional", validators=[Optional()])
    dia_semana = SelectField(
        "Dia Principal das Aulas",
        choices=[
            ("Domingo", "Domingo"),
            ("Sábado", "Sábado"),
            ("Quarta-feira", "Quarta-feira"),
            ("Quinta-feira", "Quinta-feira"),
            ("Outro", "Outro")
        ],
        default="Domingo",
        validators=[DataRequired()]
    )
    horario_inicio = StringField("Horário de Início (ex: 09:00)", validators=[Optional(), Length(max=10)])
    horario_termino = StringField("Horário de Término (ex: 10:30)", validators=[Optional(), Length(max=10)])
    coordenador_id = SelectField("Coordenador / Responsável Geral", coerce=int, validators=[Optional()])
    ativo = BooleanField("EBD Ativa", default=True)
    submit = SubmitField("Salvar Configurações")


# -----------------------------
# 📅 Formulário de Período Letivo
# -----------------------------
class EbdPeriodoForm(FlaskForm):
    nome = StringField("Nome do Período / Trimestre*", validators=[DataRequired(), Length(max=100)])
    data_inicio = DateField("Data de Início*", format="%Y-%m-%d", validators=[DataRequired()])
    data_fim = DateField("Data de Término*", format="%Y-%m-%d", validators=[DataRequired()])
    status = SelectField(
        "Status do Período",
        choices=[
            ("planejado", "Planejado"),
            ("em_andamento", "Em Andamento"),
            ("encerrado", "Encerrado")
        ],
        default="em_andamento",
        validators=[DataRequired()]
    )
    observacoes = TextAreaField("Observações / Diretrizes do Trimestre", validators=[Optional()])
    submit = SubmitField("Salvar Período")


# -----------------------------
# 📚 Formulário de Classe / Turma
# -----------------------------
class EbdClasseForm(FlaskForm):
    nome = StringField("Nome da Classe*", validators=[DataRequired(), Length(max=120)])
    periodo_id = SelectField("Período Letivo*", coerce=int, validators=[DataRequired()])
    faixa_etaria = StringField("Faixa Etária / Público (ex: 18 a 35 anos)", validators=[Optional(), Length(max=60)])
    sala = StringField("Sala / Local (ex: Sala 02 - Anexo)", validators=[Optional(), Length(max=100)])
    capacidade = IntegerField("Capacidade Máxima", default=30, validators=[Optional(), NumberRange(min=1, max=500)])
    status = SelectField(
        "Status da Classe",
        choices=[
            ("ativa", "Ativa"),
            ("inativa", "Inativa")
        ],
        default="ativa",
        validators=[DataRequired()]
    )
    descricao = TextAreaField("Descrição / Ementa da Classe", validators=[Optional()])
    submit = SubmitField("Salvar Classe")


# -----------------------------
# 👨‍🏫 Formulário de Vínculo de Professor
# -----------------------------
class EbdProfessorForm(FlaskForm):
    membro_id = SelectField("Professor (Membro da Igreja)*", coerce=int, validators=[DataRequired()])
    classe_id = SelectField("Classe*", coerce=int, validators=[DataRequired()])
    cargo = SelectField(
        "Função / Cargo*",
        choices=[
            ("principal", "Professor Titular / Principal"),
            ("auxiliar", "Professor Auxiliar"),
            ("substituto", "Professor Substituto")
        ],
        default="principal",
        validators=[DataRequired()]
    )
    status = SelectField(
        "Status",
        choices=[
            ("ativo", "Ativo"),
            ("inativo", "Inativo")
        ],
        default="ativo",
        validators=[DataRequired()]
    )
    data_inicio = DateField("Data de Início", format="%Y-%m-%d", validators=[Optional()])
    data_fim = DateField("Data de Término", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Salvar Vínculo")


# -----------------------------
# 🎓 Formulário de Matrícula de Aluno
# -----------------------------
class EbdMatriculaForm(FlaskForm):
    classe_id = SelectField("Classe / Turma*", coerce=int, validators=[DataRequired()])
    membro_id = SelectField("Aluno (Membro da Igreja)*", coerce=int, validators=[DataRequired()])
    data_matricula = DateField("Data da Matrícula*", format="%Y-%m-%d", validators=[DataRequired()])
    status = SelectField(
        "Status da Matrícula",
        choices=[
            ("ativo", "Ativo"),
            ("inativo", "Inativo"),
            ("desligado", "Desligado")
        ],
        default="ativo",
        validators=[DataRequired()]
    )
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Confirmar Matrícula")


# -----------------------------
# 🔄 Formulário de Transferência de Aluno
# -----------------------------
class EbdTransferenciaForm(FlaskForm):
    nova_classe_id = SelectField("Nova Classe / Turma*", coerce=int, validators=[DataRequired()])
    motivo_saida = StringField("Motivo da Transferência (ex: Mudança de Faixa Etária)", validators=[Optional(), Length(max=200)])
    observacoes = TextAreaField("Observações Adicionais", validators=[Optional()])
    submit = SubmitField("Efetuar Transferência")


# -----------------------------
# 📖 Formulário de Aula / Encontro
# -----------------------------
class EbdAulaForm(FlaskForm):
    classe_id = SelectField("Classe / Turma*", coerce=int, validators=[DataRequired()])
    professor_id = SelectField("Professor Ministrante", coerce=int, validators=[Optional()])
    data_aula = DateField("Data da Aula*", format="%Y-%m-%d", validators=[DataRequired()])
    numero_licao = StringField("Número da Lição (ex: Lição 07)", validators=[Optional(), Length(max=20)])
    tema = StringField("Tema da Lição*", validators=[DataRequired(), Length(max=200)])
    resumo_conteudo = TextAreaField("Resumo do Conteúdo / Textos Bíblicos", validators=[Optional()])
    status = SelectField(
        "Status da Aula",
        choices=[
            ("realizada", "Realizada"),
            ("planejada", "Planejada"),
            ("cancelada", "Cancelada")
        ],
        default="realizada",
        validators=[DataRequired()]
    )
    observacoes = TextAreaField("Observações da Aula", validators=[Optional()])
    submit = SubmitField("Salvar Aula")
