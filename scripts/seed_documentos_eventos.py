import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, date, timedelta
from app import create_app, db
from app.models import Evento, Ata, Certificado, Carta, Member, User

app = create_app()

with app.app_context():
    print("Iniciando povoamento de Eventos, Atas, Cartas Pastorais e Certificados...")

    members = Member.query.all()
    if not members:
        print("Aviso: Nenhum membro cadastrado para vincular.")
    
    # -------------------------------------------------------------
    # 1. EVENTOS & CULTOS (Calendário)
    # -------------------------------------------------------------
    print("Populando Calendário de Eventos & Cultos...")
    Evento.query.delete()

    now = datetime(2026, 8, 28, 9, 0)
    
    eventos_data = [
        # Passados / Concluídos
        {
            "titulo": "Culto da Virada e Consagração 2026",
            "descricao": "Celebração de Ação de Graças pela entrada do Ano Novo com Santa Ceia e vigília de oração.",
            "tipo": "culto especial",
            "data_inicio": datetime(2025, 12, 31, 22, 0),
            "data_fim": datetime(2026, 1, 1, 1, 0),
            "local": "Templo Sede - Nave Principal",
            "organizador": "Pr. Carlos Eduardo (Ministério Pastoral)",
            "status": "concluído"
        },
        {
            "titulo": "Retiro Espiritual de Carnaval - 'Santidade ao Senhor'",
            "descricao": "Acampamento de jovens e famílias com ministrações da Palavra, louvor, gincanas bíblicas e comunhão.",
            "tipo": "retiro",
            "data_inicio": datetime(2026, 2, 14, 18, 0),
            "data_fim": datetime(2026, 2, 17, 14, 0),
            "local": "Sítio Recanto das Águas Claras - Nazaré Paulista",
            "organizador": "Liderança de Jovens (Geração Eleita)",
            "status": "concluído"
        },
        {
            "titulo": "1º Grande Batismo nas Águas de 2026",
            "descricao": "Cerimônia solene de batismo nas águas dos novos convertidos que concluíram o discipulado.",
            "tipo": "batismo",
            "data_inicio": datetime(2026, 4, 12, 9, 30),
            "data_fim": datetime(2026, 4, 12, 12, 30),
            "local": "Chácara Ebenezer / Batistério Municipal",
            "organizador": "Conselho de Diaconia e Pastores",
            "status": "concluído"
        },
        {
            "titulo": "Conferência Missionária 'Ide por Todo o Mundo'",
            "descricao": "Fim de semana focado em missões transculturais com testemunhos de missionários e arrecadação de fundos.",
            "tipo": "conferência",
            "data_inicio": datetime(2026, 5, 22, 19, 30),
            "data_fim": datetime(2026, 5, 24, 21, 30),
            "local": "Templo Sede",
            "organizador": "Secretaria de Missões (SEMADI)",
            "status": "concluído"
        },
        {
            "titulo": "Cruzada Evangelística no Bairro Esperança",
            "descricao": "Ação de evangelismo ao ar livre com atendimento social, corte de cabelo gratuito e pregação da Palavra.",
            "tipo": "evangelismo",
            "data_inicio": datetime(2026, 6, 20, 14, 0),
            "data_fim": datetime(2026, 6, 20, 18, 0),
            "local": "Praça Central do Bairro Esperança",
            "organizador": "Departamento de Ação Social e Evangelismo",
            "status": "concluído"
        },
        {
            "titulo": "Assembleia Geral Ordinária de Membros (1º Semestre)",
            "descricao": "Apresentação dos relatórios da secretaria, balancete financeiro semestral e parecer do conselho fiscal.",
            "tipo": "reunião",
            "data_inicio": datetime(2026, 7, 19, 15, 0),
            "data_fim": datetime(2026, 7, 19, 18, 0),
            "local": "Salão Social da Igreja",
            "organizador": "Mesa Diretora da Igreja",
            "status": "concluído"
        },
        # Atuais / Próximos
        {
            "titulo": "Vigília Jovem 'Desperta Igreja'",
            "descricao": "Noite de clamor, adoração e busca do Espírito Santo voltada para toda a mocidade e adolescentes.",
            "tipo": "culto especial",
            "data_inicio": datetime(2026, 8, 29, 23, 0),
            "data_fim": datetime(2026, 8, 30, 5, 0),
            "local": "Templo Sede",
            "organizador": "Ministério de Jovens e Louvor",
            "status": "confirmado"
        },
        {
            "titulo": "Culto de Celebração da Família e Santa Ceia",
            "descricao": "Culto solene com celebração da Ceia do Senhor, consagração de crianças e recepção de novos membros.",
            "tipo": "culto especial",
            "data_inicio": datetime(2026, 9, 6, 18, 30),
            "data_fim": datetime(2026, 9, 6, 21, 0),
            "local": "Templo Sede - Nave Principal",
            "organizador": "Ministério Pastoral",
            "status": "confirmado"
        },
        {
            "titulo": "Congresso de Mulheres 'Mulher Virtuosa 2026'",
            "descricao": "Encontro anual do círculo de oração e departamento feminino com preletoras convidadas e workshops.",
            "tipo": "conferência",
            "data_inicio": datetime(2026, 9, 18, 19, 0),
            "data_fim": datetime(2026, 9, 20, 21, 30),
            "local": "Auditório Principal",
            "organizador": "Departamento Feminino (Círculo de Oração)",
            "status": "confirmado"
        },
        {
            "titulo": "2º Batismo nas Águas do Ano",
            "descricao": "Celebração batismal para novos irmãos convertidos nos cultos e células de evangelismo.",
            "tipo": "batismo",
            "data_inicio": datetime(2026, 10, 11, 9, 0),
            "data_fim": datetime(2026, 10, 11, 12, 0),
            "local": "Chácara Betel",
            "organizador": "Equipe de Discipulado e Batismos",
            "status": "planejado"
        },
        {
            "titulo": "Festa das Crianças - Ministério Infantil",
            "descricao": "Comemoração do Dia das Crianças com teatro bíblico, gincanas, distribuição de lembrancinhas e lanches.",
            "tipo": "outros",
            "data_inicio": datetime(2026, 10, 12, 14, 0),
            "data_fim": datetime(2026, 10, 12, 17, 30),
            "local": "Pátio da EBD Infantil",
            "organizador": "Ministério Infantil (Cordeirinhos de Cristo)",
            "status": "planejado"
        },
        {
            "titulo": "Conferência Anual de Liderança e Discipulado",
            "descricao": "Treinamento intensivo para líderes de ministérios, professores da EBD e diáconos.",
            "tipo": "conferência",
            "data_inicio": datetime(2026, 11, 6, 19, 30),
            "data_fim": datetime(2026, 11, 8, 17, 0),
            "local": "Templo Sede",
            "organizador": "Pastor Presidente e Diretoria",
            "status": "planejado"
        },
        {
            "titulo": "Cantata de Natal 2026 - 'O Verbo se Fez Carne'",
            "descricao": "Grande apresentação de Natal com coro unificado, orquestra instrumental e encenação da Natividade.",
            "tipo": "culto especial",
            "data_inicio": datetime(2026, 12, 20, 19, 0),
            "data_fim": datetime(2026, 12, 20, 21, 30),
            "local": "Templo Sede",
            "organizador": "Ministério de Louvor e Artes",
            "status": "planejado"
        }
    ]

    for ev in eventos_data:
        evento_obj = Evento(
            titulo=ev["titulo"],
            descricao=ev["descricao"],
            tipo=ev["tipo"],
            data_inicio=ev["data_inicio"],
            data_fim=ev["data_fim"],
            local=ev["local"],
            organizador=ev["organizador"],
            status=ev["status"],
            token_expira_em=ev["data_fim"] + timedelta(days=30)
        )
        db.session.add(evento_obj)


    # -------------------------------------------------------------
    # 2. LIVRO DE ATAS (Atas)
    # -------------------------------------------------------------
    print("Populando Livro de Atas...")
    Ata.query.delete()

    atas_data = [
        {
            "titulo": "Ata nº 01/2025 – Assembleia Geral de Abertura do Exercício e Calendário Anual",
            "data_emissao": date(2025, 1, 15),
            "tipo": "Assembleia Geral",
            "situacao": "Aprovada",
            "local": "Templo Sede, Rua da Paz, nº 100",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "Pastor Presidente, Corpo Diaconal, Diretoria Executiva e 48 membros comungantes.",
            "pauta": "1. Apresentação do Calendário Eclesiástico de 2025; 2. Aprovação da proposta orçamentária; 3. Nomeação dos líderes de departamentos.",
            "deliberacoes": "Aprovado por unanimidade o calendário de eventos e o orçamento previsto para o exercício de 2025. Homologadas as lideranças dos departamentos Infantil, Jovens, Mulheres e Missões.",
            "observacoes": "A ata foi lida, aprovada e assinada por todos os presentes na mesa diretora."
        },
        {
            "titulo": "Ata nº 02/2025 – Reunião de Diretoria: Aprovação da Reforma do Telhado e Climatização",
            "data_emissao": date(2025, 5, 10),
            "tipo": "Reunião de Diretoria",
            "situacao": "Aprovada",
            "local": "Secretaria da Igreja",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "Diretoria Executiva e Comissão de Obras e Patrimônio.",
            "pauta": "1. Orçamentos para troca das calhas e telhas da nave central; 2. Instalação de novos aparelhos de ar-condicionado.",
            "deliberacoes": "Aprovada a contratação da empresa Construtora Aliança no valor orçado, utilizando os recursos do Fundo de Construção e Ofertas Especiais de Reforma.",
            "observacoes": "Início das obras previsto para o dia 20 de maio de 2025."
        },
        {
            "titulo": "Ata nº 03/2025 – Assembleia Geral Ordinária: Prestação de Contas do 1º Semestre",
            "data_emissao": date(2025, 7, 20),
            "tipo": "Assembleia Geral",
            "situacao": "Aprovada",
            "local": "Templo Sede",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "Membros efetivos e comungantes da igreja local.",
            "pauta": "1. Parecer do Conselho Fiscal sobre as contas do 1º semestre de 2025; 2. Relatório de crescimento da membresia.",
            "deliberacoes": "Contas aprovadas com louvor pelo plenário sem ressalvas. Registrada a entrada de 12 novos membros por batismo e transferência.",
            "observacoes": "Demonstrativo contábil afixado no mural de avisos da secretaria."
        },
        {
            "titulo": "Ata nº 01/2026 – Assembleia Geral Ordinária: Eleição da Mesa Diretora do Biênio 2026-2027",
            "data_emissao": date(2026, 1, 18),
            "tipo": "Assembleia Geral",
            "situacao": "Aprovada",
            "local": "Templo Sede",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "55 membros votantes presentes e diretoria em exercício.",
            "pauta": "1. Eleição e posse da Diretoria Estatutária; 2. Eleição dos membros do Conselho Fiscal.",
            "deliberacoes": "Eleita por aclamação a chapa única encabeçada pelo Pr. Carlos Eduardo (Presidente), Ir. Marcos Toledo (1º Secretário) e Ir. Sandra Lima (1ª Tesoureira).",
            "observacoes": "Documentação encaminhada para registro em Cartório de Registro de Pessoas Jurídicas."
        },
        {
            "titulo": "Ata nº 02/2026 – Reunião Ministerial: Planejamento da Conferência de Missões e Evangelismo",
            "data_emissao": date(2026, 4, 5),
            "tipo": "Conselho Pastoral",
            "situacao": "Aprovada",
            "local": "Gabinete Pastoral",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "Pastores auxiliares, presbíteros e coordenadores de missões.",
            "pauta": "1. Definição da data e preletores da Conferência Missionária; 2. Envio de ajuda financeira para os missionários no Sertão.",
            "deliberacoes": "Fixada a data para 22 a 24 de maio de 2026. Aprovado o reajuste de 15% no sustento missionário enviado mensalmente ao campo.",
            "observacoes": "Todos os departamentos foram orientados a participar dos preparativos."
        },
        {
            "titulo": "Ata nº 03/2026 – Assembleia Geral Semestral: Balancete Financeiro e Recepção de Membros",
            "data_emissao": date(2026, 7, 19),
            "tipo": "Assembleia Geral",
            "situacao": "Aprovada",
            "local": "Templo Sede",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "62 membros ativos presentes.",
            "pauta": "1. Balancete do 1º Semestre de 2026; 2. Recepção formal de 8 novos membros por aclamação.",
            "deliberacoes": "Aprovado integralmente o balancete com saldo positivo em todas as contas e fundos. Homologada a recepção dos novos irmãos no rol de membros.",
            "observacoes": "Ata redigida em livro próprio de registro eclesiástico."
        },
        {
            "titulo": "Ata nº 04/2026 – Reunião Extraordinária de Diretoria: Aquisição de Novos Equipamentos de Som",
            "data_emissao": date(2026, 8, 15),
            "tipo": "Reunião de Diretoria",
            "situacao": "Em Revisão",
            "local": "Secretaria Geral",
            "presidente": "Pr. Carlos Eduardo Ramos",
            "secretario": "Ir. Marcos Vinícius Toledo",
            "participantes": "Membros da diretoria e equipe técnica de áudio e multimídia.",
            "pauta": "1. Substituição da mesa de som analógica por mesa digital de 32 canais; 2. Compra de microfones sem fio UHF.",
            "deliberacoes": "Em fase de cotação com três fornecedores especializados. Decidido pela aquisição do modelo Behringer X32 com pagamento parcelado em 6x sem juros.",
            "observacoes": "Ata aguardando assinatura formal dos conselheiros fiscais."
        }
    ]

    for ata in atas_data:
        db.session.add(Ata(**ata))


    # -------------------------------------------------------------
    # 3. CARTAS PASTORAIS (Cartas)
    # -------------------------------------------------------------
    print("Populando Cartas Pastorais...")
    Carta.query.delete()

    sample_members = members[:6] if len(members) >= 6 else members

    cartas_data = [
        {
            "titulo": "Carta de Recomendação e Apresentação de Membro em Comunhão",
            "data_emissao": date(2026, 8, 20),
            "remetente": "Pr. Carlos Eduardo Ramos - Pastor Presidente",
            "destinatario": "Igreja Evangélica Assembleia de Deus de Curitiba/PR",
            "cidade": "Curitiba - PR",
            "situacao": "enviado",
            "membro_id": sample_members[0].id if sample_members else None,
            "corpo": (
                f"Aos amados irmãos em Cristo Jesus e ao Ilustre Ministério Pastoral,\n\n"
                f"Vimos por meio desta apresentar e recomendar fraternalmente o(a) irmão(ã) "
                f"{sample_members[0].nome if sample_members else 'Fernando Rodrigues Gomes'}, "
                f"membro em plena comunhão e assíduo nesta igreja local, cumpridor(a) de seus deveres cristãos "
                f"e de conduta moral e espiritual ilibada.\n\n"
                f"Tendo transferido sua residência para essa aprazível localidade por motivos profissionais, "
                f"solicitamos que o(a) recebam no amor de Cristo e prestem o devido pastoreio e acolhimento.\n\n"
                f"Na paz do Senhor Jesus Cristo,\n"
                f"Pr. Carlos Eduardo Ramos\nPastor Titular"
            )
        },
        {
            "titulo": "Carta de Transferência Eclesiástica Oficial",
            "data_emissao": date(2026, 7, 28),
            "remetente": "Igreja Sede - Secretaria Geral",
            "destinatario": "Igreja Batista Renovada de Belo Horizonte/MG",
            "cidade": "Belo Horizonte - MG",
            "situacao": "entregue",
            "membro_id": sample_members[1].id if len(sample_members) > 1 else None,
            "corpo": (
                f"Saudações na paz do Senhor Jesus Cristo!\n\n"
                f"Certificamos que a irmã {sample_members[1].nome if len(sample_members) > 1 else 'Manuela Fernandes Soares'} "
                f"foi desligada a pedido próprio do rol de membros desta congregação, encontrando-se em plena paz "
                f"e sem nenhuma pendência disciplinar, doutrinária ou administrativa.\n\n"
                f"Rogamos a Deus ricas bênçãos sobre sua nova congregação e ministério local.\n\n"
                f"Fraternalmente em Cristo,\n"
                f"Secretaria Administrativa & Conselho Pastoral"
            )
        },
        {
            "titulo": "Carta Convite para Pregador Convidado - Conferência de Jovens",
            "data_emissao": date(2026, 8, 10),
            "remetente": "Ministério Pastoral & Liderança de Jovens",
            "destinatario": "Pr. Lucas Evangelista Mendes",
            "cidade": "Campinas - SP",
            "situacao": "enviado",
            "membro_id": None,
            "corpo": (
                f"Prezado Pr. Lucas Evangelista,\n\n"
                f"A paz do Senhor Jesus.\n\n"
                f"Temos a honra e a alegria de convidá-lo formalmente para ser o preletor oficial da nossa "
                f"Vigília e Encontro da Juventude, que acontecerá no dia 29 de Agosto de 2026, às 23h, em nosso Templo Sede.\n\n"
                f"Todas as despesas de translado e hospedagem serão cobertas pela igreja anfitriã. Aguardamos sua "
                f"confirmação para alinharmos os detalhes de acolhimento.\n\n"
                f"Em Cristo,\nPr. Carlos Eduardo Ramos"
            )
        },
        {
            "titulo": "Carta Pastoral de Conforto e Solidariedade à Família Enlutada",
            "data_emissao": date(2026, 6, 15),
            "remetente": "Gabinete Pastoral da Igreja",
            "destinatario": "Família Silva e Oliveira",
            "cidade": "São Paulo - SP",
            "situacao": "entregue",
            "membro_id": sample_members[2].id if len(sample_members) > 2 else None,
            "corpo": (
                f"Queridos irmãos e amada família,\n\n"
                f"'Preciosa é à vista do Senhor a morte dos seus santos' (Salmo 116:15).\n\n"
                f"Expressamos nossos mais profundos sentimentos de pesar e solidariedade pelo passamento de seu ente querido. "
                f"Que o Consolador Divino, o Espírito Santo de Deus, derrame bálsamo e paz sobre todos os corações neste momento "
                f"de dor e saudade. A igreja continua em constante oração por toda a família.\n\n"
                f"Com o abraço fraterno de toda a comunidade da fé,\nPr. Carlos Eduardo"
            )
        },
        {
            "titulo": "Carta de Autorização e Credencial de Viagem Missionária",
            "data_emissao": date(2026, 8, 5),
            "remetente": "Secretaria de Missões e Evangelismo",
            "destinatario": "A quem possa interessar / Comunidades do Vale do Ribeira",
            "cidade": "Registro - SP",
            "situacao": "enviado",
            "membro_id": sample_members[3].id if len(sample_members) > 3 else None,
            "corpo": (
                f"Declaramos para os devidos fins que o(a) portador(a) desta carta credencial, "
                f"{sample_members[3].nome if len(sample_members) > 3 else 'Thiago Alves Barbosa'}, "
                f"é missionário(a) enviado(a) e devidamente credenciado(a) por esta igreja para realização de "
                f"visitas pastorais, assistência social e evangelização em comunidades ribeirinhas no período de 10 a 25 de Agosto de 2026.\n\n"
                f"Solicitamos a todas as autoridades e comunidades a acolhida fraternal necessária para o bom cumprimento desta missão cristã.\n\n"
                f"Pr. Carlos Eduardo Ramos - Presidente"
            )
        },
        {
            "titulo": "Carta Circular aos Membros: Início da Campanha de Oração e Reforma",
            "data_emissao": date(2026, 8, 1),
            "remetente": "Pastorado da Igreja",
            "destinatario": "A todos os Membros e Congregados",
            "cidade": "São Paulo - SP",
            "situacao": "entregue",
            "membro_id": None,
            "corpo": (
                f"Amada Igreja do Senhor,\n\n"
                f"Graça e paz da parte de nosso Senhor e Salvador Jesus Cristo.\n\n"
                f"Convocamos todo o corpo de membros para nos unirmos em 21 dias de oração, consagração e jejum pelo avivamento de nossas famílias "
                f"e pelo sucesso da campanha de ampliação do templo sede. Cremos que grandes coisas o Senhor fará no meio de nós!\n\n"
                f"'Edifiquemos o muro, e já não seremos mais em opróbrio' (Neemias 2:17).\n\n"
                f"Unidos na mesma fé,\nCorpo Pastoral"
            )
        }
    ]

    for c in cartas_data:
        db.session.add(Carta(**c))


    # -------------------------------------------------------------
    # 4. CERTIFICADOS (Certificados)
    # -------------------------------------------------------------
    print("Populando Certificados...")
    Certificado.query.delete()

    certificados_data = []

    # Certificados de Batismo
    for i, m in enumerate(members[:8]):
        certificados_data.append({
            "titulo": f"Certificado de Batismo nas Águas – {m.nome}",
            "data_emissao": m.data_batismo or date(2026, 4, 12),
            "criado_por": m.nome,
            "evento": "1º Grande Batismo nas Águas de 2026",
            "situacao": "entregue",
            "corpo": (
                f"Certificamos que {m.nome.upper()} professou publicamente a sua fé no Senhor Jesus Cristo "
                f"e foi sepultado(a) nas águas batismais em nome do Pai, do Filho e do Espírito Santo, "
                f"segundo a ordenança bíblica de Mateus 28:19, tornando-se membro comungante do corpo de Cristo."
            )
        })

    # Certificados de Curso de Liderança e EBD
    for i, m in enumerate(members[8:14]):
        certificados_data.append({
            "titulo": f"Certificado de Conclusão do Curso de Liderança Eclesiástica – {m.nome}",
            "data_emissao": date(2026, 6, 28),
            "criado_por": m.nome,
            "evento": "Curso de Capacitação de Líderes e Obreiros 2026",
            "situacao": "entregue",
            "corpo": (
                f"Certificamos para os devidos fins ministeriais que {m.nome.upper()} concluiu com excelente aproveitamento "
                f"o Curso de Capacitação em Liderança Cristã e Hermenêutica Bíblica, com carga horária de 60 horas/aula, "
                f"demonstrando zelo, dedicação e fidelidade às Sagradas Escrituras."
            )
        })

    # Certificados de Apresentação de Crianças
    for i, m in enumerate(members[14:18]):
        certificados_data.append({
            "titulo": f"Certificado de Apresentação ao Senhor – {m.nome}",
            "data_emissao": date(2026, 5, 10),
            "criado_por": m.nome,
            "evento": "Culto Solene de Consagração de Crianças e Famílias",
            "situacao": "entregue",
            "corpo": (
                f"Certificamos que a criança foi apresentada e consagrada ao Senhor Todo-Poderoso em culto solene, "
                f"conforme o exemplo bíblico de Lucas 2:22, sob as orações e bênçãos pastorais, assumindo os pais o solene "
                f"compromisso de educá-la nos caminhos da verdade e no temor do Senhor."
            )
        })

    # Certificados de Reconhecimento e Diaconato
    for i, m in enumerate(members[18:22]):
        certificados_data.append({
            "titulo": f"Certificado de Consagração ao Diaconato – {m.nome}",
            "data_emissao": date(2026, 1, 18),
            "criado_por": m.nome,
            "evento": "Assembleia Geral Solene de Ordenação e Posse",
            "situacao": "entregue",
            "corpo": (
                f"Certificamos que o(a) irmão(ã) {m.nome.upper()} foi solenemente consagrado(a) ao Santo Ministério de Diaconia, "
                f"em reconhecimento ao seu testemunho irrepreensível, piedade e dedicação incansável na obra de Deus e no serviço aos santos (1 Timóteo 3:8-13)."
            )
        })

    # Certificados de Membresia e Honra ao Mérito
    for i, m in enumerate(members[22:26]):
        certificados_data.append({
            "titulo": f"Certificado de Membro Oficial da Igreja – {m.nome}",
            "data_emissao": date(2026, 7, 19),
            "criado_por": m.nome,
            "evento": "Recepção de Novos Membros e Batismo",
            "situacao": "enviado",
            "corpo": (
                f"Certificamos que {m.nome.upper()} é membro efetivo, ativo e em plena comunhão desta congregação, "
                f"tendo direito a todos os privilégios e responsabilidades espirituais conferidos pelo Estatuto da Igreja e pela Palavra de Deus."
            )
        })

    for cert in certificados_data:
        db.session.add(Certificado(**cert))

    db.session.commit()

    print("\n" + "=" * 60)
    print("POVOAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"Total de Eventos gerados: {Evento.query.count()}")
    print(f"Total de Atas geradas: {Ata.query.count()}")
    print(f"Total de Cartas Pastorais geradas: {Carta.query.count()}")
    print(f"Total de Certificados gerados: {Certificado.query.count()}")
    print("=" * 60)
