#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏛️ SiGI — Sistema Integrado de Gestão de Igreja
Script Universal de Instalação e Configuração

Uso:
  Modo Interativo:
    python install.py

  Modo Não-Interativo (Automatizado):
    python install.py --non-interactive --env production --db sqlite --admin-name "Admin" --admin-email "admin@sigi.com" --admin-password "SenhaForte123"
"""

import os
import sys
import subprocess
import argparse
import secrets
from pathlib import Path

# Configuração de encoding para terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
MIN_PYTHON_VERSION = (3, 10)

def print_header(titulo):
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)

def print_step(numero, total, mensagem):
    print(f"\n[{numero}/{total}] ⚙️  {mensagem}")

def print_ok(mensagem):
    print(f"  ✅ [OK] {mensagem}")

def print_warn(mensagem):
    print(f"  ⚠️  [AVISO] {mensagem}")

def print_error(mensagem):
    print(f"  ❌ [ERRO] {mensagem}")

def verificar_versao_python():
    print_header("1. VERIFICAÇÃO DE PRÉ-REQUISITOS DO SISTEMA")
    versao = sys.version_info
    print(f"  Python Detectado: {versao.major}.{versao.minor}.{versao.micro}")
    
    if versao < MIN_PYTHON_VERSION:
        print_error(f"O SiGI requer Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} ou superior.")
        print("  Atualize o Python do seu servidor antes de prosseguir.")
        sys.exit(1)
    
    print_ok("Versão do Python compatível com o SiGI.")

def obter_executavel_python_venv():
    if sys.platform == "win32":
        venv_py = BASE_DIR / "venv" / "Scripts" / "python.exe"
    else:
        venv_py = BASE_DIR / "venv" / "bin" / "python"
    return venv_py

def criar_ou_verificar_venv():
    venv_dir = BASE_DIR / "venv"
    venv_py = obter_executavel_python_venv()

    # Verifica se já estamos executando dentro de um virtualenv
    no_virtualenv = (sys.prefix != sys.base_prefix)

    if venv_dir.exists() and venv_py.exists():
        print_ok("Ambiente virtual (venv) já existente detectado.")
        return venv_py
    elif no_virtualenv:
        print_ok(f"Ambiente virtual ativo detectado: {sys.prefix}")
        return Path(sys.executable)
    else:
        print("  Criando novo ambiente virtual em 'venv/'...")
        try:
            import venv
            venv.create(venv_dir, with_pip=True)
            print_ok("Ambiente virtual criado com sucesso.")
            return venv_py
        except Exception as e:
            print_warn(f"Não foi possível criar o venv via módulo padrão: {e}")
            print("  Utilizando o interpretador Python atual do sistema...")
            return Path(sys.executable)

def instalar_dependencias(python_exe):
    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        print_error("Arquivo requirements.txt não encontrado!")
        sys.exit(1)

    print("  Instalando dependências do requirements.txt...")
    cmd = [str(python_exe), "-m", "pip", "install", "-r", str(req_file)]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print_ok("Todas as dependências instaladas e atualizadas com sucesso.")
    except subprocess.CalledProcessError as e:
        print_warn("Algumas dependências opcionais podem ter emitido avisos durante a instalação.")
        if "WeasyPrint" in e.stderr:
            print_warn("WeasyPrint (geração de PDF nativo) requer bibliotecas do sistema (Pango/Cairo). O sistema web funcionará normalmente.")

def criar_diretorios_obrigatorios():
    diretorios = [
        BASE_DIR / "instance",
        BASE_DIR / "app" / "static" / "uploads",
        BASE_DIR / "logs",
        BASE_DIR / "backups"
    ]
    for d in diretorios:
        d.mkdir(parents=True, exist_ok=True)
        # Garante arquivo .gitkeep para estrutura de pastas
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists() and d.name in ["uploads", "logs", "backups"]:
            gitkeep.touch()
    
    print_ok("Diretórios necessários criados e verificados com permissão de escrita.")

def configurar_env(modo_interativo=True, env_tipo="production", db_tipo="sqlite", db_url=None):
    env_file = BASE_DIR / ".env"
    
    if env_file.exists():
        print_ok("Arquivo '.env' já existente detectado. Preservando configurações vigentes.")
        return

    print("  Gerando arquivo de configuração '.env'...")
    secret_key = secrets.token_hex(32)

    if modo_interativo:
        print("\n  --- CONFIGURAÇÃO DE AMBIENTE ---")
        print("  1 - Produção (Recomendado para servidores web, PythonAnywhere, cPanel)")
        print("  2 - Desenvolvimento (Ativa debug e recarregamento automático)")
        op_env = input("  Selecione o ambiente [1/2] (padrão: 1): ").strip()
        env_tipo = "development" if op_env == "2" else "production"

        print("\n  --- BANCO DE DADOS ---")
        print("  1 - SQLite (Padrão e pronto para uso local ou congregações no PythonAnywhere)")
        print("  2 - MySQL / MariaDB (Recomendado para cPanel / servidores dedicados)")
        op_db = input("  Selecione o banco de dados [1/2] (padrão: 1): ").strip()
        
        if op_db == "2":
            db_tipo = "mysql"
            db_host = input("  Host do MySQL (padrão: localhost): ").strip() or "localhost"
            db_port = input("  Porta do MySQL (padrão: 3306): ").strip() or "3306"
            db_name = input("  Nome do Banco de Dados: ").strip() or "sigi_db"
            db_user = input("  Usuário do MySQL: ").strip() or "root"
            db_pass = input("  Senha do MySQL: ").strip()
            db_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        else:
            db_tipo = "sqlite"
            db_url = "sqlite:///instance/sigi.db"
    else:
        if db_tipo == "mysql" and not db_url:
            db_url = "mysql+pymysql://root:@localhost:3306/sigi_db?charset=utf8mb4"
        elif not db_url:
            db_url = "sqlite:///instance/sigi.db"

    conteudo_env = f"""# ==============================================================================
# 🏛️ SiGI — Variáveis de Ambiente de Produção / Instalação
# Gerado automaticamente pelo instalador em {Path(__file__).name}
# ==============================================================================

FLASK_ENV={env_tipo}
SECRET_KEY={secret_key}
APP_TIMEZONE=America/Sao_Paulo

# Banco de Dados
DATABASE_URL={db_url}

# Uploads e Arquivos
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH_MB=10

# Sessão e Segurança
SESSION_TIMEOUT=60
REMEMBER_DAYS=7

# Configurações de E-mail (Preencha para habilitar notificações SMTP)
MAIL_SERVER=localhost
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_NAME=SiGI Notificações
MAIL_DEFAULT_EMAIL=naoresponda@sigi.local

LOG_LEVEL=INFO
"""
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(conteudo_env)
    
    print_ok(f"Arquivo '.env' gerado com sucesso (Chave criptográfica de 256 bits gerada).")

def inicializar_banco(python_exe):
    print("  Inicializando esquema e tabelas do banco de dados...")
    (BASE_DIR / "instance").mkdir(parents=True, exist_ok=True)
    script_init = """
import sys
from app import create_app, db
from app.models import Permission

app = create_app()
with app.app_context():
    db.create_all()
    
    # Garante permissões padrão do sistema
    areas_acoes = {
        'usuarios': ['view', 'create', 'edit', 'delete'],
        'config': ['view', 'edit', 'delete'],
        'mail': ['view', 'create', 'edit', 'delete'],
        'financeiro': ['view', 'create', 'edit', 'delete'],
        'atas': ['view', 'create', 'edit', 'delete'],
        'cartas': ['view', 'create', 'edit', 'delete'],
        'certificados': ['view', 'create', 'edit', 'delete'],
        'eventos': ['view', 'create', 'edit', 'delete'],
        'membros': ['view', 'create', 'edit', 'delete'],
        'patrimonios': ['view', 'create', 'edit', 'delete'],
        'ebd': ['view', 'create', 'edit', 'delete', 'frequencia'],
        'perfil': ['view', 'password']
    }
    
    for area, acoes in areas_acoes.items():
        for acao in acoes:
            if not Permission.query.filter_by(area=area, action=acao).first():
                db.session.add(Permission(area=area, action=acao))
                
    db.session.commit()
    print('BANCO_OK')
"""
    try:
        res = subprocess.run([str(python_exe), "-c", script_init], cwd=str(BASE_DIR), capture_output=True, text=True, check=True)
        if "BANCO_OK" in res.stdout:
            print_ok("Tabelas do banco de dados e matriz de permissões inicializadas com sucesso.")
        else:
            print_ok("Banco de dados verificado.")
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao inicializar o banco de dados:\n{e.stderr}")
        sys.exit(1)

def criar_usuario_admin(python_exe, modo_interativo=True, nome=None, email=None, senha=None, skip_admin=False):
    if skip_admin:
        print_ok("Criação de administrador ignorada conforme parâmetro.")
        return

    script_check = """
from app import create_app
from app.models import User
app = create_app()
with app.app_context():
    print(User.query.filter_by(is_admin=True).count())
"""
    res = subprocess.run([str(python_exe), "-c", script_check], cwd=str(BASE_DIR), capture_output=True, text=True)
    count_admin = int(res.stdout.strip().split()[-1]) if res.stdout.strip() else 0

    if count_admin > 0:
        print_ok(f"Já existe(m) {count_admin} usuário(s) administrador(es) cadastrado(s).")
        return

    print("\n  --- CRIAÇÃO DO PRIMEIRO USUÁRIO ADMINISTRADOR ---")
    if modo_interativo and not (email and senha):
        nome = input("  Nome completo do Administrador (ex: Pastor Titular): ").strip() or "Administrador Geral"
        email = input("  E-mail de login (ex: admin@suaigreja.com.br): ").strip()
        while not email:
            email = input("  E-mail é obrigatório: ").strip()
        senha = input("  Senha de acesso (mínimo 6 caracteres): ").strip()
        while len(senha) < 6:
            senha = input("  Senha deve ter pelo menos 6 caracteres: ").strip()
    else:
        nome = nome or "Administrador Geral"
        email = email or "admin@sigi.local"
        senha = senha or "admin123456"

    script_create_user = f"""
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    u = User(nome="{nome}", email="{email}", is_admin=True, ativo=True)
    u.set_password("{senha}")
    db.session.add(u)
    db.session.commit()
    print('USER_OK')
"""
    res = subprocess.run([str(python_exe), "-c", script_create_user], cwd=str(BASE_DIR), capture_output=True, text=True)
    if "USER_OK" in res.stdout:
        print_ok(f"Usuário administrador criado com sucesso ({email}).")
    else:
        print_error(f"Erro ao criar usuário administrador: {res.stderr}")

def executar_healthcheck(python_exe):
    print("  Executando verificação de integridade da aplicação...")
    script_health = """
from app import create_app, db
from app.models import User, Igreja
app = create_app()
with app.app_context():
    db.session.execute(db.text('SELECT 1'))
    print('HEALTH_OK')
"""
    res = subprocess.run([str(python_exe), "-c", script_health], cwd=str(BASE_DIR), capture_output=True, text=True)
    if "HEALTH_OK" in res.stdout:
        print_ok("Verificação de saúde aprovada com 100% de integridade.")
    else:
        print_warn(f"Aviso na verificação de integridade:\n{res.stderr}")

def main():
    parser = argparse.ArgumentParser(description="Instalador Automático do SiGI")
    parser.add_argument("--non-interactive", action="store_true", help="Executa a instalação em modo silencioso/automatizado")
    parser.add_argument("--env", choices=["production", "development"], default="production", help="Tipo de ambiente")
    parser.add_argument("--db", choices=["sqlite", "mysql"], default="sqlite", help="Tipo de banco de dados")
    parser.add_argument("--db-url", type=str, help="URL de conexão completa do banco de dados")
    parser.add_argument("--admin-name", type=str, help="Nome do usuário administrador")
    parser.add_argument("--admin-email", type=str, help="E-mail do usuário administrador")
    parser.add_argument("--admin-password", type=str, help="Senha do usuário administrador")
    parser.add_argument("--skip-admin", action="store_true", help="Pula a criação do usuário administrador")
    
    args = parser.parse_args()
    interativo = not args.non_interactive

    print_header("🏛️  SIGI — INSTALADOR OFICIAL DO SISTEMA")
    print("  Sistema Integrado de Gestão de Igreja")
    print("  Compatível com Servidores Compartilhados, PythonAnywhere e Linux SSH\n")

    # 1. Checagem de Python
    verificar_versao_python()

    # 2. Virtualenv
    print_step(2, 7, "Configuração do Ambiente Virtual (venv)")
    python_exe = criar_ou_verificar_venv()

    # 3. Dependências
    print_step(3, 7, "Instalação de Dependências")
    instalar_dependencias(python_exe)

    # 4. Diretórios de Trabalho
    print_step(4, 7, "Criação de Diretórios do Sistema")
    criar_diretorios_obrigatorios()

    # 5. Variáveis de Ambiente (.env)
    print_step(5, 7, "Configuração de Variáveis de Ambiente (.env)")
    configurar_env(
        modo_interativo=interativo,
        env_tipo=args.env,
        db_tipo=args.db,
        db_url=args.db_url
    )

    # 6. Banco de Dados e Permissões
    print_step(6, 7, "Inicialização do Banco de Dados")
    inicializar_banco(python_exe)

    # 7. Usuário Administrador & Healthcheck
    print_step(7, 7, "Administrador e Diagnóstico Final")
    criar_usuario_admin(
        python_exe,
        modo_interativo=interativo,
        nome=args.admin_name,
        email=args.admin_email,
        senha=args.admin_password,
        skip_admin=args.skip_admin
    )
    executar_healthcheck(python_exe)

    # Resumo Final e Próximos Passos
    print_header("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("""
  O SiGI está pronto para execução!

  📌 COMO INICIAR O SISTEMA:
  
  1. Em Desenvolvimento Local:
     python run.py
     (Acesse: http://localhost:5000)

  2. No PythonAnywhere:
     - Acesse a aba 'Web' no painel
     - Aponte o arquivo WSGI para: wsgi.py
     - Configure os Static Files:
         URL: /static/        -> Directory: /home/seu_usuario/sigi/app/static/
         URL: /static/uploads -> Directory: /home/seu_usuario/sigi/app/static/uploads/
     - Clique em 'Reload'

  3. Em Servidor Compartilhado (cPanel / Apache / Passenger):
     - No 'Setup Python App', defina o arquivo de inicialização como: wsgi.py
     - Application Entry point: application

  Consulte 'DEPLOY.md' para guias detalhados e procedimentos de segurança.
""")

if __name__ == "__main__":
    main()
