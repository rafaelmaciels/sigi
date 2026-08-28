#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Verificador de Saúde e Integridade do Sistema (Healthcheck)
Valida ambiente, banco de dados, permissões de escrita, chave secreta e arquivos estáticos.

Uso:
  python healthcheck.py
"""

import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def check_ok(msg):
    print(f"  ✅ [OK] {msg}")

def check_warn(msg):
    print(f"  ⚠️  [AVISO] {msg}")

def check_error(msg):
    print(f"  ❌ [FALHA] {msg}")

def main():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO E VERIFICAÇÃO DE SAÚDE DO SIGI")
    print("=" * 70)

    erros_criticos = 0
    avisos = 0

    # 1. Checagem do arquivo .env
    print("\n[1/6] Verificando Variáveis de Ambiente...")
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        check_ok("Arquivo '.env' presente na raiz do projeto.")
    else:
        check_error("Arquivo '.env' NÃO encontrado! Execute 'python install.py'.")
        erros_criticos += 1

    # 2. Inicialização do App Flask e Configurações
    print("\n[2/6] Verificando Configurações do Flask e SECRET_KEY...")
    try:
        from app import create_app, db
        from config import get_config
        app = create_app(get_config())
        
        secret = app.config.get("SECRET_KEY", "")
        if not secret or secret == "dev-secret-key-change-in-production":
            check_warn("SECRET_KEY está utilizando o valor padrão inseguro. Defina uma chave forte no .env.")
            avisos += 1
        else:
            check_ok("SECRET_KEY configurada adequadamente.")
            
        env_mode = app.config.get("ENV") or os.environ.get("FLASK_ENV", "production")
        check_ok(f"Modo de Operação: {env_mode.upper()}")
    except Exception as e:
        check_error(f"Falha ao carregar a aplicação Flask: {e}")
        erros_criticos += 1
        sys.exit(1)

    # 3. Conexão com Banco de Dados
    print("\n[3/6] Testando Conectividade com o Banco de Dados...")
    try:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            check_ok("Conexão com o banco de dados estabelecida com sucesso.")
            
            from app.models import User, Member, Financeiro, EbdClasse
            total_users = User.query.count()
            total_membros = Member.query.count()
            total_admin = User.query.filter_by(is_admin=True).count()
            
            check_ok(f"Estatísticas: {total_users} usuários ({total_admin} administradores), {total_membros} membros cadastrados.")
            
            if total_admin == 0:
                check_warn("Nenhum usuário administrador encontrado no banco!")
                avisos += 1
    except Exception as e:
        check_error(f"Não foi possível conectar ao banco de dados: {e}")
        erros_criticos += 1

    # 4. Permissões de Escrita em Diretórios
    print("\n[4/6] Verificando Permissões de Escrita...")
    diretorios = [
        BASE_DIR / "instance",
        BASE_DIR / "app" / "static" / "uploads",
        BASE_DIR / "logs",
        BASE_DIR / "backups"
    ]
    for d in diretorios:
        d.mkdir(parents=True, exist_ok=True)
        teste_arquivo = d / ".healthcheck_write_test"
        try:
            teste_arquivo.write_text("test")
            teste_arquivo.unlink()
            check_ok(f"Diretório '{d.relative_to(BASE_DIR)}': Permissão de escrita OK.")
        except Exception as e:
            check_error(f"Sem permissão de escrita em '{d.relative_to(BASE_DIR)}': {e}")
            erros_criticos += 1

    # 5. Arquivos Estáticos Essenciais
    print("\n[5/6] Verificando Integridade dos Arquivos Estáticos...")
    arquivos_estaticos = [
        BASE_DIR / "app" / "static" / "css" / "bootstrap.min.css",
        BASE_DIR / "app" / "static" / "css" / "base.css",
        BASE_DIR / "app" / "static" / "js" / "bootstrap.bundle.min.js",
        BASE_DIR / "app" / "static" / "js" / "chart.min.js"
    ]
    for static_file in arquivos_estaticos:
        if static_file.exists():
            check_ok(f"Arquivo estático presente: {static_file.name}")
        else:
            check_warn(f"Arquivo estático ausente: {static_file.relative_to(BASE_DIR)}")
            avisos += 1

    # 6. Diagnóstico Final
    print("\n" + "=" * 70)
    if erros_criticos == 0:
        print(f"🎉 HEALTHCHECK APROVADO! O SiGI está 100% operacional ({avisos} aviso(s)).")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"❌ HEALTHCHECK REPROVADO! Foram encontrados {erros_criticos} erro(s) crítico(s).")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
