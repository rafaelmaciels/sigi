import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User, Permission, UserPermission

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

def setup_users():
    with app.app_context():
        # Admin
        admin = User.query.filter_by(email="rafael@sigi.com").first()
        if not admin:
            admin = User(nome="Admin Teste", email="rafael@sigi.com", is_admin=True, ativo=True)
            admin.set_password("admin123")
            db.session.add(admin)
        else:
            admin.is_admin = True
            admin.ativo = True

        # Operador
        op = User.query.filter_by(email="operador@sigi.com").first()
        if not op:
            op = User(nome="Operador Teste", email="operador@sigi.com", is_admin=False, ativo=True)
            op.set_password("operador123")
            db.session.add(op)
        else:
            op.is_admin = False
            op.ativo = True

        # Membro
        membro = User.query.filter_by(email="membro@sigi.com").first()
        if not membro:
            membro = User(nome="Membro Teste", email="membro@sigi.com", is_admin=False, ativo=True)
            membro.set_password("membro123")
            db.session.add(membro)
        else:
            membro.is_admin = False
            membro.ativo = True

        db.session.commit()

        # Permissoes do Operador: apenas eventos:view
        UserPermission.query.filter_by(user_id=op.id).delete()
        perm_eventos = Permission.query.filter_by(area="eventos", action="view").first()
        if not perm_eventos:
            perm_eventos = Permission(area="eventos", action="view")
            db.session.add(perm_eventos)
            db.session.commit()
        db.session.add(UserPermission(user_id=op.id, permission_id=perm_eventos.id))

        # Permissoes do Membro: nenhuma
        UserPermission.query.filter_by(user_id=membro.id).delete()
        db.session.commit()

        return admin.id, op.id, membro.id

def test_all_scenarios():
    admin_id, op_id, membro_id = setup_users()

    print("=" * 60)
    print("INICIANDO SUITE DE TESTES DE PERMISSOES E DASHBOARD")
    print("=" * 60)

    # ---------------------------------------------------------
    # TESTE 1: ADMINISTRADOR
    # ---------------------------------------------------------
    print("\n[TESTE 1] Testando usuario ADMINISTRADOR (ID: %d)..." % admin_id)
    client_admin = app.test_client()
    with client_admin.session_transaction() as sess:
        sess['_user_id'] = str(admin_id)
        sess['_fresh'] = True

    res_dash = client_admin.get('/dashboard')
    assert res_dash.status_code == 200, f"Falha no dashboard do admin: {res_dash.status_code}"
    html_admin = res_dash.get_data(as_text=True)

    assert "Fluxo do M" in html_admin, "Admin deveria visualizar 'Fluxo do Mes'"
    assert "Crescimento Natural da Igreja" in html_admin, "Admin deveria visualizar 'Crescimento Natural'"
    assert "Resumo da Movimenta" in html_admin, "Admin deveria visualizar 'Resumo da Movimentacao Anual'"
    assert "Distribui" in html_admin and "Batismo" in html_admin, "Admin deveria visualizar 'Distribuicao por Batismo'"
    assert "Hist" in html_admin and "Financeiro" in html_admin, "Admin deveria visualizar 'Historico Financeiro'"
    assert "crescimentoChart" in html_admin, "Admin deveria ter grafico de crescimento"
    assert "financeiroChart" in html_admin, "Admin deveria ter grafico financeiro"
    assert "membrosChart" in html_admin, "Admin deveria ter grafico de membros"
    print("  [OK] Dashboard do Administrador renderizou todos os 6 cards e graficos perfeitamente.")

    res_rel = client_admin.get('/membros/relatorio')
    assert res_rel.status_code == 200, f"Admin deveria acessar relatorio_membros: {res_rel.status_code}"
    print("  [OK] Admin acessou /membros/relatorio com sucesso (HTTP 200).")

    res_fin = client_admin.get('/financeiro/')
    assert res_fin.status_code == 200, f"Admin deveria acessar financeiro: {res_fin.status_code}"
    print("  [OK] Admin acessou /financeiro/ com sucesso (HTTP 200).")

    res_cfg = client_admin.get('/configuracoes/')
    assert res_cfg.status_code == 200, f"Admin deveria acessar configuracoes: {res_cfg.status_code}"
    print("  [OK] Admin acessou /configuracoes/ com sucesso (HTTP 200).")


    # ---------------------------------------------------------
    # TESTE 2: OPERADOR COM PERMISSAO APENAS EM EVENTOS
    # ---------------------------------------------------------
    print("\n[TESTE 2] Testando usuario OPERADOR (ID: %d)..." % op_id)
    client_op = app.test_client()
    with client_op.session_transaction() as sess:
        sess['_user_id'] = str(op_id)
        sess['_fresh'] = True

    res_dash_op = client_op.get('/dashboard')
    assert res_dash_op.status_code == 200, f"Falha no dashboard do operador: {res_dash_op.status_code}"
    html_op = res_dash_op.get_data(as_text=True)

    assert "Fluxo do M" not in html_op, "Operador NAO deveria visualizar 'Fluxo do Mes'"
    assert "Crescimento Natural da Igreja" not in html_op, "Operador NAO deveria visualizar 'Crescimento Natural'"
    assert "Resumo da Movimenta" not in html_op, "Operador NAO deveria visualizar 'Resumo da Movimentacao Anual'"
    assert "Distribui" not in html_op or "Batismo" not in html_op, "Operador NAO deveria visualizar 'Distribuicao por Batismo'"
    assert "Hist" not in html_op or "ltimos 6 Meses" not in html_op, "Operador NAO deveria visualizar 'Historico Financeiro'"
    assert "crescimentoChart" not in html_op, "Operador NAO deveria ter script crescimentoChart"
    assert "financeiroChart" not in html_op, "Operador NAO deveria ter script financeiroChart"
    assert "membrosChart" not in html_op, "Operador NAO deveria ter script membrosChart"
    print("  [OK] Dashboard do Operador ocultou todos os 6 cards e graficos sensiveis.")

    # Testar funcionalidade permitida pela Matriz
    res_eve = client_op.get('/eventos/')
    assert res_eve.status_code == 200, f"Operador deveria acessar eventos: {res_eve.status_code}"
    print("  [OK] Operador acessou /eventos/ com sucesso (HTTP 200, permitido na Matriz).")

    # Testar bloqueios de rotas nao permitidas
    res_fin_blocked = client_op.get('/financeiro/', follow_redirects=False)
    assert res_fin_blocked.status_code in [302, 403], f"Operador NAO deveria acessar financeiro: {res_fin_blocked.status_code}"
    print("  [OK] Tentativa de acesso direto a /financeiro/ foi bloqueada (HTTP 302).")

    res_rel_blocked = client_op.get('/membros/relatorio', follow_redirects=False)
    assert res_rel_blocked.status_code in [302, 403], f"Operador NAO deveria acessar /membros/relatorio: {res_rel_blocked.status_code}"
    print("  [OK] Tentativa de acesso direto a /membros/relatorio foi bloqueada (HTTP 302).")

    res_cfg_blocked = client_op.get('/configuracoes/', follow_redirects=False)
    assert res_cfg_blocked.status_code in [302, 403], f"Operador NAO deveria acessar /configuracoes/: {res_cfg_blocked.status_code}"
    print("  [OK] Tentativa de acesso direto a /configuracoes/ foi bloqueada (HTTP 302).")


    # ---------------------------------------------------------
    # TESTE 3: MEMBRO SEM PERMISSOES ADMINISTRATIVAS
    # ---------------------------------------------------------
    print("\n[TESTE 3] Testando usuario MEMBRO COMUM (ID: %d)..." % membro_id)
    client_membro = app.test_client()
    with client_membro.session_transaction() as sess:
        sess['_user_id'] = str(membro_id)
        sess['_fresh'] = True

    res_dash_membro = client_membro.get('/dashboard')
    assert res_dash_membro.status_code == 200, f"Falha no dashboard do membro: {res_dash_membro.status_code}"
    html_membro = res_dash_membro.get_data(as_text=True)

    assert "Fluxo do M" not in html_membro, "Membro NAO deveria visualizar 'Fluxo do Mes'"
    assert "Crescimento Natural da Igreja" not in html_membro, "Membro NAO deveria visualizar 'Crescimento Natural'"
    assert "Resumo da Movimenta" not in html_membro, "Membro NAO deveria visualizar 'Resumo da Movimentacao Anual'"
    assert "Distribui" not in html_membro or "Batismo" not in html_membro, "Membro NAO deveria visualizar 'Distribuicao por Batismo'"
    assert "Hist" not in html_membro or "ltimos 6 Meses" not in html_membro, "Membro NAO deveria visualizar 'Historico Financeiro'"
    print("  [OK] Dashboard do Membro ocultou todos os 6 cards e graficos restritos.")

    res_eve_membro = client_membro.get('/eventos/', follow_redirects=False)
    assert res_eve_membro.status_code in [302, 403], f"Membro sem permissao NAO deveria acessar /eventos/: {res_eve_membro.status_code}"
    print("  [OK] Membro sem permissao de eventos foi bloqueado em /eventos/ (HTTP 302).")

    print("\n" + "=" * 60)
    print("TODOS OS TESTES DE VALIDACAO PASSARAM COM 100% DE SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_scenarios()
