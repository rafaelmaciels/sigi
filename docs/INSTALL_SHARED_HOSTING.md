# 🌐 Guia de Implantação em Hospedagem Compartilhada (cPanel / Apache / Passenger)

Este manual orienta a instalação do **SiGI** em provedores de hospedagem compartilhada comuns (HostGator, Locaweb, KingHost, Hostinger, cPanel padrão com CloudLinux / Phusion Passenger).

---

## 1. Requisitos no Provedor

- Painel **cPanel** com recurso **Setup Python App** (Phusion Passenger / CloudLinux).
- Suporte a **Python 3.10+**.
- Suporte a **Bancos de Dados MySQL / MariaDB** ou **SQLite**.
- Acesso ao **Terminal cPanel** ou **SSH**.

---

## 2. Criar o Banco de Dados MySQL (Recomendado no cPanel)

1. No painel cPanel, acesse **Bancos de Dados MySQL**.
2. Crie um novo banco (ex: `usuario_sigi`).
3. Crie um novo usuário com senha forte (ex: `usuario_sigiapp`).
4. Adicione o usuário ao banco de dados concedendo **TODOS OS PRIVILÉGIOS**.
5. Anote a connection string:
   ```text
   mysql+pymysql://usuario_sigiapp:SENHA@localhost:3306/usuario_sigi?charset=utf8mb4
   ```

---

## 3. Configurar a Aplicação Python no cPanel

1. Acesse o menu **Setup Python App** (ou *Criar Aplicativo Python*).
2. Clique em **Create Application**:
   - **Python version:** Selecione `3.10`, `3.11` ou `3.12`.
   - **Application root:** Informe a pasta onde o projeto será instalado (ex: `sigi` ou `public_html/sigi`).
   - **Application URL:** Selecione o domínio ou subdomínio (ex: `igreja.seusite.com.br`).
   - **Application startup file:** `wsgi.py`
   - **Application Entry point:** `application`
3. Clique em **Create**.
4. O cPanel exibirá um comando para ativar o ambiente virtual no topo da página. Copie-o.

---

## 4. Instalação dos Arquivos do SiGI

Abra o **Terminal** do cPanel (ou acesse via SSH):

```bash
# 1. Acesse a pasta do aplicativo
cd ~/sigi

# 2. Clone ou descompacte os arquivos do SiGI
git clone https://github.com/rafaelmaciels/sigi.git .

# 3. Ative o ambiente virtual do cPanel (utilize o comando copiado no Setup Python App)
source /home/seu_usuario/virtualenv/sigi/3.11/bin/activate

# 4. Execute o instalador automático
python install.py
```

Durante o instalador:
- Escolha **1 - Produção**
- Escolha **2 - MySQL** e cole os dados do banco criado na etapa 2 (ou use **1 - SQLite**).
- Defina o e-mail e senha do Administrador.

---

## 5. Permissões de Pastas e Finalização

Garanta que as pastas de dados possuam permissão de escrita para o processo web do Apache/Passenger:

```bash
chmod -R 755 instance/ app/static/uploads/ logs/ backups/
```

1. Retorne à página **Setup Python App** no cPanel.
2. Clique no botão **Restart** ao lado da sua aplicação.
3. Acesse a URL do seu domínio e realize o login.

---

## 6. Rotina de Atualização no cPanel

Para atualizar o sistema no futuro via Terminal do cPanel:

```bash
cd ~/sigi
source /home/seu_usuario/virtualenv/sigi/3.11/bin/activate
git pull
python update.py
```
Em seguida, clique em **Restart** no painel Setup Python App.
