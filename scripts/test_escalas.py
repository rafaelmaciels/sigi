import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import User, Member, Permission, UserPermission, Equipe, EquipeFuncao, EquipeMembro, Escala, EscalaItem
from app.services.escala_service import EscalaService

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

def run_tests():
    print("=" * 70)
    print("TESTES AUTOMATIZADOS DO MODULO DE ESCALAS & VOLUNTARIOS")
    print("=" * 70)

    with app.app_context():
        # Limpeza preventiva de dados de testes anteriores
        for title in ['Culto Especial de Teste Automatizado', 'Outra Atividade Simultanea', 'Escala Clonada Teste']:
            for e in Escala.query.filter_by(titulo=title).all():
                db.session.delete(e)
        db.session.commit()

        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("[ERRO] Nenhum usuario admin encontrado para executar os testes.")
            return False

        client_admin = app.test_client()
        with client_admin.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # -------------------------------------------------------------------
        # [1/10] Listagem de Escalas & Autocomplete
        # -------------------------------------------------------------------
        print("\n[1/10] Testando listagem de escalas (/escalas/) e autocomplete (/api/busca/escalas)...")
        res = client_admin.get("/escalas/")
        assert res.status_code == 200, f"Status incorreto: {res.status_code}"
        assert "Escala de Obreiros" in res.get_data(as_text=True)

        res_ac = client_admin.get("/api/busca/escalas?q=Culto")
        assert res_ac.status_code == 200
        dados_ac = res_ac.get_json()
        assert isinstance(dados_ac, list)
        print("  [OK] Listagem e endpoint de autocomplete validados com sucesso (Status 200).")

        # -------------------------------------------------------------------
        # [2/10] Criação de Nova Escala
        # -------------------------------------------------------------------
        print("\n[2/10] Testando criacao de nova escala (/escalas/nova)...")
        hoje = date.today()
        data_escala = hoje + timedelta(days=10)
        payload_escala = {
            "titulo": "Culto Especial de Teste Automatizado",
            "data": data_escala.strftime("%Y-%m-%d"),
            "hora_inicio": "19:30",
            "hora_fim": "21:30",
            "local": "Templo Central",
            "observacoes": "Instrucoes de teste automatizado",
            "status": "publicada"
        }
        res = client_admin.post("/escalas/nova", data=payload_escala, follow_redirects=True)
        assert res.status_code == 200
        escala_criada = Escala.query.filter_by(titulo="Culto Especial de Teste Automatizado").first()
        assert escala_criada is not None, "Escala nao foi persistida no banco."
        print(f"  [OK] Escala criada com sucesso (ID: {escala_criada.id}).")

        # -------------------------------------------------------------------
        # [3/10] Gestão de Equipes & Funções
        # -------------------------------------------------------------------
        print("\n[3/10] Testando equipes e funcoes...")
        equipe = Equipe.query.first()
        assert equipe is not None, "Nenhuma equipe encontrada para o teste."
        funcao = equipe.funcoes[0] if equipe.funcoes else None
        assert funcao is not None, "Nenhuma funcao encontrada para a equipe."
        print(f"  [OK] Equipe '{equipe.nome}' e funcao '{funcao.nome}' validadas.")

        # -------------------------------------------------------------------
        # [4/10] Inclusão de Voluntário na Escala
        # -------------------------------------------------------------------
        print("\n[4/10] Testando inclusao de voluntario na escala...")
        membro = Member.query.filter((Member.status.is_(None)) | (Member.status == "Ativo")).first()
        assert membro is not None, "Nenhum membro ativo para escalar."

        payload_item = {
            "equipe_id": equipe.id,
            "funcao_id": funcao.id,
            "membro_id": membro.id,
            "observacao": "Primeiro ensaio 18h"
        }
        res = client_admin.post(f"/escalas/{escala_criada.id}/adicionar-item", data=payload_item, follow_redirects=True)
        assert res.status_code == 200

        item_escalado = EscalaItem.query.filter_by(escala_id=escala_criada.id, membro_id=membro.id).first()
        assert item_escalado is not None, "Item da escala nao foi persistido."
        assert item_escalado.status == "pendente"
        print(f"  [OK] Voluntario '{membro.nome}' escalado com sucesso.")

        # -------------------------------------------------------------------
        # [5/10] Detecção de Conflito de Horário Concorrente
        # -------------------------------------------------------------------
        print("\n[5/10] Testando deteccao de conflitos de horario...")
        segunda_escala = Escala(
            titulo="Outra Atividade Simultanea",
            data=data_escala,
            hora_inicio="19:00",
            hora_fim="21:00",
            status="publicada"
        )
        db.session.add(segunda_escala)
        db.session.commit()

        analise_conflito = EscalaService.verificar_conflitos(
            membro_id=membro.id,
            escala_data=data_escala,
            hora_inicio="20:00",
            hora_fim="21:30",
            escala_id=segunda_escala.id
        )
        assert analise_conflito["possui_conflito"] is True, "Deveria acusar choque de horario."
        print(f"  [OK] Conflito detectado com precisao: {analise_conflito['conflitos'][0]}")

        # -------------------------------------------------------------------
        # [6/10] Fluxo de Substituição Preservando Histórico
        # -------------------------------------------------------------------
        print("\n[6/10] Testando fluxo de substituicao com historico...")
        outro_membro = Member.query.filter(Member.id != membro.id, (Member.status.is_(None)) | (Member.status == "Ativo")).first()
        assert outro_membro is not None, "Segundo membro nao encontrado para substituicao."

        payload_subst = {
            "novo_membro_id": outro_membro.id,
            "motivo": "Imprevisto pessoal no trabalho"
        }
        res = client_admin.post(f"/escalas/item/{item_escalado.id}/substituir", data=payload_subst, follow_redirects=True)
        assert res.status_code == 200

        db.session.refresh(item_escalado)
        assert item_escalado.membro_id == outro_membro.id, "Membro atual nao foi atualizado."
        assert item_escalado.membro_original_id == membro.id, "Membro original nao foi preservado!"
        assert item_escalado.status == "substituido"
        assert "trabalho" in item_escalado.motivo_substituicao
        print(f"  [OK] Substituicao efetuada com sucesso. Original: {membro.nome} -> Substituto: {outro_membro.nome}.")

        # -------------------------------------------------------------------
        # [7/10] Duplicação Segura de Escala (Clonagem com 1 Clique)
        # -------------------------------------------------------------------
        print("\n[7/10] Testando clonagem/duplicacao de escala...")
        nova_data_clonada = data_escala + timedelta(days=7)
        payload_duplicar = {
            "nova_data": nova_data_clonada.strftime("%Y-%m-%d"),
            "nova_hora_inicio": "19:30",
            "nova_hora_fim": "21:30",
            "novo_titulo": "Escala Clonada Teste"
        }
        res = client_admin.post(f"/escalas/{escala_criada.id}/duplicar", data=payload_duplicar, follow_redirects=True)
        assert res.status_code == 200

        escala_clonada = Escala.query.filter_by(titulo="Escala Clonada Teste").first()
        assert escala_clonada is not None, "Escala clonada nao encontrada."
        assert escala_clonada.status == "rascunho", "Escala clonada deveria iniciar como rascunho."
        assert len(escala_clonada.itens) == 1, "Itens deveriam ter sido clonados."
        assert escala_clonada.itens[0].status == "pendente", "Item clonado deveria ser pendente."
        print("  [OK] Duplicacao de escala validada com sucesso.")

        # -------------------------------------------------------------------
        # [8/10] Página Pública & Confirmação por Token sem Login
        # -------------------------------------------------------------------
        print("\n[8/10] Testando pagina publica por token sem autenticacao...")
        client_publico = app.test_client()

        res_publico = client_publico.get(f"/escalas/publico/{escala_criada.public_token}")
        assert res_publico.status_code == 200
        assert "Culto Especial de Teste Automatizado" in res_publico.get_data(as_text=True)
        print("  [OK] Pagina publica de voluntario acessivel sem login (Status 200).")

        res_confirma = client_publico.post(
            f"/escalas/publico/{escala_criada.public_token}/item/{item_escalado.id}/confirmar",
            follow_redirects=True
        )
        assert res_confirma.status_code == 200
        db.session.refresh(item_escalado)
        assert item_escalado.status == "confirmado", "Status deveria ser confirmado."
        print("  [OK] Confirmacao de presenca publica pelo voluntario validada.")

        # -------------------------------------------------------------------
        # [9/10] Versão para Impressão de Mural
        # -------------------------------------------------------------------
        print("\n[9/10] Testando versao de impressao A4 (/imprimir)...")
        res_print = client_admin.get(f"/escalas/{escala_criada.id}/imprimir")
        assert res_print.status_code == 200
        assert "Mural de Escala" in res_print.get_data(as_text=True)
        print("  [OK] Template de impressao A4 gerado com sucesso (Status 200).")

        # -------------------------------------------------------------------
        # [10/10] Controle de Acesso / RBAC
        # -------------------------------------------------------------------
        print("\n[10/10] Testando controle de acesso e permissoes...")
        client_admin.get("/logout")

        usuario_sem_perm = User.query.filter_by(is_admin=False).first()
        assert usuario_sem_perm is not None, "Nenhum usuario nao-admin encontrado."

        client_non_admin = app.test_client()
        with client_non_admin.session_transaction() as sess:
            sess['_user_id'] = str(usuario_sem_perm.id)
            sess['_fresh'] = True

        res_bloqueado = client_non_admin.get("/escalas/", follow_redirects=False)
        assert res_bloqueado.status_code in [302, 403], f"Acesso indevido: {res_bloqueado.status_code}"
        print("  [OK] Usuario sem permissao de escalas devidamente bloqueado (Redirect 302).")

        # Limpeza dos dados temporários criados nos testes
        try:
            if escala_clonada:
                db.session.delete(escala_clonada)
            if segunda_escala:
                db.session.delete(segunda_escala)
            if escala_criada:
                db.session.delete(escala_criada)
            if usuario_sem_perm:
                db.session.delete(usuario_sem_perm)
            db.session.commit()
        except Exception:
            db.session.rollback()

        print("\n" + "=" * 70)
        print("TODOS OS 10 TESTES DO MODULO DE ESCALAS PASSARAM COM SUCESSO!")
        print("=" * 70)
        return True

if __name__ == "__main__":
    sucesso = run_tests()
    if not sucesso:
        sys.exit(1)
