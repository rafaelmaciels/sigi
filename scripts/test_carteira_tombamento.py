import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models.member import Member
from app.models.patrimonio import Patrimonio
from app.models.user import User
from app.routes.member.member import gerar_proximo_numero_carteira, calcular_validade_carteira
from app.routes.patrimonio.patrimonio import gerar_proxima_etiqueta_patrimonio, obter_prefixo_categoria

app = create_app()

with app.test_client() as client:
    with app.app_context():
        # Obter usuário admin para a sessão de teste
        admin = User.query.filter_by(is_admin=True).first()
        assert admin is not None, "Admin não encontrado!"

    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin.id)
        sess['_fresh'] = True

    print("\n--- TESTE 1: Validação de Numeração e Validade de Carteirinhas ---")
    with app.app_context():
        prox_carteira = gerar_proximo_numero_carteira()
        print(f"Próxima carteira calculada: {prox_carteira}")
        assert len(prox_carteira) == 5, "Carteira deve ter 5 dígitos (ex: 00001)"
        assert prox_carteira.isdigit(), "Carteira deve ser numérica"

        hoje = date.today()
        val = calcular_validade_carteira(hoje)
        dias = (val - hoje).days
        print(f"Validade para hoje ({hoje}): {val} ({dias} dias)")
        assert dias == 365, f"Validade deve ser de exatamente 365 dias, obtido: {dias}"

    print("\n--- TESTE 2: Requisição GET em /membros/carteira/ e /membros/carteira/<id> ---")
    res1 = client.get("/membros/carteira/")
    assert res1.status_code == 200, f"Erro ao acessar /membros/carteira/: {res1.status_code}"
    assert b"Carteira de Membro Oficial" in res1.data
    assert b"365 DIAS" in res1.data
    print("GET /membros/carteira/ -> 200 OK com exibição correta!")

    with app.app_context():
        membro_exemplo = Member.query.filter_by(numero_carteira="00001").first()
        if not membro_exemplo:
            membro_exemplo = Member.query.first()

    res2 = client.get(f"/membros/carteira/{membro_exemplo.id}")
    assert res2.status_code == 200, f"Erro ao acessar carteira individual: {res2.status_code}"
    assert membro_exemplo.numero_carteira.encode() in res2.data
    print(f"GET /membros/carteira/{membro_exemplo.id} -> 200 OK exibindo carteira {membro_exemplo.numero_carteira}!")

    print("\n--- TESTE 3: Validação de Etiquetas de Tombamento de Patrimônio ---")
    with app.app_context():
        assert gerar_proxima_etiqueta_patrimonio("Imóveis") == "PAT-IMO-004"
        assert gerar_proxima_etiqueta_patrimonio("Veículos") == "PAT-VEI-003"
        assert gerar_proxima_etiqueta_patrimonio("Equipamentos") == "PAT-EQU-013"
        assert gerar_proxima_etiqueta_patrimonio("Móveis") == "PAT-MOV-006"
        print("Geração sequencial de etiquetas de tombamento validada com sucesso!")

    print("\n--- TESTE 4: API JSON /patrimonios/api/proxima-etiqueta ---")
    api_res = client.get("/patrimonios/api/proxima-etiqueta?categoria=Equipamentos")
    assert api_res.status_code == 200
    json_data = api_res.get_json()
    assert json_data["sucesso"] is True
    assert json_data["etiqueta"] == "PAT-EQU-013"
    print(f"API retornou JSON válido: {json_data}")

    api_res2 = client.get("/patrimonios/api/proxima-etiqueta?categoria=Móveis")
    assert api_res2.status_code == 200
    json_data2 = api_res2.get_json()
    assert json_data2["etiqueta"] == "PAT-MOV-006"
    print(f"API retornou para Móveis: {json_data2['etiqueta']}")

    print("\n--- TESTE 5: Formulário de Novo Patrimônio com Pré-Preenchimento ---")
    form_res = client.get("/patrimonios/novo")
    assert form_res.status_code == 200
    assert b"id=\"numeroEtiqueta\"" in form_res.data
    assert b"categoriaSelect" in form_res.data
    print("Formulário de novo patrimônio carregado com campos inteligentes!")

    print("\n=======================================================")
    print("  TODOS OS 5 TESTES AUTOMATIZADOS FORAM APROVADOS!  ")
    print("=======================================================")
