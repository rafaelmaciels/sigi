# 🐍 Guia Passo a Passo de Implantação no PythonAnywhere

Este manual descreve como instalar e rodar o **SiGI** na plataforma **PythonAnywhere** (planos Free, Hacker ou Custom).

---

## 1. Criar a Conta e Acessar o Console Bash

1. Crie ou acesse sua conta em [pythonanywhere.com](https://www.pythonanywhere.com).
2. No painel principal (**Dashboard**), acesse a aba **Consoles** e clique em **Bash**.

---

## 2. Clonar o Projeto e Executar o Instalador

No console Bash do PythonAnywhere, execute os seguintes comandos:

```bash
# 1. Clonar o repositório
git clone https://github.com/rafaelmaciels/sigi.git

# 2. Entrar na pasta do SiGI
cd sigi

# 3. Dar permissão de execução e rodar o instalador
chmod +x install.sh update.sh
./install.sh
```

Durante a instalação:
- Escolha o ambiente: **1 - Produção**
- Escolha o banco de dados: **1 - SQLite** *(ou MySQL caso tenha criado no painel do PythonAnywhere)*
- Informe seu Nome, E-mail e Senha para o primeiro usuário Administrador.

---

## 3. Configurar a Aplicação Web no Painel

1. Acesse a aba **Web** no menu superior do PythonAnywhere.
2. Clique no botão azul **Add a new web app**.
3. No modal de configuração:
   - Clique em **Next**;
   - Selecione **Manual configuration** *(NÃO selecione Flask direto, para usarmos o nosso virtualenv)*;
   - Selecione **Python 3.11** (ou 3.10 / 3.12);
   - Conclua a criação da Web App.

---

## 4. Configurar o Virtualenv

Na página de configuração da sua Web App (aba **Web**):
1. Role até a seção **Virtualenv**.
2. Clique em **Enter path to a virtualenv** e informe o caminho completo:
   ```text
   /home/seu_usuario/sigi/venv
   ```
   *(Substitua `seu_usuario` pelo seu nome de usuário no PythonAnywhere).*

---

## 5. Configurar o Arquivo WSGI

Na seção **Code** da aba **Web**:
1. Clique no link do arquivo **WSGI configuration file** (`/var/www/seu_usuario_pythonanywhere_com_wsgi.py`).
2. Apague todo o conteúdo padrão do arquivo e cole apenas o seguinte código:

```python
import sys
import os

# Caminho da pasta do SiGI
path = '/home/seu_usuario/sigi'
if path not in sys.path:
    sys.path.insert(0, path)

# Carrega variáveis do arquivo .env
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(path, '.env'))

# Importa a aplicação configurada
from wsgi import application
```
*(Lembre-se de substituir `seu_usuario` pelo seu username).*
3. Clique em **Save** no canto superior direito.

---

## 6. Mapear Arquivos Estáticos e Uploads

Na seção **Static files** da aba **Web**, adicione exatamente as seguintes 2 entradas:

| URL | Directory (Caminho Completo) |
| :--- | :--- |
| `/static/` | `/home/seu_usuario/sigi/app/static/` |
| `/static/uploads/` | `/home/seu_usuario/sigi/app/static/uploads/` |

---

## 7. Recarregar e Testar a Aplicação

1. No topo da página da aba **Web**, clique no botão verde **Reload seu_usuario.pythonanywhere.com**.
2. Acesse a URL: `https://seu_usuario.pythonanywhere.com`.
3. Faça login com o e-mail e senha cadastrados no instalador.

---

## 8. Diagnóstico de Erros no PythonAnywhere

Se a página exibir `Something went wrong`:
1. Acesse a aba **Web**;
2. Na seção **Log files**, abra o link **Error log** (`seu_usuario.pythonanywhere.com.error.log`);
3. Os últimos erros de execução estarão discriminados no final do arquivo.
