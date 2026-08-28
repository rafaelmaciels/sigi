#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SiGI — Testes Automatizados: Transformar Membro em Usuário & Controle de Acesso EBD
"""

import sys
import os
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import Member, User, Permission, UserPermission
from app.models.ebd import EbdClasse, EbdProfessor, EbdPeriodo

app = create_app()
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False

def test_suite():
    print("\n" + "=" * 70)
    print("  🧪 INICIANDO SUÍTE DE TESTES: MEMBRO ↔ USUÁRIO & SEGURANÇA EBD")
    print("=" * 70 + "\n")

    with app.test_client() as client:
        with app.app_context():
            # 1. Criação de Dados para o Teste
            db.create_all()

            # Cria Administrador
            admin = User.query.filter_by(email="admin_teste@sigi.com").first()
            if not admin:
                admin = User(nome="Admin Teste", email="admin_teste@sigi.com", is_admin=True, ativo=True)
                admin.set_password("Admin@123456")
                db.session.add(admin)
                db.session.commit()

            # Cria Membro Pastor Carlos
            membro_carlos = Member.query.filter_by(email="carlos_teste@sigi.com").first()
            if not membro_carlos:
                membro_carlos = Member(
                    nome="Pr. Carlos Eduardo Teste",
                    email="carlos_teste@sigi.com",
                    funcao="Pastor",
                    status="Ativo",
                    telefone="(11) 99999-0001"
                )
                db.session.add(membro_carlos)
                db.session.commit()

            # Cria Membro Diácono André
            membro_andre = Member.query.filter_by(email="andre_teste@sigi.com").first()
            if not membro_andre:
                membro_andre = Member(
                    nome="Diác. André Teste",
                    email="andre_teste@sigi.com",
                    funcao="Diácono",
                    status="Ativo",
                    telefone="(11) 99999-0002"
                )
                db.session.add(membro_andre)
                db.session.commit()

            # Cria Período e Classes
            periodo = EbdPeriodo.query.first()
            if not periodo:
                periodo = EbdPeriodo(nome="Período Teste 2026", data_inicio=date(2026, 1, 1), data_fim=date(2026, 12, 31), status="em_andamento")
                db.session.add(periodo)
                db.session.commit()

            classe_adultos = EbdClasse.query.filter_by(nome="Classe Adultos Teste").first()
            if not classe_adultos:
                classe_adultos = EbdClasse(nome="Classe Adultos Teste", periodo_id=periodo.id, sala="Sala 01", status="ativa")
                db.session.add(classe_adultos)
                db.session.commit()

            classe_jovens = EbdClasse.query.filter_by(nome="Classe Jovens Teste").first()
            if not classe_jovens:
                classe_jovens = EbdClasse(nome="Classe Jovens Teste", periodo_id=periodo.id, sala="Sala 02", status="ativa")
                db.session.add(classe_jovens)
                db.session.commit()

            # Vincula Pr. Carlos como Professor APENAS de Adultos
            vinculo_carlos = EbdProfessor.query.filter_by(classe_id=classe_adultos.id, membro_id=membro_carlos.id).first()
            if not vinculo_carlos:
                vinculo_carlos = EbdProfessor(classe_id=classe_adultos.id, membro_id=membro_carlos.id, cargo="principal", status="ativo")
                db.session.add(vinculo_carlos)
                db.session.commit()

            # Vincula André como Professor de Jovens
            vinculo_andre = EbdProfessor.query.filter_by(classe_id=classe_jovens.id, membro_id=membro_andre.id).first()
            if not vinculo_andre:
                vinculo_andre = EbdProfessor(classe_id=classe_jovens.id, membro_id=membro_andre.id, cargo="principal", status="ativo")
                db.session.add(vinculo_andre)
                db.session.commit()

            carlos_id = membro_carlos.id
            carlos_nome = membro_carlos.nome
            andre_id = membro_andre.id
            adultos_id = classe_adultos.id
            jovens_id = classe_jovens.id

            print("✅ [Passo 1] Ambiente e registros de teste preparados.")

        # 2. Login como Administrador
        res_login = client.post("/login", data={"email": "admin_teste@sigi.com", "senha": "Admin@123456"}, follow_redirects=True)
        assert res_login.status_code == 200
        print("✅ [Passo 2] Login de Administrador autenticado com sucesso.")

        # 3. Teste: Transformar Membro (Pr. Carlos) em Usuário (Perfil Professor EBD)
        with app.app_context():
            usr_old = User.query.filter((User.email == "carlos_user@sigi.com") | (User.member_id == carlos_id)).all()
            for u in usr_old:
                db.session.delete(u)
            db.session.commit()

        res_criar = client.post(
            f"/membros/{carlos_id}/tornar-usuario",
            data={
                "email": "carlos_user@sigi.com",
                "senha": "SenhaForte123",
                "confirmar_senha": "SenhaForte123",
                "perfil": "professor_ebd"
            },
            follow_redirects=True
        )
        assert res_criar.status_code == 200

        with app.app_context():
            usuario_carlos = User.query.filter_by(email="carlos_user@sigi.com").first()
            assert usuario_carlos is not None, "Usuário deveria ter sido criado"
            assert usuario_carlos.member_id == carlos_id, "Usuário deve estar vinculado ao membro"
            assert usuario_carlos.member.nome == carlos_nome, "Relacionamento bidirecional deve funcionar"
            assert usuario_carlos.has_permission("ebd", "view") is True, "Deve ter permissão ebd:view"
            assert usuario_carlos.has_permission("ebd", "frequencia") is True, "Deve ter permissão ebd:frequencia"
            assert usuario_carlos.has_permission("financeiro", "view") is False, "NÃO deve ter permissão de financeiro"
            assert usuario_carlos.is_admin is False, "Não deve ser admin geral"
            print("✅ [Passo 3] Membro transformado em Usuário com perfil 'Professor EBD' e permissões corretas.")

        # 4. Teste: Bloqueio de Criar Segundo Usuário para o Mesmo Membro
        res_dup_membro = client.post(
            f"/membros/{carlos_id}/tornar-usuario",
            data={
                "email": "carlos_segundo@sigi.com",
                "senha": "SenhaForte123",
                "confirmar_senha": "SenhaForte123",
                "perfil": "professor_ebd"
            },
            follow_redirects=True
        )
        assert "já possui uma conta de usuário" in res_dup_membro.get_data(as_text=True)
        print("✅ [Passo 4] Bloqueio de segundo usuário para o mesmo membro funcionando.")

        # 5. Teste: Bloqueio de E-mail Duplicado
        res_dup_email = client.post(
            f"/membros/{andre_id}/tornar-usuario",
            data={
                "email": "carlos_user@sigi.com", # mesmo email
                "senha": "SenhaForte123",
                "confirmar_senha": "SenhaForte123",
                "perfil": "professor_ebd"
            },
            follow_redirects=True
        )
        assert "já está em uso por outro usuário" in res_dup_email.get_data(as_text=True)
        print("✅ [Passo 5] Bloqueio de e-mail duplicado funcionando.")

        # 6. Teste: Desativar Acesso do Usuário sem alterar status do Membro
        res_toggle = client.post(f"/membros/{carlos_id}/toggle-usuario", follow_redirects=True)
        assert res_toggle.status_code == 200
        with app.app_context():
            u_check = User.query.filter_by(email="carlos_user@sigi.com").first()
            m_check = Member.query.get(carlos_id)
            assert u_check.ativo is False, "Usuário deve estar inativo"
            assert m_check.status == "Ativo", "Membro deve continuar ativo"
            print("✅ [Passo 6] Desativação do usuário mantém o membro intacto na congregação.")

        # Reativa o usuário
        client.post(f"/membros/{carlos_id}/toggle-usuario", follow_redirects=True)

        # 7. Logout do Admin e Login como Professor Carlos
        client.get("/logout", follow_redirects=True)
        res_prof_login = client.post("/login", data={"email": "carlos_user@sigi.com", "senha": "SenhaForte123"}, follow_redirects=True)
        assert res_prof_login.status_code == 200
        print("✅ [Passo 7] Professor autenticado com suas próprias credenciais.")

        # 8. Professor acessa 'Minhas Classes' e sua própria classe (Adultos)
        res_minhas = client.get("/ebd/minhas-classes")
        assert res_minhas.status_code == 200
        assert "Classe Adultos Teste" in res_minhas.get_data(as_text=True)
        assert "Classe Jovens Teste" not in res_minhas.get_data(as_text=True), "Não deve ver a classe de outro professor"
        print("✅ [Passo 8] Portal 'Minhas Classes' exibindo apenas as turmas vinculadas ao professor.")

        # 9. Professor acessa os detalhes de sua classe (Permitido)
        res_det_propria = client.get(f"/ebd/classes/{adultos_id}")
        assert res_det_propria.status_code == 200
        print("✅ [Passo 9] Acesso à própria classe permitido com sucesso.")

        # 10. Professor tenta acessar classe de outro professor (Jovens) -> Deve ser bloqueado!
        res_det_alheia = client.get(f"/ebd/classes/{jovens_id}", follow_redirects=True)
        assert "Acesso restrito" in res_det_alheia.get_data(as_text=True)
        print("✅ [Passo 10] Segurança no backend bloqueou tentativa de acessar classe de outro professor.")

    print("\n" + "=" * 70)
    print("  🎉 TODOS OS 10 TESTES PASSARAM COM 100% DE SUCESSO!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    test_suite()
