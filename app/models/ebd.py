from datetime import datetime, timezone, date
from app.extensions import db

# -----------------------------
# 🏫 Configuração Geral da EBD
# -----------------------------
class EbdConfig(db.Model):
    __tablename__ = "ebd_config"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, default="Escola Bíblica Dominical")
    descricao = db.Column(db.Text, nullable=True)
    dia_semana = db.Column(db.String(30), nullable=False, default="Domingo")
    horario_inicio = db.Column(db.String(10), nullable=True, default="09:00")
    horario_termino = db.Column(db.String(10), nullable=True, default="10:30")
    
    # Responsável / Coordenador Geral da EBD (membro)
    coordenador_id = db.Column(db.Integer, db.ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    coordenador = db.relationship("Member", foreign_keys=[coordenador_id], backref="ebd_coordenadas")

    ativo = db.Column(db.Boolean, default=True)
    atualizado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EbdConfig {self.nome}>"


# -----------------------------
# 📅 Períodos Letivos / Trimestres
# -----------------------------
class EbdPeriodo(db.Model):
    __tablename__ = "ebd_periodos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False) # Ex: "1º Trimestre 2026"
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    
    # Status: planejado, em_andamento, encerrado
    status = db.Column(db.String(30), nullable=False, default="em_andamento")
    observacoes = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    classes = db.relationship("EbdClasse", backref="periodo", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<EbdPeriodo {self.nome} ({self.status})>"


# -----------------------------
# 📚 Classes / Turmas
# -----------------------------
class EbdClasse(db.Model):
    __tablename__ = "ebd_classes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False) # Ex: "Jovens - Geração Eleita", "Adultos", "Primários"
    faixa_etaria = db.Column(db.String(60), nullable=True) # Ex: "18 a 35 anos", "7 a 9 anos"
    sala = db.Column(db.String(100), nullable=True) # Ex: "Sala 03 - 1º Andar"
    capacidade = db.Column(db.Integer, nullable=True, default=30)
    status = db.Column(db.String(20), nullable=False, default="ativa") # ativa, inativa
    descricao = db.Column(db.Text, nullable=True)
    
    periodo_id = db.Column(db.Integer, db.ForeignKey("ebd_periodos.id", ondelete="CASCADE"), nullable=False)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    professores = db.relationship("EbdProfessor", backref="classe", cascade="all, delete-orphan", lazy=True)
    matriculas = db.relationship("EbdMatricula", backref="classe", cascade="all, delete-orphan", lazy=True)
    aulas = db.relationship("EbdAula", backref="classe", cascade="all, delete-orphan", lazy=True)

    @property
    def professor_principal(self):
        p = next((prof for prof in self.professores if prof.cargo == "principal" and prof.status == "ativo"), None)
        return p.membro if p else None

    @property
    def total_matriculados_ativos(self):
        return len([m for m in self.matriculas if m.status == "ativo"])

    def __repr__(self):
        return f"<EbdClasse {self.nome}>"


# -----------------------------
# 👨‍🏫 Professores da Classe
# -----------------------------
class EbdProfessor(db.Model):
    __tablename__ = "ebd_professores"

    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, db.ForeignKey("ebd_classes.id", ondelete="CASCADE"), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    
    # Cargo: principal, auxiliar, substituto
    cargo = db.Column(db.String(30), nullable=False, default="principal")
    status = db.Column(db.String(20), nullable=False, default="ativo") # ativo, inativo
    data_inicio = db.Column(db.Date, nullable=True, default=date.today)
    data_fim = db.Column(db.Date, nullable=True)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamento com Member
    membro = db.relationship("Member", backref="ebd_lecionadas")

    def __repr__(self):
        return f"<EbdProfessor {self.membro.nome if self.membro else self.membro_id} - {self.cargo}>"


# -----------------------------
# 🎓 Matrícula do Aluno
# -----------------------------
class EbdMatricula(db.Model):
    __tablename__ = "ebd_matriculas"
    __table_args__ = (
        db.UniqueConstraint("classe_id", "membro_id", "status", name="uq_classe_membro_status_ativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, db.ForeignKey("ebd_classes.id", ondelete="CASCADE"), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    
    data_matricula = db.Column(db.Date, nullable=False, default=date.today)
    
    # Status: ativo, inativo, transferido, desligado
    status = db.Column(db.String(20), nullable=False, default="ativo")
    data_saida = db.Column(db.Date, nullable=True)
    motivo_saida = db.Column(db.String(200), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    membro = db.relationship("Member", backref="ebd_matriculas")
    frequencias = db.relationship("EbdFrequencia", backref="matricula", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<EbdMatricula Aluno={self.membro.nome if self.membro else self.membro_id} Classe={self.classe_id}>"


# -----------------------------
# 📖 Aulas / Encontros
# -----------------------------
class EbdAula(db.Model):
    __tablename__ = "ebd_aulas"

    id = db.Column(db.Integer, primary_key=True)
    classe_id = db.Column(db.Integer, db.ForeignKey("ebd_classes.id", ondelete="CASCADE"), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    
    data_aula = db.Column(db.Date, nullable=False)
    numero_licao = db.Column(db.String(20), nullable=True) # Ex: "Lição 08"
    tema = db.Column(db.String(200), nullable=False) # Ex: "A Fidelidade de Deus em Tempos de Prova"
    resumo_conteudo = db.Column(db.Text, nullable=True)
    
    # Status: planejada, realizada, cancelada
    status = db.Column(db.String(20), nullable=False, default="realizada")
    observacoes = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    professor = db.relationship("Member", foreign_keys=[professor_id], backref="ebd_aulas_ministradas")
    frequencias = db.relationship("EbdFrequencia", backref="aula", cascade="all, delete-orphan", lazy=True)

    @property
    def total_presentes(self):
        return len([f for f in self.frequencias if f.status_presenca == "presente"])

    @property
    def total_faltas(self):
        return len([f for f in self.frequencias if f.status_presenca in ["falta", "falta_justificada"]])

    @property
    def total_visitantes(self):
        return len([f for f in self.frequencias if f.status_presenca == "visitante"])

    def __repr__(self):
        return f"<EbdAula {self.data_aula} - {self.tema}>"


# -----------------------------
# ✅ Frequência / Presença
# -----------------------------
class EbdFrequencia(db.Model):
    __tablename__ = "ebd_frequencias"
    __table_args__ = (
        db.UniqueConstraint("aula_id", "matricula_id", name="uq_aula_matricula"),
    )

    id = db.Column(db.Integer, primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey("ebd_aulas.id", ondelete="CASCADE"), nullable=False)
    matricula_id = db.Column(db.Integer, db.ForeignKey("ebd_matriculas.id", ondelete="CASCADE"), nullable=False)
    
    # Status: presente, falta, falta_justificada, visitante
    status_presenca = db.Column(db.String(30), nullable=False, default="presente")
    
    # Motivo: doenca, viagem, trabalho, familia, outro
    motivo_falta = db.Column(db.String(50), nullable=True)
    justificativa = db.Column(db.Text, nullable=True)
    observacao_aluno = db.Column(db.Text, nullable=True)
    
    registrado_por = db.Column(db.String(100), nullable=True)
    
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EbdFrequencia Aula={self.aula_id} Matrícula={self.matricula_id} Status={self.status_presenca}>"
