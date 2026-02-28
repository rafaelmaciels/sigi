from datetime import datetime
from app.extensions import db

class Igreja(db.Model):
    __tablename__ = "igreja"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    site = db.Column(db.String(120))
    pastor_responsavel = db.Column(db.String(120))
    ano_fundacao = db.Column(db.Integer)
    versiculo_tema = db.Column(db.String(250))

    atualizado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True
    )

    def __repr__(self):
        return f"<Igreja {self.nome}>"
