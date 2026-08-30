import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from app import create_app, db
from app.models import User, Member, Permission, UserPermission
from app.models.ebd import EbdConfig, EbdPeriodo, EbdClasse, EbdProfessor, EbdMatricula, EbdAula, EbdFrequencia

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

def run_tests():
    print("=" * 70)
    print("🧪 INICIANDO TESTES AUTOMATIZADOS DO MÓDULO EBD")
    print("=" * 70)

    with app.test_client() as client:
        with app.app_context():
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                print("❌ Nenhum usuário admin encontrado para os testes.")
                return

            # Login como Admin
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
                sess['_fresh'] = True

            print("\n[1/8] Testando Acesso ao Dashboard da EBD...")
            res = client.get("/ebd/")
            assert res.status_code == 200, f"Erro ao carregar Dashboard EBD: status {res.status_code}"
            assert "Escola Bíblica Dominical" in res.get_data(as_text=True)
            print("  ✅ Dashboard EBD carregado com sucesso (Status 200).")

            print("\n[2/8] Testando Listagem de Classes...")
            res = client.get("/ebd/classes")
            assert res.status_code == 200
            assert "Classes" in res.get_data(as_text=True)
            print("  ✅ Listagem de classes validada com sucesso.")

            print("\n[3/8] Testando Criação de Nova Classe...")
            periodo = EbdPeriodo.query.first()
            nova_classe_data = {
                "nome": "Classe Teste Automatizado",
                "periodo_id": periodo.id,
                "faixa_etaria": "Adultos",
                "sala": "Sala Teste",
                "capacidade": 25,
                "status": "ativa",
                "descricao": "Classe temporária para validação de testes automatizados."
            }
            res = client.post("/ebd/classes/nova", data=nova_classe_data, follow_redirects=True)
            assert res.status_code == 200
            classe_criada = EbdClasse.query.filter_by(nome="Classe Teste Automatizado").first()
            assert classe_criada is not None, "Classe não foi persistida no banco."
            print(f"  ✅ Classe criada com sucesso (ID: {classe_criada.id}).")

            print("\n[4/8] Testando Matrícula de Aluno...")
            membro = Member.query.filter_by(status="Ativo").first()
            if not membro:
                membro = Member.query.first()
            # Limpa qualquer matricula anterior deste membro nesta classe
            EbdMatricula.query.filter_by(classe_id=classe_criada.id, membro_id=membro.id).delete()
            db.session.commit()
            mat_data = {
                "classe_id": classe_criada.id,
                "membro_id": membro.id,
                "data_matricula": date.today().strftime("%Y-%m-%d"),
                "status": "ativo",
                "observacoes": "Matrícula de teste automatizado."
            }
            res = client.post("/ebd/matriculas/nova", data=mat_data, follow_redirects=True)
            assert res.status_code == 200
            mat_criada = EbdMatricula.query.filter_by(classe_id=classe_criada.id, membro_id=membro.id, status="ativo").first()
            assert mat_criada is not None, "Matrícula não foi persistida no banco."
            print(f"  ✅ Aluno {membro.nome} matriculado com sucesso na classe {classe_criada.nome}.")

            print("\n[5/8] Testando Criação de Aula e Abertura de Chamada...")
            aula_data = {
                "classe_id": classe_criada.id,
                "data_aula": date.today().strftime("%Y-%m-%d"),
                "numero_licao": "Lição 99",
                "tema": "Tema Teste Automatizado",
                "resumo_conteudo": "Conteúdo de teste.",
                "status": "realizada",
                "observacoes": "Teste"
            }
            res = client.post("/ebd/aulas/nova", data=aula_data, follow_redirects=True)
            assert res.status_code == 200
            aula_criada = EbdAula.query.filter_by(classe_id=classe_criada.id, tema="Tema Teste Automatizado").first()
            assert aula_criada is not None, "Aula não foi persistida no banco."
            print(f"  ✅ Aula criada com sucesso (ID: {aula_criada.id}).")

            print("\n[6/8] Testando Lançamento e Atualização de Chamada...")
            chamada_data = {
                f"status_{mat_criada.id}": "falta_justificada",
                f"motivo_{mat_criada.id}": "Viagem",
                f"justificativa_{mat_criada.id}": "Viagem a trabalho",
                f"obs_{mat_criada.id}": "Solicitou gravação da aula"
            }
            res = client.post(f"/ebd/aulas/{aula_criada.id}/chamada", data=chamada_data, follow_redirects=True)
            assert res.status_code == 200
            freq_salva = EbdFrequencia.query.filter_by(aula_id=aula_criada.id, matricula_id=mat_criada.id).first()
            assert freq_salva is not None, "Frequência não foi gravada."
            assert freq_salva.status_presenca == "falta_justificada"
            assert freq_salva.motivo_falta == "Viagem"
            print("  ✅ Chamada registrada e justificada com sucesso no banco de dados.")

            print("\n[7/8] Testando Mapa de Frequência e Relatório Geral...")
            res_mapa = client.get(f"/ebd/relatorios/mapa-frequencia?classe_id={classe_criada.id}")
            assert res_mapa.status_code == 200
            assert "Mapa de Frequência" in res_mapa.get_data(as_text=True)
            
            res_geral = client.get("/ebd/relatorios/geral")
            assert res_geral.status_code == 200
            assert "Relatório Consolidado" in res_geral.get_data(as_text=True)
            print("  ✅ Relatórios e mapas de frequência gerados com sucesso.")

            print("\n[8/8] Testando Isolamento e Limpeza dos Dados de Teste...")
            EbdFrequencia.query.filter_by(aula_id=aula_criada.id).delete()
            EbdAula.query.filter_by(classe_id=classe_criada.id).delete()
            EbdMatricula.query.filter_by(classe_id=classe_criada.id).delete()
            EbdClasse.query.filter_by(nome="Classe Teste Automatizado").delete()
            db.session.commit()
            assert EbdClasse.query.filter_by(nome="Classe Teste Automatizado").first() is None
            print("  ✅ Limpeza concluída sem afetar dados existentes.")

    print("\n" + "=" * 70)
    print("🎉 TODOS OS TESTES DO MÓDULO EBD PASSARAM COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
