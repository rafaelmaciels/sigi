#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌱 SiGI — Script de Povoamento Completo da Escola Bíblica Dominical (EBD)
Gera:
- Configuração Geral da EBD
- Períodos Letivos (1º, 2º e 3º Trimestre 2026)
- 5 Classes com salas, capacidades e faixas etárias
- Professores vinculados (titulares e auxiliares)
- Matrículas por faixa etária
- Aulas dos domingos com temas e resumos de lições
- Registros de presença / falta / justificativa e visitantes (Mapa de Frequência)
"""

import sys
import os
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import Member
from app.models.ebd import EbdConfig, EbdPeriodo, EbdClasse, EbdProfessor, EbdMatricula, EbdAula, EbdFrequencia

app = create_app()

def seed_ebd():
    with app.app_context():
        print("🌱 [EBD] Iniciando povoamento completo da Escola Bíblica Dominical...")

        # Limpa dados anteriores da EBD para inserção limpa e íntegra
        EbdFrequencia.query.delete()
        EbdAula.query.delete()
        EbdMatricula.query.delete()
        EbdProfessor.query.delete()
        EbdClasse.query.delete()
        EbdPeriodo.query.delete()
        db.session.commit()

        # 1. Configuração Geral da EBD
        pastor = Member.query.filter(Member.funcao.ilike("%pastor%")).first() or Member.query.first()
        config = EbdConfig.query.first()
        if not config:
            config = EbdConfig(
                nome="Escola Bíblica Dominical — Sede Central",
                descricao="Departamento de Ensino Bíblico, Discipulado e Formação Cristã Contínua",
                dia_semana="Domingo",
                horario_inicio="09:00",
                horario_termino="10:30",
                coordenador_id=pastor.id if pastor else None,
                ativo=True
            )
            db.session.add(config)
        else:
            config.nome = "Escola Bíblica Dominical — Sede Central"
            config.coordenador_id = pastor.id if pastor else None
            config.ativo = True
        
        db.session.commit()
        print("  ✅ Configuração Geral da EBD salva.")

        # 2. Períodos Letivos de 2026
        p1 = EbdPeriodo(
            nome="1º Trimestre 2026 - O Caráter de Cristo",
            data_inicio=date(2026, 1, 4),
            data_fim=date(2026, 3, 29),
            status="encerrado",
            observacoes="Estudo das bem-aventuranças e das virtudes do Fruto do Espírito."
        )
        db.session.add(p1)

        p2 = EbdPeriodo(
            nome="2º Trimestre 2026 - A Igreja e sua Missão",
            data_inicio=date(2026, 4, 5),
            data_fim=date(2026, 6, 28),
            status="encerrado",
            observacoes="Missiologia bíblica e a história do livro de Atos dos Apóstolos."
        )
        db.session.add(p2)

        p3 = EbdPeriodo(
            nome="3º Trimestre 2026 - As Parábolas de Jesus",
            data_inicio=date(2026, 7, 5),
            data_fim=date(2026, 9, 27),
            status="em_andamento",
            observacoes="Lições práticas sobre os mistérios e princípios do Reino de Deus."
        )
        db.session.add(p3)
        db.session.commit()
        print("  ✅ 3 Períodos letivos cadastrados (1º e 2º encerrados, 3º em andamento).")

        # 3. 5 Classes com Salas e Faixas Etárias
        classes_data = [
            {
                "nome": "Maternal & Jardim — Pequenos de Jesus",
                "faixa_etaria": "3 a 6 anos",
                "sala": "Sala 01 (Espaço Infantil)",
                "capacidade": 20,
                "descricao": "Histórias bíblicas ilustradas, cânticos e atividades lúdicas de fé.",
                "idade_min": 0, "idade_max": 6
            },
            {
                "nome": "Primários & Juniores — Heróis da Fé",
                "faixa_etaria": "7 a 11 anos",
                "sala": "Sala 02 (1º Andar)",
                "capacidade": 25,
                "descricao": "Memorização de versículos, biografias bíblicas e fundamentos morais.",
                "idade_min": 7, "idade_max": 11
            },
            {
                "nome": "Adolescentes — Conectados com Deus",
                "faixa_etaria": "12 a 17 anos",
                "sala": "Sala 03 (Anexo Jovem)",
                "capacidade": 30,
                "descricao": "Desafios da juventude, identidade cristã e princípios para o dia a dia.",
                "idade_min": 12, "idade_max": 17
            },
            {
                "nome": "Jovens — Geração Forte",
                "faixa_etaria": "18 a 35 anos",
                "sala": "Auditório 2",
                "capacidade": 45,
                "descricao": "Vida universitária, vocação, relacionamentos bíblicos e maturidade espiritual.",
                "idade_min": 18, "idade_max": 35
            },
            {
                "nome": "Adultos — Maturidade Cristã",
                "faixa_etaria": "36 anos em diante",
                "sala": "Nave Principal",
                "capacidade": 120,
                "descricao": "Estudo aprofundado das Escrituras, família cristã e liderança servidora.",
                "idade_min": 36, "idade_max": 120
            }
        ]

        classes_criadas = []
        for cd in classes_data:
            c = EbdClasse(
                nome=cd["nome"],
                periodo_id=p3.id,
                faixa_etaria=cd["faixa_etaria"],
                sala=cd["sala"],
                capacidade=cd["capacidade"],
                status="ativa",
                descricao=cd["descricao"]
            )
            db.session.add(c)
            db.session.flush()
            classes_criadas.append((c, cd))

        db.session.commit()
        print(f"  ✅ {len(classes_criadas)} classes ativas cadastradas com salas e capacidades.")

        # 4. Vincular Professores
        membros_todos = Member.query.filter(Member.status.ilike("ativo")).all()
        if not membros_todos:
            membros_todos = Member.query.all()

        professores_candidatos = [m for m in membros_todos if any(kw in (m.funcao or "").lower() for kw in ["professor", "pastor", "presb", "diác", "líder"])]
        if len(professores_candidatos) < 5:
            professores_candidatos = membros_todos[:5]

        for i, (c, _) in enumerate(classes_criadas):
            prof_titular = professores_candidatos[i % len(professores_candidatos)]
            db.session.add(EbdProfessor(
                classe_id=c.id,
                membro_id=prof_titular.id,
                cargo="principal",
                status="ativo",
                data_inicio=p3.data_inicio
            ))
            # Professor auxiliar
            prof_aux = professores_candidatos[(i + 1) % len(professores_candidatos)]
            if prof_aux.id != prof_titular.id:
                db.session.add(EbdProfessor(
                    classe_id=c.id,
                    membro_id=prof_aux.id,
                    cargo="auxiliar",
                    status="ativo",
                    data_inicio=p3.data_inicio
                ))

        db.session.commit()
        print("  ✅ Professores titulares e auxiliares vinculados a todas as salas.")

        # 5. Matrículas dos Alunos por Faixa Etária
        total_matriculas = 0
        hoje = date(2026, 8, 28)

        for m in membros_todos:
            idade = m.idade if m.idade is not None else 30
            # Encontra a classe correspondente à idade
            classe_alvo = None
            for c, cd in classes_criadas:
                if cd["idade_min"] <= idade <= cd["idade_max"]:
                    classe_alvo = c
                    break
            if not classe_alvo:
                classe_alvo = classes_criadas[-1][0] # Adultos como fallback

            db.session.add(EbdMatricula(
                classe_id=classe_alvo.id,
                membro_id=m.id,
                data_matricula=p3.data_inicio,
                status="ativo",
                observacoes="Matrícula inicial do período letivo."
            ))
            total_matriculas += 1

        db.session.commit()
        print(f"  ✅ {total_matriculas} alunos matriculados nas 5 classes da EBD.")

        # 6. Aulas e Frequências dos Domingos (3º Trimestre 2026)
        temas_licoes = [
            ("Lição 01", "O Semeador e os Tipos de Coração"),
            ("Lição 02", "O Trigo e o Joio: Discernimento e Paciência"),
            ("Lição 03", "O Grão de Mostarda: O Crescimento do Reino"),
            ("Lição 04", "O Tesouro Escondido e a Pérola de Grande Valor"),
            ("Lição 05", "O Credor Incompassivo: A Prática do Perdão"),
            ("Lição 06", "Os Trabalhadores da Vinha e a Graça Soberana"),
            ("Lição 07", "Os Dois Filhos: A Obediência Prática"),
            ("Lição 08", "O Filho Pródigo e o Amor Incondicional do Pai"),
        ]

        # Domingos de Julho a 28/Agosto de 2026
        data_corrente = p3.data_inicio
        domingos = []
        while data_corrente <= hoje:
            if data_corrente.weekday() == 6: # Domingo
                domingos.append(data_corrente)
            data_corrente += timedelta(days=1)

        motivos_falta = ["Saúde / Consulta", "Viagem em família", "Escala de Trabalho", "Compromisso Acadêmico"]

        total_aulas = 0
        total_frequencias = 0

        for idx_aula, d_aula in enumerate(domingos):
            if idx_aula < len(temas_licoes):
                num_licao, tema_licao = temas_licoes[idx_aula]
            else:
                num_licao, tema_licao = f"Lição {idx_aula+1:02d}", f"Estudo Bíblico Especial {idx_aula+1}"

            for c, _ in classes_criadas:
                aula = EbdAula(
                    classe_id=c.id,
                    professor_id=c.professor_principal.id if c.professor_principal else None,
                    data_aula=d_aula,
                    numero_licao=num_licao,
                    tema=f"{c.nome.split('—')[0].strip()}: {tema_licao}",
                    resumo_conteudo=f"Exposição dinâmica e estudo prático sobre '{tema_licao}'. Aplicação prática na vida cristã.",
                    status="realizada"
                )
                db.session.add(aula)
                db.session.flush()
                total_aulas += 1

                # Chamada de todos os matriculados
                matriculas_classe = EbdMatricula.query.filter_by(classe_id=c.id, status="ativo").all()
                for mat in matriculas_classe:
                    sorteio = random.random()
                    if sorteio < 0.82: # 82% presente
                        st = "presente"
                        motivo = None
                    elif sorteio < 0.92: # 10% falta justificada
                        st = "falta_justificada"
                        motivo = random.choice(motivos_falta)
                    else: # 8% falta
                        st = "falta"
                        motivo = None

                    freq = EbdFrequencia(
                        aula_id=aula.id,
                        matricula_id=mat.id,
                        status_presenca=st,
                        motivo_falta=motivo,
                        justificativa=f"Ausência comunicada: {motivo}" if motivo else None,
                        registrado_por="Secretaria da EBD"
                    )
                    db.session.add(freq)
                    total_frequencias += 1

        db.session.commit()
        print(f"  ✅ {total_aulas} aulas realizadas registradas nos domingos.")
        print(f"  ✅ {total_frequencias} registros de frequência consolidados (Mapa de Frequência & Desempenho).")

if __name__ == "__main__":
    seed_ebd()
