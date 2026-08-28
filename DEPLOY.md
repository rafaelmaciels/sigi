# 🏛️ SiGI — Guia Oficial de Implantação e Deploy

Este documento fornece as diretrizes para instalação, configuração, operação em produção, backup e resolução de problemas do **SiGI (Sistema Integrado de Gestão de Igreja)**.

---

## 📑 Sumário
1. [Requisitos Mínimos](#1-requisitos-mínimos)
2. [Instalação Rápida Automatizada](#2-instalação-rápida-automatizada)
3. [Guia de Instalação no PythonAnywhere](#3-guia-de-instalação-no-pythonanywhere)
4. [Guia de Instalação em Hospedagem Compartilhada (cPanel / Apache)](#4-guia-de-instalação-em-hospedagem-compartilhada-cpanel--apache)
5. [Configuração de Produção & Variáveis de Ambiente](#5-configuração-de-produção--variáveis-de-ambiente)
6. [Rotina de Atualização Segura](#6-rotina-de-atualização-segura)
7. [Rotina de Backup e Restauração](#7-rotina-de-backup-e-restauração)
8. [Verificação de Saúde (Healthcheck)](#8-verificação-de-saúde-healthcheck)
9. [Troubleshooting & Resolução de Problemas](#9-troubleshooting--resolução-de-problemas)
10. [Procedimento de Rollback](#10-procedimento-de-rollback)

---

## 1. Requisitos Mínimos

- **Linguagem:** Python 3.10, 3.11 ou 3.12.
- **Gerenciador de Pacotes:** `pip` e módulo `venv`.
- **Servidor Web:** Apache com `mod_wsgi`, Phusion Passenger, Nginx + Gunicorn ou PythonAnywhere WSGI.
- **Banco de Dados:**
  - *SQLite:* Nativo (recomendado para congregações locais ou PythonAnywhere Free/Hacker).
  - *MySQL / MariaDB:* Versão 5.7+ ou 8.0+ (recomendado para produção multi-usuário em cPanel).
- **Memória RAM:** 512 MB de RAM mínima (1 GB recomendado).
- **Espaço em Disco:** 200 MB para o sistema + espaço para uploads de fotos/comprovantes.

---

## 2. Instalação Rápida Automatizada

### No Linux / macOS / Servidor SSH:
```bash
git clone https://github.com/rafaelmaciels/sigi.git
cd sigi
chmod +x install.sh update.sh
./install.sh
```

### No Windows ou execução direta em Python:
```bash
python install.py
```

### Instalação Silenciosa (CI/CD ou Scripts):
```bash
python install.py --non-interactive \
  --env production \
  --db sqlite \
  --admin-name "Pastor Titular" \
  --admin-email "admin@suaigreja.com.br" \
  --admin-password "SenhaForte123"
```

---

## 3. Guia de Instalação no PythonAnywhere

Consulte o manual detalhado com telas e mapeamento de diretórios em:
📄 **[`docs/INSTALL_PYTHONANYWHERE.md`](docs/INSTALL_PYTHONANYWHERE.md)**

**Resumo Rápido:**
1. Abra um console Bash no painel do PythonAnywhere.
2. Clone o repositório e execute `./install.sh`.
3. Na aba **Web**:
   - Crie uma Web App apontando para Python 3.11 / Manual Configuration.
   - Configure o **Virtualenv** apontando para `/home/seu_usuario/sigi/venv`.
   - No **WSGI configuration file**, importe `from wsgi import application`.
   - Em **Static Files**, adicione os mapeamentos:
     - `/static/` &rarr; `/home/seu_usuario/sigi/app/static/`
     - `/static/uploads/` &rarr; `/home/seu_usuario/sigi/app/static/uploads/`
4. Clique no botão verde **Reload**.

---

## 4. Guia de Instalação em Hospedagem Compartilhada (cPanel / Apache)

Consulte o manual completo em:
📄 **[`docs/INSTALL_SHARED_HOSTING.md`](docs/INSTALL_SHARED_HOSTING.md)**

**Resumo Rápido:**
1. Acesse o **Setup Python App** no cPanel.
2. Crie a aplicação escolhendo Python 3.10+.
3. Defina **Application root** como `sigi` e **Application startup file** como `wsgi.py`.
4. Entre via SSH ou Terminal do cPanel e execute `python install.py`.
5. Reinicie a aplicação no botão **Restart**.

---

## 5. Configuração de Produção & Variáveis de Ambiente

As configurações são lidas do arquivo `.env` gerado na raiz.

```ini
FLASK_ENV=production
SECRET_KEY=sua-chave-criptografica-gerada-no-instalador
APP_TIMEZONE=America/Sao_Paulo

# SQLite:
DATABASE_URL=sqlite:///instance/sigi.db

# MySQL:
# DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/sigi_db?charset=utf8mb4

UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH_MB=10

# E-mail (SMTP):
MAIL_SERVER=smtp.seuservidor.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=notificacoes@suaigreja.com.br
MAIL_PASSWORD=sua-senha
MAIL_DEFAULT_NAME=Secretaria SiGI
MAIL_DEFAULT_EMAIL=notificacoes@suaigreja.com.br
```

---

## 6. Rotina de Atualização Segura

Para atualizar uma instalação existente sem perder dados de membros, finanças ou uploads:

```bash
# 1. Puxe as atualizações do Git
git pull

# 2. Execute o atualizador seguro (gera snapshot prévio automaticamente)
python update.py

# 3. Recarregue seu servidor web (Reload no PythonAnywhere ou Restart no cPanel)
```

---

## 7. Rotina de Backup e Restauração

### Gerar Backup Manual:
```bash
python backup.py
```
O arquivo `.zip` será criado em `backups/backup_sigi_AAAAMMDD_HHMMSS.zip` contendo:
- O banco de dados completo (`instance/sigi.db`);
- Todos os arquivos de mídia enviados por usuários (`app/static/uploads/`);
- O arquivo de configurações (`.env`).

### Restaurar Backup:
1. Descompacte o arquivo `.zip` na raiz do projeto.
2. Execute `python healthcheck.py` para validar.

---

## 8. Verificação de Saúde (Healthcheck)

Para verificar o status da instalação e diagnosticar falhas:
```bash
python healthcheck.py
```
O script verifica:
- Existência e integridade do `.env`;
- Segurança da `SECRET_KEY`;
- Conexão e contagem de registros no banco de dados;
- Permissões de escrita nos diretórios `instance/`, `uploads/`, `logs/`, `backups/`;
- Presença dos arquivos CSS/JS do Bootstrap e gráficos.

---

## 9. Troubleshooting & Resolução de Problemas

### ❌ Erro: `ModuleNotFoundError`
- **Causa:** O virtualenv não foi ativado ou o WSGI está apontando para o Python global.
- **Solução:** No painel Web (PythonAnywhere ou cPanel), aponte o Virtualenv para a pasta `/caminho/sigi/venv`.

### ❌ Erro: `WeasyPrint could not import some external libraries`
- **Causa:** Bibliotecas C nativas (Pango/Cairo) não estão no PATH do SO.
- **Solução:** O sistema web funciona normalmente. Para geração de PDF via WeasyPrint em servidores Linux, instale `libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0` (ou utilize o layout de impressão web `@media print` nativo nos certificados e relatórios).

### ❌ Erro 500 no carregamento do WSGI
- **Causa:** Arquivo `.env` ausente ou permissões incorretas no diretório `instance/`.
- **Solução:** Execute `python healthcheck.py` para identificar o ponto de falha exato.

---

## 10. Procedimento de Rollback

Caso uma atualização precise ser desfeita:
1. Localize o snapshot pré-atualização gerado automaticamente em `backups/snapshot_pre_update_*.zip`.
2. Restaure os arquivos da versão anterior:
   ```bash
   git checkout <commit_anterior>
   ```
3. Descompacte o snapshot para recuperar o banco anterior:
   ```bash
   unzip backups/snapshot_pre_update_*.zip
   ```
4. Reinicie a aplicação web.
