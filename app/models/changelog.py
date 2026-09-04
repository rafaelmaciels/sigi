from datetime import datetime, timezone
from app.extensions import db

TIPOS_CHANGELOG = (
    "Nova funcionalidade",
    "Melhoria",
    "Ajuste",
    "Correção",
    "Manutenção"
)

MODULOS_CHANGELOG = (
    "Secretaria & Membros",
    "Financeiro",
    "Escola Dominical (EBD)",
    "Escalas & Voluntários",
    "Eventos & Calendário",
    "Documentos",
    "Patrimônio",
    "Dashboard",
    "Configurações & Segurança",
    "Geral / Sistema"
)

class Changelog(db.Model):
    __tablename__ = "changelogs"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    modulo = db.Column(db.String(50), nullable=False, default="Geral / Sistema")
    tipo = db.Column(db.String(30), nullable=False, default="Melhoria")
    descricao = db.Column(db.Text, nullable=False)
    finalidade = db.Column(db.Text, nullable=False)
    data_implantacao = db.Column(db.Date, nullable=False)
    versao = db.Column(db.String(20), nullable=True)

    # Vínculo com usuário responsável
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    usuario = db.relationship("User", backref=db.backref("changelogs", lazy=True))

    # Nome preservado para histórico do Git ou quando o usuário não tiver conta
    autor_nome = db.Column(db.String(100), nullable=True)

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    atualizado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @property
    def responsavel(self) -> str:
        if self.usuario and self.usuario.display_name:
            return self.usuario.display_name
        return self.autor_nome or "Equipe SIGI"

    @property
    def badge_class(self) -> str:
        classes = {
            "Nova funcionalidade": "bg-success-subtle text-success border border-success-subtle",
            "Melhoria": "bg-primary-subtle text-primary border border-primary-subtle",
            "Ajuste": "bg-warning-subtle text-warning border border-warning-subtle",
            "Correção": "bg-danger-subtle text-danger border border-danger-subtle",
            "Manutenção": "bg-secondary-subtle text-secondary border border-secondary-subtle"
        }
        return classes.get(self.tipo, "bg-secondary-subtle text-secondary border border-secondary-subtle")

    @property
    def badge_icon(self) -> str:
        icons = {
            "Nova funcionalidade": "bi-plus-circle-fill",
            "Melhoria": "bi-arrow-up-circle-fill",
            "Ajuste": "bi-sliders",
            "Correção": "bi-exclamation-triangle-fill",
            "Manutenção": "bi-gear-fill"
        }
        return icons.get(self.tipo, "bi-check-circle")

    @property
    def modulo_icon(self) -> str:
        icons = {
            "Secretaria & Membros": "bi-people",
            "Financeiro": "bi-wallet2",
            "Escola Dominical (EBD)": "bi-book",
            "Escalas & Voluntários": "bi-clipboard-check",
            "Eventos & Calendário": "bi-calendar-event",
            "Documentos": "bi-file-earmark-text",
            "Patrimônio": "bi-box-seam",
            "Dashboard": "bi-grid-1x2",
            "Configurações & Segurança": "bi-shield-lock",
            "Geral / Sistema": "bi-cpu"
        }
        return icons.get(self.modulo, "bi-app")

    def __repr__(self):
        return f"<Changelog #{self.id} {self.data_implantacao} - {self.titulo}>"
