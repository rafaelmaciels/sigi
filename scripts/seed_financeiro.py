import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
from datetime import date, timedelta
from app import create_app, db
from app.models.financeiro import Financeiro
from app.models.member import Member
from app.models.user import User

app = create_app()

with app.app_context():
    print("Iniciando povoamento de dados financeiros...")
    
    # Busca membros para associar a dízimos e ofertas
    members = Member.query.all()
    dizimistas = [m for m in members if m.dizimista]
    if not dizimistas:
        dizimistas = members[:10]
        
    usuario_nome = "rafael@sigi.com"
    user = User.query.first()
    if user:
        usuario_nome = user.nome or user.email

    # Definição de receitas típicas recorrentes e avulsas
    # Período: De Janeiro de 2025 até Agosto de 2026 (20 meses)
    
    start_date = date(2025, 1, 1)
    end_date = date(2026, 8, 28)
    
    # Limpa dados anteriores se existirem (opcional, ou adiciona se estiver vazio)
    total_existente = Financeiro.query.count()
    if total_existente > 0:
        print(f"Encontrados {total_existente} lançamentos existentes. Limpando para inserção de dados novos e consistentes...")
        Financeiro.query.delete()
        db.session.commit()

    novos_lancamentos = []

    # Itera mês a mês
    current_year = 2025
    for year in [2025, 2026]:
        max_month = 8 if year == 2026 else 12
        for month in range(1, max_month + 1):
            
            # --- 1. RECEITAS DO MÊS ---
            # A) Dízimos dos membros (vários no decorrer do mês)
            for m in dizimistas:
                # Cada dizimista contribui 1 ou 2 vezes no mês
                dias_dizimo = [random.randint(5, 12)]
                if random.random() > 0.6:
                    dias_dizimo.append(random.randint(20, 26))
                
                for dia in dias_dizimo:
                    if year == 2026 and month == 8 and dia > 28:
                        dia = 25
                    val = round(random.uniform(150.0, 1200.0), 2)
                    forma = random.choice(["PIX", "PIX", "Transferência Bancária (TED/DOC)", "Dinheiro (Espécie)"])
                    conta = "Chave PIX Oficial" if "PIX" in forma else ("Conta Corrente Principal" if "Transferência" in forma else "Caixa Geral (Espécie)")
                    
                    novos_lancamentos.append(Financeiro(
                        data=date(year, month, dia),
                        valor=val,
                        tipo="Entrada",
                        categoria="Dízimos",
                        conta=conta,
                        departamento="Templo / Geral",
                        forma_pagamento=forma,
                        descricao=f"Dízimo fiel - {m.nome}",
                        observacoes="Contribuição mensal dizimista",
                        membro_id=m.id,
                        cpf_membro=m.cpf,
                        conciliado=True,
                        usuario=usuario_nome
                    ))

            # B) Ofertas de Cultos de Domingo e Quarta
            # 4 domingos por mês
            for dom in [3, 10, 17, 24]:
                if year == 2026 and month == 8 and dom > 28:
                    continue
                val_culto = round(random.uniform(600.0, 2400.0), 2)
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, dom),
                    valor=val_culto,
                    tipo="Entrada",
                    categoria="Ofertas de Culto",
                    conta=random.choice(["Caixa Geral (Espécie)", "Chave PIX Oficial"]),
                    departamento="Templo / Geral",
                    forma_pagamento=random.choice(["Dinheiro (Espécie)", "PIX"]),
                    descricao=f"Ofertas arrecadadas no culto de celebração ({dom:02d}/{month:02d})",
                    observacoes="Culto de Domingo - Celebração da Família",
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # C) Ofertas de Missões
            dia_missoes = random.choice([7, 14, 21])
            if not (year == 2026 and month == 8 and dia_missoes > 28):
                val_missoes = round(random.uniform(400.0, 1500.0), 2)
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, dia_missoes),
                    valor=val_missoes,
                    tipo="Entrada",
                    categoria="Ofertas de Missões",
                    conta="Fundo de Missões",
                    departamento="Missões & Evangelismo",
                    forma_pagamento="PIX",
                    descricao=f"Domingo de Missões - Arrecadação ({month:02d}/{year})",
                    observacoes="Oferta voluntária para obra missionária",
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # D) Ofertas de Construção / Reforma
            dia_reforma = 15
            val_reforma = round(random.uniform(500.0, 3000.0), 2)
            novos_lancamentos.append(Financeiro(
                data=date(year, month, dia_reforma),
                valor=val_reforma,
                tipo="Entrada",
                categoria="Ofertas de Construção / Reforma",
                conta="Fundo de Construção / Reforma",
                departamento="Obras & Patrimônio",
                forma_pagamento="PIX",
                descricao=f"Campanha tijolo abençoado / Ampliação ({month:02d}/{year})",
                observacoes="Fundo destinado à reforma do templo",
                conciliado=True,
                usuario=usuario_nome
            ))

            # E) Cantina / Livraria
            for sab in [6, 20]:
                if year == 2026 and month == 8 and sab > 28:
                    continue
                val_cantina = round(random.uniform(120.0, 480.0), 2)
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, sab),
                    valor=val_cantina,
                    tipo="Entrada",
                    categoria="Vendas da Cantina / Livraria",
                    conta="Caixa Geral (Espécie)",
                    departamento="Jovens & Adolescentes",
                    forma_pagamento=random.choice(["Cartão de Débito", "PIX", "Dinheiro (Espécie)"]),
                    descricao="Arrecadação Cantina dos Jovens",
                    observacoes="Vendas pós-culto",
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # --- 2. DESPESAS DO MÊS ---
            # A) Sustento Pastoral
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 5),
                valor=3800.00,
                tipo="Saída",
                categoria="Prebenda / Sustento Pastoral",
                conta="Conta Corrente Principal",
                departamento="Ministério Pastoral",
                forma_pagamento="Transferência Bancária (TED/DOC)",
                descricao="Prebenda Pastoral Mensal",
                observacoes="Pagamento de proventos do pastor presidente",
                conciliado=True,
                usuario=usuario_nome
            ))

            # B) Aluguel / Manutenção
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 10),
                valor=2200.00,
                tipo="Saída",
                categoria="Aluguel do Templo / Imóveis",
                conta="Conta Corrente Principal",
                departamento="Templo / Geral",
                forma_pagamento="Boleto",
                descricao="Aluguel do imóvel templo sede",
                cnpj_fornecedor="12.345.678/0001-90",
                conciliado=True,
                usuario=usuario_nome
            ))

            # C) Contas de Consumo (Água, Energia, Internet)
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 12),
                valor=round(random.uniform(450.0, 780.0), 2),
                tipo="Saída",
                categoria="Contas de Consumo (Água, Luz, Internet)",
                conta="Conta Corrente Principal",
                departamento="Secretaria & Administração",
                forma_pagamento="Boleto",
                descricao="Conta de Energia Elétrica - Enel/Neoenergia",
                cnpj_fornecedor="08.123.456/0001-11",
                conciliado=True,
                usuario=usuario_nome
            ))
            
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 13),
                valor=round(random.uniform(110.0, 190.0), 2),
                tipo="Saída",
                categoria="Contas de Consumo (Água, Luz, Internet)",
                conta="Conta Corrente Principal",
                departamento="Secretaria & Administração",
                forma_pagamento="Boleto",
                descricao="Conta de Água e Saneamento - Sabesp/Copasa",
                conciliado=True,
                usuario=usuario_nome
            ))

            novos_lancamentos.append(Financeiro(
                data=date(year, month, 15),
                valor=149.90,
                tipo="Saída",
                categoria="Contas de Consumo (Água, Luz, Internet)",
                conta="Conta Corrente Principal",
                departamento="Secretaria & Administração",
                forma_pagamento="Boleto",
                descricao="Link de Internet Fibra Óptica 500MB",
                conciliado=True,
                usuario=usuario_nome
            ))

            # D) Sustento Missionário
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 18),
                valor=900.00,
                tipo="Saída",
                categoria="Missões / Sustento Missionário",
                conta="Fundo de Missões",
                departamento="Missões & Evangelismo",
                forma_pagamento="PIX",
                descricao="Envio de auxílio missionário - Campo Sertão",
                observacoes="Projeto missionário parceiro",
                conciliado=True,
                usuario=usuario_nome
            ))

            # E) Ação Social / Cestas Básicas
            novos_lancamentos.append(Financeiro(
                data=date(year, month, 20),
                valor=round(random.uniform(350.0, 750.0), 2),
                tipo="Saída",
                categoria="Ação Social / Diaconia / Cestas Básicas",
                conta="Fundo de Ação Social",
                departamento="Ação Social & Diaconia",
                forma_pagamento=random.choice(["Cartão de Débito", "PIX"]),
                descricao="Aquisição de alimentos para cestas básicas comunitárias",
                observacoes="Atendimento a famílias carentes cadastradas",
                conciliado=True,
                usuario=usuario_nome
            ))

            # F) Escola Bíblica Dominical (EBD) / Didáticos
            if month in [1, 4, 7, 10]: # início de trimestres
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, 8),
                    valor=round(random.uniform(280.0, 520.0), 2),
                    tipo="Saída",
                    categoria="Escola Bíblica Dominical (EBD) / Didáticos",
                    conta="Conta Corrente Principal",
                    departamento="Escola Bíblica (EBD)",
                    forma_pagamento="Boleto",
                    descricao="Revistas e materiais didáticos para novo trimestre da EBD",
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # G) Manutenção do Templo e Equipamentos
            if random.random() > 0.4:
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, min(25, 28 if (year == 2026 and month == 8) else 25)),
                    valor=round(random.uniform(180.0, 850.0), 2),
                    tipo="Saída",
                    categoria="Manutenção do Templo e Estrutura",
                    conta="Conta Corrente Principal",
                    departamento="Obras & Patrimônio",
                    forma_pagamento="PIX",
                    descricao=random.choice([
                        "Manutenção preventiva dos ares-condicionados",
                        "Material de limpeza e copa para o mês",
                        "Substituição de lâmpadas LED e fiação",
                        "Pintura e reparos em alvenaria"
                    ]),
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # H) Louvor e Mídia
            if random.random() > 0.5:
                novos_lancamentos.append(Financeiro(
                    data=date(year, month, min(22, 28 if (year == 2026 and month == 8) else 22)),
                    valor=round(random.uniform(150.0, 600.0), 2),
                    tipo="Saída",
                    categoria="Comunicação, Mídia e Transmissão",
                    conta="Conta Corrente Principal",
                    departamento="Louvor & Multimídia",
                    forma_pagamento="Cartão de Crédito",
                    descricao="Cabos de áudio XLR, microfones e licença de software de transmissão",
                    conciliado=True,
                    usuario=usuario_nome
                ))

            # I) Taxas Bancárias
            novos_lancamentos.append(Financeiro(
                data=date(year, month, min(28, 28 if (year == 2026 and month == 8) else 28)),
                valor=39.90,
                tipo="Saída",
                categoria="Tarifas e Taxas Bancárias",
                conta="Conta Corrente Principal",
                departamento="Secretaria & Administração",
                forma_pagamento="Transferência Bancária (TED/DOC)",
                descricao="Tarifa de manutenção de conta jurídica",
                conciliado=True,
                usuario=usuario_nome
            ))

    print(f"Total de lançamentos gerados: {len(novos_lancamentos)}")
    db.session.bulk_save_objects(novos_lancamentos)
    db.session.commit()
    print("Dados financeiros populados com sucesso no banco de dados!")
