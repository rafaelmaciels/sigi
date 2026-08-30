#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Povoamento/Configuração dos Dados da Igreja Sede
Garante que a tabela exista e cria/atualiza os dados institucionais da Igreja Sede.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Igreja

def seed_dados_igreja():
    app = create_app()
    with app.app_context():
        db.create_all()
        igreja = Igreja.query.first()
        if not igreja:
            print("Criando dados institucionais padrão da Igreja Sede...")
            igreja = Igreja(
                nome="Igreja Evangélica Comunidade da Graça — Sede",
                cnpj="12.345.678/0001-90",
                endereco="Av. Principal, 1000 - Centro, São Paulo - SP, CEP 01000-000",
                telefone="(11) 3333-4444",
                email="contato@igrejadagraca.com.br",
                site="www.igrejadagraca.com.br",
                pastor_responsavel="Pr. Carlos Eduardo da Silva",
                ano_fundacao=1995,
                versiculo_tema="Porque dEle, por Ele e para Ele são todas as coisas. (Romanos 11:36)"
            )
            db.session.add(igreja)
            db.session.commit()
            print("[OK] Dados da Igreja cadastrados com sucesso no banco de dados!")
        else:
            print(f"[OK] Dados da Igreja ja existentes: {igreja.nome}")

if __name__ == "__main__":
    seed_dados_igreja()
