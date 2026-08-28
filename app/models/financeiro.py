from datetime import datetime, timezone
from app.extensions import db

# -----------------------------
# 💰 Constantes Eclesiásticas Evangélicas
# -----------------------------
TIPOS_FINANCEIRO = ("Entrada", "Saída")

CATEGORIAS_RECEITAS_PADRAO = [
    "Dízimos",
    "Ofertas de Culto",
    "Ofertas de Missões",
    "Ofertas de Construção / Reforma",
    "Ofertas Alçadas / Votos",
    "Vendas da Cantina / Livraria",
    "Inscrições de Retiros / Congressos",
    "Ação Social (Doações Recebidas)",
    "Rendimentos / Outras Receitas"
]

CATEGORIAS_DESPESAS_PADRAO = [
    "Prebenda / Sustento Pastoral",
    "Ajudas de Custo / Diárias",
    "Manutenção do Templo e Estrutura",
    "Contas de Consumo (Água, Luz, Internet)",
    "Aluguel do Templo / Imóveis",
    "Ação Social / Diaconia / Cestas Básicas",
    "Missões / Sustento Missionário",
    "Escola Bíblica Dominical (EBD) / Didáticos",
    "Ministério de Louvor / Instrumentos / Som",
    "Comunicação, Mídia e Transmissão",
    "Ministério Infantil / Crianças",
    "Departamentos (Jovens, Mulheres, Homens)",
    "Retiros, Congressos e Festividades",
    "Impostos, INSS e Encargos",
    "Tarifas e Taxas Bancárias",
    "Outras Despesas"
]

DEPARTAMENTOS_PADRAO = [
    "Templo / Geral",
    "Secretaria & Administração",
    "Ministério Pastoral",
    "Missões & Evangelismo",
    "Ação Social & Diaconia",
    "Escola Bíblica (EBD)",
    "Louvor & Multimídia",
    "Ministério Infantil",
    "Jovens & Adolescentes",
    "Mulheres",
    "Homens",
    "Obras & Patrimônio"
]

CONTAS_PADRAO = [
    "Caixa Geral (Espécie)",
    "Conta Corrente Principal",
    "Chave PIX Oficial",
    "Fundo de Missões",
    "Fundo de Construção / Reforma",
    "Fundo de Ação Social",
    "Poupança / Aplicações",
    "Outra Conta"
]

FORMAS_PAGAMENTO_PADRAO = [
    "PIX",
    "Dinheiro (Espécie)",
    "Cartão de Débito",
    "Cartão de Crédito",
    "Transferência Bancária (TED/DOC)",
    "Boleto",
    "Cheque"
]

class Financeiro(db.Model):
    __tablename__ = "financeiro"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    tipo = db.Column(db.String(20), nullable=False)  # Entrada / Saída
    categoria = db.Column(db.String(100), nullable=False)
    conta = db.Column(db.String(100), nullable=False, default="Caixa Geral (Espécie)")
    departamento = db.Column(db.String(100), nullable=False, default="Templo / Geral")
    forma_pagamento = db.Column(db.String(50), nullable=False, default="Dinheiro (Espécie)")

    descricao = db.Column(db.String(200))
    observacoes = db.Column(db.Text, nullable=True)

    # Vínculo eclesiástico (Membro dizimista / contribuinte)
    membro_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)
    membro = db.relationship('Member', backref=db.backref('lancamentos_financeiros', lazy=True))

    cpf_membro = db.Column(db.String(14))
    cnpj_fornecedor = db.Column(db.String(18))

    conciliado = db.Column(db.Boolean, default=False)
    comprovante = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Usuário do sistema que realizou o lançamento
    usuario = db.Column(db.String(100))

    def __init__(self, **kwargs):
        tipo = kwargs.get("tipo")
        if tipo not in TIPOS_FINANCEIRO:
            raise ValueError("Tipo deve ser 'Entrada' ou 'Saída'")
        super().__init__(**kwargs)

    @property
    def nome_identificador(self):
        """Retorna o nome do membro vinculado, se houver, ou a descrição do lançamento."""
        if self.membro:
            return self.membro.nome
        return self.descricao or self.categoria

    def __repr__(self):
        data_str = self.data.strftime('%d/%m/%Y') if self.data else "sem data"
        return f"<Financeiro {self.tipo} {self.categoria} R${self.valor:.2f} em {data_str}>"
