#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de testes para validação da lógica de ordenação de:
1. Eventos (Próximos cronológicos -> Passados do mais recente ao mais antigo)
2. Aniversariantes no Dashboard (Ciclo anual contínuo dinâmico)
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import Evento, Member
from app.services.dashboard_service import DashboardService
from utils.dates import get_system_timezone, get_current_datetime, get_current_date

def run_tests():
    app = create_app()
    with app.app_context():
        print("=" * 70)
        print("INICIANDO TESTES DE ORDENAÇÃO DINÂMICA (SiGI)")
        print("=" * 70)

        # ---------------------------------------------------------
        # TESTE 1: Timezone e Utilitário de Data
        # ---------------------------------------------------------
        print("\n[TESTE 1] Verificação de Timezone e Utilitário de Datas...")
        tz = get_system_timezone()
        dt_atual = get_current_datetime()
        d_atual = get_current_date()
        print(f"  Timezone ativo: {tz}")
        print(f"  Data/Hora atual local: {dt_atual}")
        print(f"  Data atual local: {d_atual}")
        assert dt_atual.date() == d_atual, "Data atual inconsistente com DateTime atual"
        print("  ✅ [OK] Utilitário de datas funcionando perfeitamente.")

        # ---------------------------------------------------------
        # TESTE 2: Lógica de Ordenação de Eventos
        # ---------------------------------------------------------
        print("\n[TESTE 2] Verificação da Ordenação de Eventos...")
        ref_now = datetime(2026, 8, 28, 12, 0, 0) # 28/08/2026 às 12:00
        
        # Cria eventos de teste em memória temporária (rollback no final)
        test_events = [
            Evento(titulo="Evento A - 10/08 (Passado antigo)", tipo="culto_especial", data_inicio=datetime(2026, 8, 10, 19, 0), data_fim=datetime(2026, 8, 10, 21, 0)),
            Evento(titulo="Evento B - 25/08 (Passado recente)", tipo="reuniao", data_inicio=datetime(2026, 8, 25, 20, 0), data_fim=datetime(2026, 8, 25, 21, 30)),
            Evento(titulo="Evento C - 28/08 Manhã (Passado hoje)", tipo="evangelismo", data_inicio=datetime(2026, 8, 28, 8, 0), data_fim=datetime(2026, 8, 28, 11, 0)),
            Evento(titulo="Evento D - 28/08 Noite (Próximo hoje)", tipo="culto_especial", data_inicio=datetime(2026, 8, 28, 19, 30), data_fim=datetime(2026, 8, 28, 21, 30)),
            Evento(titulo="Evento E - 29/08 (Próximo amanhã)", tipo="retiro", data_inicio=datetime(2026, 8, 29, 9, 0), data_fim=datetime(2026, 8, 29, 18, 0)),
            Evento(titulo="Evento F - 02/09 (Próximo)", tipo="conferencia", data_inicio=datetime(2026, 9, 2, 19, 0), data_fim=datetime(2026, 9, 2, 21, 0)),
            Evento(titulo="Evento G - 15/09 (Próximo distante)", tipo="batismo", data_inicio=datetime(2026, 9, 15, 10, 0), data_fim=datetime(2026, 9, 15, 12, 0)),
        ]
        
        for ev in test_events:
            db.session.add(ev)
        db.session.flush()

        order_clauses = Evento.get_order_by_proximos_e_passados(ref_now=ref_now)
        resultado_eventos = (
            Evento.query
            .filter(Evento.id.in_([e.id for e in test_events]))
            .order_by(*order_clauses)
            .all()
        )

        ordem_titulos = [e.titulo for e in resultado_eventos]
        print("  Ordem obtida:")
        for idx, t in enumerate(ordem_titulos, 1):
            print(f"    {idx}. {t}")

        # Ordem esperada:
        # 1. 28/08 Noite (Hoje futuro)
        # 2. 29/08 (Amanhã)
        # 3. 02/09
        # 4. 15/09
        # 5. 28/08 Manhã (Hoje passado)
        # 6. 25/08 (Passado recente)
        # 7. 10/08 (Passado antigo)
        assert resultado_eventos[0].titulo == "Evento D - 28/08 Noite (Próximo hoje)"
        assert resultado_eventos[1].titulo == "Evento E - 29/08 (Próximo amanhã)"
        assert resultado_eventos[2].titulo == "Evento F - 02/09 (Próximo)"
        assert resultado_eventos[3].titulo == "Evento G - 15/09 (Próximo distante)"
        assert resultado_eventos[4].titulo == "Evento C - 28/08 Manhã (Passado hoje)"
        assert resultado_eventos[5].titulo == "Evento B - 25/08 (Passado recente)"
        assert resultado_eventos[6].titulo == "Evento A - 10/08 (Passado antigo)"
        print("  ✅ [OK] Ordenação de eventos seguiu rigorosamente a regra: Próximos (ASC) -> Passados (DESC).")

        db.session.rollback()

        # ---------------------------------------------------------
        # TESTE 3: Lógica de Ciclo Anual de Aniversariantes
        # ---------------------------------------------------------
        print("\n[TESTE 3] Verificação da Ordenação do Ciclo Anual de Aniversariantes...")
        ref_today = date(2026, 8, 28) # 28 de Agosto

        test_members = [
            Member(nome="Ana (10/08 - Passou este ano)", data_nascimento=date(1990, 8, 10)),
            Member(nome="Bruno (28/08 - Hoje!)", data_nascimento=date(1995, 8, 28)),
            Member(nome="Carlos (30/08 - Em 2 dias)", data_nascimento=date(1992, 8, 30)),
            Member(nome="Daniela (05/09 - Em 8 dias)", data_nascimento=date(1985, 9, 5)),
            Member(nome="Eduardo (15/09 - Em 18 dias)", data_nascimento=date(2000, 9, 15)),
            Member(nome="Fernanda (20/10 - Em 53 dias)", data_nascimento=date(1998, 10, 20)),
            Member(nome="Gabriel (10/11 - Em 74 dias)", data_nascimento=date(1991, 11, 10)),
            Member(nome="Helena (05/01 - Próximo ano)", data_nascimento=date(1988, 1, 5)),
            Member(nome="Igor (15/02 - Próximo ano)", data_nascimento=date(2002, 2, 15)),
            Member(nome="Juliana (29/02 - Bissexto)", data_nascimento=date(2000, 2, 29)),
        ]

        for m in test_members:
            db.session.add(m)
        db.session.flush()

        aniversariantes_ordenados = DashboardService.get_proximos_aniversariantes(limit=100, ref_date=ref_today)
        
        # Filtra apenas os membros de teste
        ids_teste = [m.id for m in test_members]
        resultado_niver = [m for m in aniversariantes_ordenados if m.id in ids_teste]

        print("  Ordem de Aniversariantes:")
        for idx, m in enumerate(resultado_niver, 1):
            dias = DashboardService._dias_para_proximo_aniversario(m.data_nascimento, ref_today)
            print(f"    {idx}. {m.nome} -> {m.data_nascimento.strftime('%d/%m')} (faltam {dias} dias)")

        assert resultado_niver[0].nome.startswith("Bruno") # 28/08 (hoje = 0 dias)
        assert resultado_niver[1].nome.startswith("Carlos") # 30/08
        assert resultado_niver[2].nome.startswith("Daniela") # 05/09
        assert resultado_niver[3].nome.startswith("Eduardo") # 15/09
        assert resultado_niver[4].nome.startswith("Fernanda") # 20/10
        assert resultado_niver[5].nome.startswith("Gabriel") # 10/11
        assert resultado_niver[6].nome.startswith("Helena") # 05/01 (ano seguinte!)
        assert resultado_niver[7].nome.startswith("Igor") # 15/02 (ano seguinte!)
        assert resultado_niver[8].nome.startswith("Juliana") # 29/02 (ano seguinte!)
        assert resultado_niver[9].nome.startswith("Ana") # 10/08 (passou este ano -> último lugar!)

        print("  ✅ [OK] Ciclo anual contínuo de aniversariantes validado com sucesso!")

        # ---------------------------------------------------------
        # TESTE 4: Transição de Fim de Ano (31 de Dezembro)
        # ---------------------------------------------------------
        print("\n[TESTE 4] Verificação da Transição em 31 de Dezembro...")
        ref_nye = date(2026, 12, 31)
        resultado_nye = sorted(
            test_members,
            key=lambda m: (
                DashboardService._dias_para_proximo_aniversario(m.data_nascimento, ref_nye),
                m.nome
            )
        )
        print(f"  Primeiro aniversariante após 31/12: {resultado_nye[0].nome} (esperado Helena em 05/01)")
        assert resultado_nye[0].nome.startswith("Helena") # 05/01
        print("  ✅ [OK] Transição de virada de ano funciona automaticamente.")

        db.session.rollback()

        print("\n" + "=" * 70)
        print("TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! 🎉")
        print("=" * 70)

if __name__ == "__main__":
    run_tests()
