from datetime import datetime, timezone
import uuid
from app.extensions import db

# -----------------------------
# 📅 Eventos
# -----------------------------
class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # 🔹 Tipos de evento permitidos
    TIPOS_EVENTO = [
        "culto especial",
        "retiro",
        "batismo",
        "reunião",
        "evangelismo",
        "conferência",
        "outros"
    ]

    tipo = db.Column(db.String(50), nullable=False)

    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)

    local = db.Column(db.String(150), nullable=True)
    organizador = db.Column(db.String(100), nullable=True)

    # 🔹 Status permitidos
    STATUS_EVENTO = [
        "confirmado",
        "planejado",
        "em andamento",
        "concluído",
        "cancelado"
    ]

    status = db.Column(db.String(20), nullable=False, default="confirmado")

    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # 🔗 Token público único para compartilhamento
    public_token = db.Column(
        db.String(16),
        unique=True,
        nullable=False,
        default=lambda: uuid.uuid4().hex[:12]
    )

    # 🔐 Data de expiração do token público
    token_expira_em = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        data_str = self.data_inicio.strftime('%d/%m/%Y %H:%M') if self.data_inicio else "sem data"
        return f"<Evento {self.titulo} - {data_str}>"

    @classmethod
    def get_order_by_proximos_e_passados(cls, ref_now=None):
        """
        Retorna as expressões de ordenação dinâmica para eventos:
        1. Próximos eventos (>= ref_now), ordenados do mais próximo ao mais distante (ASC).
        2. Eventos passados (< ref_now), ordenados do mais recente ao mais antigo (DESC).
        """
        from sqlalchemy import case
        if ref_now is None:
            from utils.dates import get_current_datetime
            ref_now = get_current_datetime()

        order_group = case((cls.data_inicio >= ref_now, 0), else_=1).asc()
        order_future = case((cls.data_inicio >= ref_now, cls.data_inicio), else_=None).asc()
        order_past = case((cls.data_inicio < ref_now, cls.data_inicio), else_=None).desc()

        return (order_group, order_future, order_past)
