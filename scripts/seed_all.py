#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Script Geral de Povoamento de Dados (Seed Master)
Popula todo o sistema com dados demonstrativos completos e realistas:
1. Dados da Igreja Sede
2. Membros, Oficiais, Crianças, Jovens e Visitantes (Crescimento Natural da Igreja 2025-2026)
3. Escola Bíblica Dominical (EBD - Classes, Professores, Matrículas, Aulas, Frequências)
4. Gestão de Patrimônio e Bens
5. Calendário de Eventos, Atas de Assembleia, Cartas Pastorais e Certificados
6. Lançamentos Financeiros (Fluxo de Caixa 2025-2026)
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
from app.models.ebd import EbdConfig, EbdPeriodo, EbdClasse, EbdProfessor, EbdMatricula, EbdAula, EbdFrequencia
from app.models.financeiro import Financeiro

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
    print("  ✅ Dados da Igreja configurados com sucesso.")

def seed_membros():
    print("👥 [2/6] Cadastrando Membros, Oficiais, Crianças, Jovens e Visitantes...")
    
    # Limpa membros para garantir histórico consistente de crescimento
    Member.query.delete()
    db.session.commit()

    membros_completos = [
        # Liderança Pastoral e Diaconal
        {"nome": "Pr. Carlos Eduardo da Silva", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Pra. Helena Silva", "telefone": "(11) 98111-1001", "email": "pastorcarlos@sigi.local", "funcao": "Pastor Titular", "dizimista": True, "batizado": True, "nasc": date(1975, 4, 12), "batismo": date(1992, 10, 15), "cad": date(2025, 1, 5), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Pra. Helena Beatriz Silva", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Pr. Carlos Eduardo da Silva", "telefone": "(11) 98111-1002", "email": "pastorahelena@sigi.local", "funcao": "Pastora Auxiliar", "dizimista": True, "batizado": True, "nasc": date(1978, 8, 24), "batismo": date(1995, 6, 20), "cad": date(2025, 1, 5), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Presb. Marcos Roberto Santos", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Débora Santos", "telefone": "(11) 98222-2001", "email": "marcos.santos@gmail.com", "funcao": "Presbítero", "dizimista": True, "batizado": True, "nasc": date(1980, 2, 10), "batismo": date(2000, 3, 12), "cad": date(2025, 1, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Diác. André Luiz Ferreira", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Mariana Ferreira", "telefone": "(11) 98333-3001", "email": "andre.ferreira@hotmail.com", "funcao": "Diácono", "dizimista": True, "batizado": True, "nasc": date(1985, 11, 5), "batismo": date(2005, 11, 20), "cad": date(2025, 1, 15), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Diác. Juliana Souza Mendes", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98333-3002", "email": "juliana.mendes@gmail.com", "funcao": "Diaconisa", "dizimista": True, "batizado": True, "nasc": date(1990, 7, 18), "batismo": date(2010, 4, 15), "cad": date(2025, 1, 20), "saida": None, "status": "ativo", "vis": False},

        # Professores e Líderes
        {"nome": "Prof. Roberto Albuquerque", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Renata Albuquerque", "telefone": "(11) 98444-4001", "email": "roberto.ebd@sigi.local", "funcao": "Professor EBD", "dizimista": True, "batizado": True, "nasc": date(1982, 9, 14), "batismo": date(1998, 8, 10), "cad": date(2025, 2, 8), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Profa. Amanda Lima Rocha", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Lucas Rocha", "telefone": "(11) 98444-4002", "email": "amanda.rocha@yahoo.com", "funcao": "Professora Infantil", "dizimista": True, "batizado": True, "nasc": date(1992, 3, 29), "batismo": date(2012, 12, 16), "cad": date(2025, 2, 15), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Gabriel Tavares Castro", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98555-5001", "email": "gabriel.jovens@gmail.com", "funcao": "Líder de Jovens", "dizimista": True, "batizado": True, "nasc": date(2001, 5, 20), "batismo": date(2018, 10, 28), "cad": date(2025, 2, 22), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Beatriz Martins Oliveira", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98555-5002", "email": "bia.louvor@gmail.com", "funcao": "Líder de Louvor", "dizimista": True, "batizado": True, "nasc": date(1999, 12, 3), "batismo": date(2016, 7, 24), "cad": date(2025, 3, 5), "saida": None, "status": "ativo", "vis": False},

        # Adultos e Famílias (Entradas distribuídas ao longo de 2025)
        {"nome": "Antônio Carlos de Almeida", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Maria Aparecida Almeida", "telefone": "(11) 98666-6001", "email": "antonio.almeida@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1968, 6, 15), "batismo": date(1989, 5, 14), "cad": date(2025, 3, 18), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Maria Aparecida Almeida", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Antônio Carlos de Almeida", "telefone": "(11) 98666-6002", "email": "maria.aparecida@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1971, 10, 8), "batismo": date(1990, 4, 22), "cad": date(2025, 3, 18), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Lucas Barbosa Ramos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98777-7001", "email": "lucas.ramos98@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1998, 1, 25), "batismo": date(2017, 9, 10), "cad": date(2025, 4, 12), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Fernanda Ribeiro Costa", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Thiago Costa", "telefone": "(11) 98777-7002", "email": "fernanda.costa@hotmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1988, 11, 30), "batismo": date(2008, 11, 23), "cad": date(2025, 4, 25), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Thiago Monteiro Costa", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Fernanda Ribeiro Costa", "telefone": "(11) 98777-7003", "email": "thiago.monteiro@hotmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1986, 4, 17), "batismo": date(2006, 8, 13), "cad": date(2025, 4, 25), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Larissa Gomes Peixoto", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98888-8001", "email": "larissa.peixoto@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(2003, 7, 12), "batismo": date(2021, 6, 27), "cad": date(2025, 5, 14), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Matheus Henrique Dias", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98888-8002", "email": "matheus.dias@gmail.com", "funcao": "Membro", "dizimista": False, "batizado": True, "nasc": date(2005, 3, 19), "batismo": date(2023, 12, 10), "cad": date(2025, 5, 29), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Paulo Sérgio Guimarães", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Sônia Guimarães", "telefone": "(11) 98999-1001", "email": "paulo.guimaraes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1964, 8, 19), "batismo": date(1985, 3, 10), "cad": date(2025, 6, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Sônia Regina Guimarães", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Paulo Sérgio Guimarães", "telefone": "(11) 98999-1002", "email": "sonia.guimaraes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1967, 1, 30), "batismo": date(1987, 7, 15), "cad": date(2025, 6, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Eduardo Cavalcanti", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98999-2001", "email": "edu.cavalcanti@terra.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1993, 10, 5), "batismo": date(2014, 5, 18), "cad": date(2025, 7, 15), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Priscila Nogueira", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98999-2002", "email": "pri.nogueira@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1995, 6, 12), "batismo": date(2015, 9, 20), "cad": date(2025, 8, 20), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Rodrigo Valente", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Flávia Valente", "telefone": "(11) 98999-3001", "email": "rodrigo.valente@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1981, 12, 1), "batismo": date(2002, 4, 14), "cad": date(2025, 9, 12), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Flávia Valente", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Rodrigo Valente", "telefone": "(11) 98999-3002", "email": "flavia.valente@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1983, 5, 18), "batismo": date(2004, 10, 22), "cad": date(2025, 9, 12), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Vitor Hugo Silveira", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98999-4001", "email": "vitor.silveira@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(2000, 2, 14), "batismo": date(2019, 11, 17), "cad": date(2025, 10, 8), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Cláudia Meireles", "sexo": "Feminino", "estado_civil": "Divorciada", "conjuge": "", "telefone": "(11) 98999-5001", "email": "claudia.meireles@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1974, 9, 27), "batismo": date(1996, 8, 11), "cad": date(2025, 11, 18), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Leandro Barreto", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98999-6001", "email": "leandro.barreto@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1996, 4, 3), "batismo": date(2016, 12, 18), "cad": date(2025, 12, 10), "saida": None, "status": "ativo", "vis": False},

        # Entradas em 2026 (Janeiro a Agosto de 2026)
        {"nome": "Guilherme Siqueira", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Tatiane Siqueira", "telefone": "(11) 97111-1001", "email": "gui.siqueira@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1989, 7, 21), "batismo": date(2010, 6, 13), "cad": date(2026, 1, 14), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Tatiane Siqueira", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Guilherme Siqueira", "telefone": "(11) 97111-1002", "email": "tati.siqueira@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1991, 11, 15), "batismo": date(2011, 8, 21), "cad": date(2026, 1, 14), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Felipe Augusto Fonseca", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 97222-2001", "email": "felipe.fonseca@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(2002, 8, 9), "batismo": date(2022, 10, 16), "cad": date(2026, 2, 18), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Renata Antunes", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 97333-3001", "email": "renata.antunes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1994, 3, 17), "batismo": date(2015, 4, 12), "cad": date(2026, 3, 22), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Alexandre Pires Moraes", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Bárbara Moraes", "telefone": "(11) 97444-4001", "email": "alex.moraes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1987, 12, 28), "batismo": date(2007, 7, 8), "cad": date(2026, 4, 19), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Bárbara Moraes", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Alexandre Pires Moraes", "telefone": "(11) 97444-4002", "email": "barbara.moraes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1989, 9, 4), "batismo": date(2009, 10, 18), "cad": date(2026, 4, 19), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Danilo Fagundes", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 97555-5001", "email": "danilo.fagundes@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(2004, 1, 11), "batismo": date(2024, 6, 23), "cad": date(2026, 5, 25), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Letícia Camargo", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 97666-6001", "email": "leticia.camargo@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1997, 8, 30), "batismo": date(2018, 5, 20), "cad": date(2026, 6, 16), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Gustavo Peçanha", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 97777-7001", "email": "gustavo.pecanha@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(2001, 10, 14), "batismo": date(2020, 11, 15), "cad": date(2026, 7, 20), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Aline Medeiros", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 97888-8001", "email": "aline.medeiros@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1998, 4, 26), "batismo": date(2017, 8, 13), "cad": date(2026, 8, 12), "saida": None, "status": "ativo", "vis": False},

        # Crianças (Maternal / Primários - EBD)
        {"nome": "Davi Silva Santos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98222-2001", "email": "", "funcao": "Criança / EBD", "dizimista": False, "batizado": False, "nasc": date(2021, 9, 8), "batismo": None, "cad": date(2025, 2, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Sarah Albuquerque", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98444-4001", "email": "", "funcao": "Criança / EBD", "dizimista": False, "batizado": False, "nasc": date(2022, 4, 15), "batismo": None, "cad": date(2025, 3, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Enzo Gabriel Rocha", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98444-4002", "email": "", "funcao": "Criança / EBD", "dizimista": False, "batizado": False, "nasc": date(2020, 11, 20), "batismo": None, "cad": date(2025, 3, 15), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Manuela Costa", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98777-7002", "email": "", "funcao": "Primários / EBD", "dizimista": False, "batizado": False, "nasc": date(2017, 6, 14), "batismo": None, "cad": date(2025, 4, 25), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Pedro Henrique Valente", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98999-3001", "email": "", "funcao": "Primários / EBD", "dizimista": False, "batizado": False, "nasc": date(2016, 2, 28), "batismo": None, "cad": date(2025, 9, 12), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Heloísa Siqueira", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 97111-1001", "email": "", "funcao": "Primários / EBD", "dizimista": False, "batizado": False, "nasc": date(2018, 10, 5), "batismo": None, "cad": date(2026, 1, 14), "saida": None, "status": "ativo", "vis": False},

        # Adolescentes (EBD)
        {"nome": "Samuel Costa Ramos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98777-7002", "email": "samuel.costa@gmail.com", "funcao": "Adolescente", "dizimista": False, "batizado": False, "nasc": date(2012, 11, 2), "batismo": None, "cad": date(2025, 4, 25), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Isabela Guimarães", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 98999-1001", "email": "isabela.guimaraes@gmail.com", "funcao": "Adolescente", "dizimista": False, "batizado": False, "nasc": date(2010, 8, 17), "batismo": None, "cad": date(2025, 6, 10), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Lucas Gabriel Meireles", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 98999-5001", "email": "lucas.meireles@gmail.com", "funcao": "Adolescente", "dizimista": False, "batizado": False, "nasc": date(2011, 5, 23), "batismo": None, "cad": date(2025, 11, 18), "saida": None, "status": "ativo", "vis": False},
        {"nome": "Rebeca Moraes", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 97444-4001", "email": "rebeca.moraes@gmail.com", "funcao": "Adolescente", "dizimista": False, "batizado": False, "nasc": date(2013, 1, 30), "batismo": None, "cad": date(2026, 4, 19), "saida": None, "status": "ativo", "vis": False},

        # Membros com Saída Registrada (Transferências / Mudança de Cidade para cálculo de saídas no gráfico)
        {"nome": "Marcelo Dantas", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Márcia Dantas", "telefone": "(11) 96111-1001", "email": "marcelo.dantas@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1979, 3, 14), "batismo": date(1999, 5, 10), "cad": date(2025, 1, 10), "saida": date(2025, 6, 30), "status": "inativo", "vis": False},
        {"nome": "Márcia Dantas", "sexo": "Feminino", "estado_civil": "Casada", "conjuge": "Marcelo Dantas", "telefone": "(11) 96111-1002", "email": "marcia.dantas@uol.com.br", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1982, 7, 20), "batismo": date(2001, 8, 15), "cad": date(2025, 1, 10), "saida": date(2025, 6, 30), "status": "inativo", "vis": False},
        {"nome": "Jorge Bastos", "sexo": "Masculino", "estado_civil": "Solteiro", "conjuge": "", "telefone": "(11) 96222-2001", "email": "jorge.bastos@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1992, 11, 4), "batismo": date(2013, 9, 22), "cad": date(2025, 3, 15), "saida": date(2025, 11, 20), "status": "inativo", "vis": False},
        {"nome": "Renata Vilela", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 96333-3001", "email": "renata.vilela@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1996, 6, 19), "batismo": date(2017, 10, 15), "cad": date(2025, 5, 10), "saida": date(2026, 3, 31), "status": "inativo", "vis": False},
        {"nome": "Cláudio Mendonça", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Denise Mendonça", "telefone": "(11) 96444-4001", "email": "claudio.mendonca@gmail.com", "funcao": "Membro", "dizimista": True, "batizado": True, "nasc": date(1973, 10, 12), "batismo": date(1994, 4, 18), "cad": date(2025, 2, 20), "saida": date(2026, 7, 15), "status": "inativo", "vis": False},

        # Visitantes
        {"nome": "Julio Cesar Brandão", "sexo": "Masculino", "estado_civil": "Casado", "conjuge": "Renata Brandão", "telefone": "(11) 99123-4567", "email": "julio.brandao@outlook.com", "funcao": "Visitante", "dizimista": False, "batizado": False, "nasc": date(1984, 8, 22), "batismo": None, "cad": date(2026, 8, 10), "saida": None, "status": "ativo", "vis": True},
        {"nome": "Camila Vasconcelos", "sexo": "Feminino", "estado_civil": "Solteira", "conjuge": "", "telefone": "(11) 99876-5432", "email": "camila.vasconcelos@gmail.com", "funcao": "Visitante", "dizimista": False, "batizado": False, "nasc": date(1997, 5, 14), "batismo": None, "cad": date(2026, 8, 17), "saida": None, "status": "ativo", "vis": True}
    ]

    for m_data in membros_completos:
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
            data_nascimento=m_data["nasc"],
            data_batismo=m_data["batismo"],
            data_cadastro=m_data["cad"],
            data_saida=m_data["saida"],
            status=m_data["status"],
            endereco="Rua das Acácias, 120",
            bairro="Jardim Esperança",
            cep="01310-100",
            igreja_local="Sede Central",
            visitante=m_data["vis"]
        )
        db.session.add(m)
    
    db.session.commit()
    print(f"  ✅ {len(membros_completos)} membros, oficiais e visitantes cadastrados com histórico 2025/2026.")

def seed_ebd():
    print("📖 [3/6] Povoando Escola Bíblica Dominical (EBD)...")
    from scripts.seed_ebd import seed_ebd as run_ebd_seed
    run_ebd_seed()

def seed_patrimonio():
    print("🏛️ [4/6] Povoando Gestão de Patrimônio e Bens...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed_pat", str(BASE_DIR / "scripts" / "seed_patrimonio.py"))
    pat_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pat_mod)

def seed_documentos_eventos():
    print("📅 [5/6] Povoando Calendário de Eventos, Atas, Cartas e Certificados...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed_doc", str(BASE_DIR / "scripts" / "seed_documentos_eventos.py"))
    doc_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(doc_mod)

def seed_financeiro():
    print("💰 [6/6] Povoando Módulo Financeiro (Dízimos, Ofertas e Despesas)...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed_fin", str(BASE_DIR / "scripts" / "seed_financeiro.py"))
    fin_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fin_mod)

def main():
    print("\n" + "=" * 70)
    print("  🌱 SIGI — POVOAMENTO COMPLETO DA BASE DE DADOS")
    print("=" * 70 + "\n")
    
    with app.app_context():
        db.create_all()
        seed_igreja()
        seed_membros()
        seed_ebd()
        seed_patrimonio()
        seed_documentos_eventos()
        seed_financeiro()

    print("\n" + "=" * 70)
    print("  🎉 BASE DE DADOS POVOADA COM 100% DE SUCESSO!")
    print("  Todos os módulos, gráficos e relatórios agora contêm dados realistas.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
