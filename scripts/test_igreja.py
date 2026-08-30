import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User, Permission, UserPermission, Igreja

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

def run_tests():
    with app.app_context():
        # Setup Admin
        admin = User.query.filter_by(email="rafael@sigi.com").first()
        if not admin:
            admin = User(nome="Admin Teste", email="rafael@sigi.com", is_admin=True, ativo=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        # Limpar registros existentes de igreja para o teste inicial
        Igreja.query.delete()
        db.session.commit()

        print("=" * 60)
        print("INICIANDO SUÍTE DE TESTES: MÓDULO DADOS DA IGREJA")
        print("=" * 60)

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
                sess['_fresh'] = True

            # 1. Testar página sem registros
            print("\n[TESTE 1] Acessar /configuracoes/igreja/ sem registro cadastrado...")
            res = client.get('/configuracoes/igreja/')
            assert res.status_code == 200, f"Esperado 200, obtido {res.status_code}"
            assert "Nenhum dado cadastrado" in res.data.decode('utf-8')
            print("  [OK] Pagina renderizada com sucesso (estado vazio, HTTP 200).")

            # 2. Testar página de cadastro/edição GET
            print("\n[TESTE 2] Acessar formulario /configuracoes/igreja/editar (GET)...")
            res = client.get('/configuracoes/igreja/editar')
            assert res.status_code == 200, f"Esperado 200, obtido {res.status_code}"
            assert "Cadastrar Dados da Igreja" in res.data.decode('utf-8')
            print("  [OK] Formulario de cadastro renderizado com sucesso (HTTP 200).")

            # 3. Testar cadastro via POST
            print("\n[TESTE 3] Cadastrar dados da igreja via POST...")
            form_payload = {
                "nome": "Igreja Evangelica Comunidade da Graca — Sede",
                "cnpj": "12.345.678/0001-90",
                "endereco": "Av. Principal, 1000 - Centro",
                "telefone": "(11) 99999-8888",
                "email": "contato@igrejadagraca.com.br",
                "site": "www.igrejadagraca.com.br",
                "pastor_responsavel": "Pr. Carlos Silva",
                "ano_fundacao": 1995,
                "versiculo_tema": "Tudo posso naquele que me fortalece."
            }
            res = client.post('/configuracoes/igreja/editar', data=form_payload, follow_redirects=False)
            assert res.status_code == 302, f"Esperado redirecionamento 302, obtido {res.status_code}"
            
            igreja_db = Igreja.query.first()
            assert igreja_db is not None, "Registro da igreja deveria ter sido criado no banco"
            assert igreja_db.nome == form_payload["nome"]
            assert igreja_db.cnpj == form_payload["cnpj"]
            print("  [OK] Dados da igreja gravados no banco de dados com sucesso.")

            # 4. Testar visualização com registro preenchido (CENÁRIO DO BUG ANTERIOR)
            print("\n[TESTE 4] Acessar /configuracoes/igreja/ com dados preenchidos (validacao do modal de exclusao e url_for)...")
            res = client.get('/configuracoes/igreja/')
            assert res.status_code == 200, f"Esperado 200, obtido {res.status_code}"
            html_content = res.data.decode('utf-8')
            assert "Igreja Evangelica Comunidade da Graca" in html_content
            assert "12.345.678/0001-90" in html_content
            assert "Pr. Carlos Silva" in html_content
            assert "confirmDeleteIgreja" in html_content
            assert "/configuracoes/igreja/excluir" in html_content
            print("  [OK] Pagina e modal de confirmacao renderizados perfeitamente com todos os url_for resolvidos (HTTP 200).")

            # 5. Testar edição do registro
            print("\n[TESTE 5] Editar dados da igreja existente via POST...")
            form_payload["pastor_responsavel"] = "Pr. Carlos Silva & Pra. Maria"
            res = client.post('/configuracoes/igreja/editar', data=form_payload, follow_redirects=True)
            assert res.status_code == 200
            assert "Pr. Carlos Silva &amp; Pra. Maria" in res.data.decode('utf-8') or "Pr. Carlos Silva & Pra. Maria" in res.data.decode('utf-8')
            print("  [OK] Edicao realizada e refletida na pagina com sucesso.")

            # 6. Testar exclusão via endpoint /excluir
            print("\n[TESTE 6] Excluir dados da igreja via POST /configuracoes/igreja/excluir...")
            res = client.post('/configuracoes/igreja/excluir', follow_redirects=True)
            assert res.status_code == 200
            assert Igreja.query.first() is None, "Registro da igreja deveria ter sido removido"
            assert "Nenhum dado cadastrado" in res.data.decode('utf-8')
            print("  [OK] Exclusao executada com sucesso e pagina retornou ao estado inicial.")

        print("\n" + "=" * 60)
        print("TODOS OS TESTES DO MODULO 'DADOS DA IGREJA' PASSARAM COM 100%!")
        print("=" * 60)


if __name__ == "__main__":
    run_tests()
