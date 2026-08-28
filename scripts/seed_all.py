#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Script Geral de Povoamento de Dados (Seed Master)
Popula todo o sistema com dados demonstrativos completos e realistas:
1. Dados da Igreja Sede
2. Membros, Oficiais e Visitantes
3. Patrimônio e Bens
4. Escola Bíblica Dominical (EBD)
5. Eventos, Cultos, Atas, Cartas e Certificados
6. Lançamentos Financeiros (Receitas e Despesas de 2025/2026)
"""

import os
import sys
import importlib.util
from pathlib import Path
from datetime import datetime, date, timedelta
import random

# Ajusta path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import Igreja, Member, User, Evento, Ata, Carta, Certificado, Patrimonio

app = create_app()

def seed_igreja():
    print("🏛️ [1/6] Configurando Dados da Igreja Sede...")
    igreja = Igreja.query.first()
    if not igreja:
        igreja = Igreja(
            nome="Igreja Evangélica Comunidade da Graça — Sede",
            cnpj="12.345.678/0001-90",
            endereco="Av. das Nações Unidas, 1500 - Centro, São Paulo/SP",
            telefone="(11) 98765-4321",
            email="contato@comunidadedagraca.org.br",
            site="https://comunidadedagraca.org.br",
            pastor_responsavel="Pr. Carlos Eduardo da Silva",
            ano_fundacao=1998,
            versiculo_tema="Porque dEle, por Ele e para Ele são todas as coisas. (Romanos 11:36)"
        )
        db.session.add(igreja)
    else:
        igreja.nome = "Igreja Evangélica Comunidade da Graça — Sede"
        igreja.pastor_responsavel = "Pr. Carlos Eduardo da Silva"
        igreja.versiculo_tema = "Porque dEle, por Ele e para Ele são todas as coisas. (Romanos 11:36)"
    db.session.commit()
    print("  ✅ Dados da Igreja configurados.")

def seed_membros():
    print("👥 [2/6] Cadastrando Membros, Oficiais e Visitantes...")
    
    membros_base = [
        # Liderança Pastoral e Diaconal
        {"nome": "Pr. Carlos Eduardo da Silva", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Pra. Helena Silva", "telefone": "(11) 98111-1001", "email": "pastorcarlos@sigi.local", "funcao": "Pastor Titular", "dizimista": True, "batizado": True, "data_nascimento": date(1975, 4, 12), "data_batismo": date(1992, 10, 15), "visitante": False},
        {"nome": "Pra. Helena Beatriz Silva", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Pr. Carlos Eduardo da Silva", "telefone": "(11) 98111-1002", "email": "pastorahelena@sigi.local", "funcao": "Pastora Auxiliar", "dizimista": True, "batizado": True, "data_nascimento": date(1978, 8, 24), "data_batismo": date(1995, 6, 20), "visitante": False},
        {"nome": "Presb. Marcos Roberto Santos", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Débora Santos", "telefone": "(11) 98222-2001", "email": "marcos.santos@gmail.com", "funcao": "Presbítero", "dizimista": True, "batizado": True, "data_nascimento": date(1980, 2, 10), "data_batismo": date(2000, 3, 12), "visitante": False},
        {"nome": "Diác. André Luiz Ferreira", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Mariana Ferreira", "telefone": "(11) 98333-3001", "email": "andre.ferreira@hotmail.com", "funcao": "Diácono", "dizimista": True, "batizado": True, "data_nascimento": date(1985, 11, 5), "data_batismo": date(2005, 11, 20), "visitante": False},
        {"nome": "Diác. Juliana Souza Mendes", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98333-3002", "email": "juliana.mendes@gmail.com", "funcao": "Diaconisa", "dizimista": True, "batizado": True, "data_nascimento": date(1990, 7, 18), "data_batismo": date(2010, 4, 15), "visitante": False},
        
        # Professores e Líderes
        {"nome": "Prof. Roberto Albuquerque", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Renata Albuquerque", "telefone": "(11) 98444-4001", "email": "roberto.ebd@sigi.local", "funcao": "Professor EBD", "dizimista": True, "batizado": True, "data_nascimento": date(1982, 9, 14), "data_batismo": date(1998, 8, 10), "visitante": False},
        {"nome": "Profa. Amanda Lima Rocha", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Lucas Rocha", "telefone": "(11) 98444-4002", "email": "amanda.rocha@yahoo.com", "funcao": "Professora Infantil", "dizimista": True, "batizado": True, "data_nascimento": date(1992, 3, 29), "data_batismo": date(2012, 12, 16), "visitante": False},
        {"nome": "Gabriel Tavares Castro", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98555-5001", "email": "gabriel.jovens@gmail.com", "funcao": "Líder de Jovens", "dizimista": True, "batizado": True, "data_nascimento": date(2001, 5, 20), "data_batismo": date(2018, 10, 28), "visitante": False},
        {"nome": "Beatriz Martins Oliveira", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98555-5002", "email": "bia.louvor@gmail.com", "funcao": "Líder de Louvor", "dizimista": True, "batizado": True, "data_nascimento": date(1999, 12, 3), "data_batismo": date(2016, 7, 24), "visitante": False},

        # Membros da Congregação
        {"nome": "Antônio Carlos de Almeida", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Maria Aparecida Almeida", "telefone": "(11) 98666-6001", "email": "antonio.almeida@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(1968, 6, 15), "data_batismo": date(1989, 5, 14), "visitante": False},
        {"nome": "Maria Aparecida Almeida", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Antônio Carlos de Almeida", "telefone": "(11) 98666-6002", "email": "maria.aparecida@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(1971, 10, 8), "data_batismo": date(1990, 4, 22), "visitante": False},
        {"nome": "Lucas Barbosa Ramos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98777-7001", "email": "lucas.ramos98@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(1998, 1, 25), "data_batismo": date(2017, 9, 10), "visitante": False},
        {"nome": "Fernanda Ribeiro Costa", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Thiago Costa", "telefone": "(11) 98777-7002", "email": "fernanda.costa@hotmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(1988, 11, 30), "data_batismo": date(2008, 11, 23), "visitante": False},
        {"nome": "Thiago Monteiro Costa", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Fernanda Ribeiro Costa", "telefone": "(11) 98777-7003", "email": "thiago.monteiro@hotmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(1986, 4, 17), "data_batismo": date(2006, 8, 13), "visitante": False},
        {"nome": "Larissa Gomes Peixoto", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98888-8001", "email": "larissa.peixoto@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "data_nascimento": date(2003, 7, 12), "data_batismo": date(2021, 6, 27), "visitante": False},
        {"nome": "Matheus Henrique Dias", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98888-8002", "email": "matheus.dias@gmail.com", "funcao": "Membro", "dizimista": False, "batizado": True, "data_nascimento": date(2005, 3, 19), "data_batismo": date(2023, 12, 10), "visitante": False},
        
        # Crianças e Adolescentes (EBD)
        {"nome": "Davi Silva Santos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98222-2001", "email": "", "funcao": "Criança / EBD", "dizimista": False, "batizado": False, "data_nascimento": date(2016, 9, 8), "data_batismo": None, "visitante": False},
        {"nome": "Sarah Albuquerque Mendes", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98444-4001", "email": "", "funcao": "Criança / EBD", "dizimista": False, "batizado": False, "data_nascimento": date(2018, 4, 15), "data_batismo": None, "visitante": False},
        {"nome": "Samuel Costa Ramos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98777-7002", "email": "", "funcao": "Adolescente", "dizimista": False, "batizado": False, "data_nascimento": date(2012, 11, 2), "data_batismo": None, "visitante": False},

        # Visitantes
        {"nome": "Julio Cesar Brandão", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Renata Brandão", "telefone": "(11) 99123-4567", "email": "julio.brandao@outlook.com", "funcao": "Visitante", "dizimista": False, "batizado": False, "data_nascimento": date(1984, 8, 22), "data_batismo": None, "visitante": True},
        {"nome": "Camila Vasconcelos", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 99876-5432", "email": "camila.vasconcelos@gmail.com", "funcao": "Visitante", "dizimista": False, "batizado": False, "data_nascimento": date(1997, 5, 14), "data_batismo": None, "visitante": True}
    ]

    for m_data in membros_base:
        m = Member.query.filter_by(nome=m_data["nome"]).first()
        if not m:
            m = Member(
                nome=m_data["nome"],
                sexo=m_data["sexo"],
                estado_civil=m_data["estado_civil"],
                conjuge=m_data["conjuge"],
                telefone=m_data["telefone"],
                email=m_data["email"],
                funcao=m_data["funcao"],
                dizimista=m_data["dizimista"],
                batizado=m_data["batizado"],
                data_nascimento=m_data["data_nascimento"],
                data_batismo=m_data["data_batismo"],
                data_cadastro=date(2025, 1, 10),
                status="ativo",
                endereco="Rua das Acácias, 120",
                bairro="Jardim Esperança",
                cep="01310-100",
                igreja_local="Sede",
                visitante=m_data["visitante"]
            )
            db.session.add(m)
    db.session.commit()
    print(f"  ✅ {len(membros_base)} membros e visitantes cadastrados com sucesso.")

def rodar_modulo(caminho_script):
    spec = importlib.util.spec_from_file_location("modulo_seed", str(caminho_script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "seed_ebd"):
        mod.seed_ebd()
    elif hasattr(mod, "main"):
        mod.main()

def main():
    print("\n" + "=" * 70)
    print("  🌱 SIGI — POVOAMENTO COMPLETO DA BASE DE DADOS")
    print("=" * 70 + "\n")
    
    with app.app_context():
        # Garante criação de todas as tabelas
        db.create_all()
        seed_igreja()
        seed_membros()

    print("🏛️ [3/6] Povoando Gestão de Patrimônio e Bens...")
    rodar_modulo(BASE_DIR / "scripts" / "seed_patrimonio.py")

    print("📖 [4/6] Povoando Escola Bíblica Dominical (EBD)...")
    rodar_modulo(BASE_DIR / "scripts" / "seed_ebd.py")

    print("📅 [5/6] Povoando Calendário de Eventos, Atas, Cartas e Certificados...")
    rodar_modulo(BASE_DIR / "scripts" / "seed_documentos_eventos.py")

    print("💰 [6/6] Povoando Módulo Financeiro (Dízimos, Ofertas e Despesas)...")
    rodar_modulo(BASE_DIR / "scripts" / "seed_financeiro.py")

    print("\n" + "=" * 70)
    print("  🎉 BASE DE DADOS POVOADA COM SUCESSO!")
    print("  Todos os módulos agora contêm dados realistas para demonstração e uso.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
