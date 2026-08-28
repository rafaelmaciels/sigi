import sys
import os
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import Member, User
from app.models.ebd import EbdConfig, EbdPeriodo, EbdClasse, EbdProfessor, EbdMatricula, EbdAula, EbdFrequencia

app = create_app()

def seed_ebd():
    with app.app_context():
        print("🌱 Iniciando povoamento da Escola Bíblica Dominical (EBD)...")

        # 1. Configuração Geral da EBD
        pastor = Member.query.filter(Member.funcao.ilike("%pastor%")).first() or Member.query.first()
        config = EbdConfig.query.first()
        if not config:
            config = EbdConfig(
                nome="Escola Bíblica Dominical — Sede",
                descricao="Departamento de Ensino Bíblico, Discipulado e Formação Cristã",
                dia_semana="Domingo",
                horario_inicio="09:00",
                horario_termino="10:30",
                coordenador_id=pastor.id if pastor else None,
                ativo=True
            )
            db.session.add(config)
        else:
            config.nome = "Escola Bíblica Dominical — Sede"
            config.coordenador_id = pastor.id if pastor else None
            config.ativo = True
        
        db.session.commit()
        print("✅ Configuração Geral da EBD salva.")

        # 2. Períodos Letivos
        p1 = EbdPeriodo.query.filter_by(nome="1º Trimestre 2026 - O Caráter de Cristo").first()
        if not p1:
            p1 = EbdPeriodo(
                nome="1º Trimestre 2026 - O Caráter de Cristo",
                data_inicio=date(2026, 1, 4),
                data_fim=date(2026, 3, 29),
                status="encerrado",
                observacoes="Estudo das bem-aventuranças e das virtudes do Fruto do Espírito."
            )
            db.session.add(p1)

        p2 = EbdPeriodo.query.filter_by(nome="2º Trimestre 2026 - A Igreja e sua Missão").first()
        if not p2:
            p2 = EbdPeriodo(
                nome="2º Trimestre 2026 - A Igreja e sua Missão",
                data_inicio=date(2026, 4, 5),
                data_fim=date(2026, 6, 28),
                status="encerrado",
                observacoes="Missiologia bíblica e a história do livro de Atos dos Apóstolos."
            )
            db.session.add(p2)

        p3 = EbdPeriodo.query.filter_by(nome="3º Trimestre 2026 - As Parábolas de Jesus").first()
        if not p3:
            p3 = EbdPeriodo(
                nome="3º Trimestre 2026 - As Parábolas de Jesus",
                data_inicio=date(2026, 7, 5),
                data_fim=date(2026, 9, 27),
                status="em_andamento",
                observacoes="Lições práticas sobre os mistérios e princípios do Reino de Deus."
            )
            db.session.add(p3)

        db.session.commit()
        print("✅ Períodos letivos cadastrados.")

        # 3. Classes para o Período Ativo (3º Trimestre)
        classes_data = [
            {
                "nome": "Maternal & Jardim — Pequenos de Jesus",
                "faixa_etaria": "3 a 6 anos",
                "sala": "Sala 01 (Espaço Infantil)",
                "capacidade": 20,
                "descricao": "Histórias bíblicas ilustradas, cânticos e atividades lúdicas de fé."
            },
            {
                "nome": "Primários & Juniores — Heróis da Fé",
                "faixa_etaria": "7 a 11 anos",
                "sala": "Sala 02 (1º Andar)",
                "capacidade": 25,
                "descricao": "Memorização de versículos, biografias bíblicas e fundamentos morais."
            },
            {
                "nome": "Adolescentes — Conectados com Deus",
                "faixa_etaria": "12 a 17 anos",
                "sala": "Sala 03 (Anexo Jovem)",
                "capacidade": 30,
                "descricao": "Desafios da juventude, identidade cristã e princípios para o dia a dia."
            },
            {
                "nome": "Jovens — Geração Forte",
                "faixa_etaria": "18 a 35 anos",
                "sala": "Auditório 2",
                "capacidade": 45,
                "descricao": "Vida universitária, vocação, relacionamentos bíblicos e maturidade espiritual."
            },
            {
                "nome": "Adultos — Maturidade Cristã",
                "faixa_etaria": "36 anos em diante",
                "sala": "Nave Principal",
                "capacidade": 120,
                "descricao": "Estudo aprofundado das Escrituras, família cristã e liderança servidora."
            }
        ]

        classes_criadas = []
        for cd in classes_data:
            c = EbdClasse.query.filter_by(nome=cd["nome"], periodo_id=p3.id).first()
            if not c:
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
            classes_criadas.append(c)

        db.session.commit()
        print(f"✅ {len(classes_criadas)} classes ativas cadastradas.")

        # 4. Membros para Professores e Alunos
        membros = Member.query.filter_by(status="Ativo").all()
        if len(membros) < 10:
            print("⚠️ Poucos membros encontrados para distribuição.")
            return

        # Distribui professores (os primeiros membros)
        professores_membros = membros[:5]
        for i, c in enumerate(classes_criadas):
            prof_membro = professores_membros[i % len(professores_membros)]
            ja_prof = EbdProfessor.query.filter_by(classe_id=c.id, membro_id=prof_membro.id).first()
            if not ja_prof:
                db.session.add(EbdProfessor(
                    classe_id=c.id,
                    membro_id=prof_membro.id,
                    cargo="principal",
                    status="ativo",
                    data_inicio=p3.data_inicio
                ))

        db.session.commit()
        print("✅ Professores vinculados a todas as classes.")

        # 5. Matrículas dos Alunos
        alunos_membros = membros[5:]
        for idx, m in enumerate(alunos_membros):
            c_dest = classes_criadas[idx % len(classes_criadas)]
            ja_mat = EbdMatricula.query.filter_by(classe_id=c_dest.id, membro_id=m.id, status="ativo").first()
            if not ja_mat:
                db.session.add(EbdMatricula(
                    classe_id=c_dest.id,
                    membro_id=m.id,
                    data_matricula=p3.data_inicio,
                    status="ativo",
                    observacoes="Matrícula inicial do período letivo."
                ))

        db.session.commit()
        print("✅ Alunos matriculados nas turmas.")

        # 6. Aulas e Frequências dos Domingos
        temas_licoes = [
            ("Lição 01", "O Semeador e os Tipos de Coração"),
            ("Lição 02", "O Trigo e o Joio: Discernimento e Paciência"),
            ("Lição 03", "O Grão de Mostarda e o Fermento: O Crescimento Invisível"),
            ("Lição 04", "O Tesouro Escondido e a Pérola de Grande Valor"),
            ("Lição 05", "O Credor Incompassivo: O Poder do Perdão"),
            ("Lição 06", "Os Trabalhadores da Vinha e a Graça Soberana"),
            ("Lição 07", "Os Dois Filhos: A Obediência Prática"),
            ("Lição 08", "O Filho Pródigo e o Pai Misericordioso"),
        ]

        data_corrente = p3.data_inicio
        domingos = []
        while data_corrente <= date.today():
            if data_corrente.weekday() == 6: # Domingo
                domingos.append(data_corrente)
            data_corrente += timedelta(days=1)

        motivos_falta = ["Doença", "Viagem", "Trabalho", "Compromisso Familiar"]

        for idx_aula, d_aula in enumerate(domingos[:len(temas_licoes)]):
            num_licao, tema_licao = temas_licoes[idx_aula]

            for c in classes_criadas:
                aula = EbdAula.query.filter_by(classe_id=c.id, data_aula=d_aula).first()
                if not aula:
                    aula = EbdAula(
                        classe_id=c.id,
                        professor_id=c.professor_principal.id if c.professor_principal else None,
                        data_aula=d_aula,
                        numero_licao=num_licao,
                        tema=tema_licao,
                        resumo_conteudo=f"Exposição bíblica e dinâmicas da {num_licao}.",
                        status="realizada"
                    )
                    db.session.add(aula)
                    db.session.flush()

                # Chamada dos alunos matriculados
                matriculas_classe = EbdMatricula.query.filter_by(classe_id=c.id, status="ativo").all()
                for mat in matriculas_classe:
                    freq = EbdFrequencia.query.filter_by(aula_id=aula.id, matricula_id=mat.id).first()
                    if not freq:
                        # 80% de chance de presença, 10% de falta justificada, 10% de falta
                        sorteio = random.random()
                        if sorteio < 0.80:
                            st = "presente"
                            motivo = None
                        elif sorteio < 0.90:
                            st = "falta_justificada"
                            motivo = random.choice(motivos_falta)
                        else:
                            st = "falta"
                            motivo = None

                        freq = EbdFrequencia(
                            aula_id=aula.id,
                            matricula_id=mat.id,
                            status_presenca=st,
                            motivo_falta=motivo,
                            justificativa=f"Ausência por motivo de {motivo}" if motivo else None,
                            registrado_por="Superintendência EBD"
                        )
                        db.session.add(freq)

        db.session.commit()
        print("✅ Aulas e chamadas dos domingos registradas com sucesso!")

        total_a = EbdAula.query.count()
        total_f = EbdFrequencia.query.count()
        total_m = EbdMatricula.query.count()
        print(f"🎉 Povoamento Concluído: {total_m} matrículas, {total_a} aulas e {total_f} registros de frequência.")

if __name__ == "__main__":
    seed_ebd()
