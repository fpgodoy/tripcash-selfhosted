# Tripcash 💰

Tripcash é uma aplicação web focada na simplicidade e eficiência para o gerenciamento das finanças de suas viagens. O objetivo é permitir que você registre seus gastos de forma rápida, organizando-os por categoria e data, sem distrações.

Esta versão foi adaptada para ser **self-hosted**, utilizando Docker para facilitar o deploy e PostgreSQL como banco de dados.

---

## 🚀 Como Rodar (Self-hosting)

A forma recomendada de executar o Tripcash é através do **Docker Compose**.

### Pré-requisitos
- [Docker](https://www.docker.com/) instalado.
- [Docker Compose](https://docs.docker.com/compose/) instalado.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/fpgodoy/tripcash-selfhosted.git
   cd tripcash-selfhosted
   ```

2. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto. O `docker-compose.yml` já possui valores padrão para facilitar testes locais, mas **nunca use os valores padrão em produção**.
   ```env
   # Credenciais do Banco e App
   SECRET_KEY=uma_string_longa_e_aleatoria_aqui
   DB_USER=tripuser
   DB_PASSWORD=sua_senha_forte_aqui
   DB_NAME=tripcashdb
   
   # Configurações Avançadas
   ALLOW_REGISTRATION=true     # Mude para false para impedir novos cadastros após criar sua conta
   GUNICORN_WORKERS=2          # Aumente se houver acesso simultâneo alto
   ```

   > **Dica:** para gerar um `SECRET_KEY` seguro, use:
   > ```bash
   > python -c "import secrets; print(secrets.token_hex(32))"
   > ```

3. **Suba os containers:**
   ```bash
   docker-compose up -d
   ```

4. **Inicialização Automática:**
   O contêiner da aplicação (`entrypoint.sh`) criará e aplicará as migrações do banco de dados automaticamente através do *Alembic*. Nenhuma inicialização manual é necessária!

5. **Acesse a aplicação:**
   A aplicação estará disponível na porta **8000** do servidor onde os containers estão rodando.
   - Acesso local: `http://localhost:8000`
   - Acesso na rede local: `http://<IP_DO_SERVIDOR>:8000`

---

## 🔒 Considerações para Produção

> **Atenção:** nunca suba a aplicação em produção com as credenciais padrão. Use sempre um arquivo `.env` com valores fortes e únicos.

### Credenciais
Defina `SECRET_KEY` e `DB_PASSWORD` com valores seguros no arquivo `.env`. Jamais comite o `.env` no repositório. O `.gitignore` já está configurado para ignorá-lo.

### Acesso por HTTPS (recomendado)
O Gunicorn serve HTTP puro na porta 8000. Para expor a aplicação na internet com segurança, utilize um reverse proxy como **Nginx** ou **Traefik** na frente da aplicação para:
- Terminar o SSL/TLS (certificado via Let's Encrypt)
- Redirecionar HTTP → HTTPS
- Servir arquivos estáticos com melhor desempenho

Para uso exclusivo em **rede local interna**, o acesso direto à porta 8000 é suficiente.

---

## 📖 Guia de Uso

O uso do Tripcash segue um fluxo lógico simples:

### 1. Registro e Login
Ao acessar a aplicação pela primeira vez, clique em **Registrar** para criar seu usuário. Após o registro, faça o login para acessar seu painel pessoal.

### 2. Criando sua primeira Viagem
Logo após o primeiro login, você será redirecionado para criar uma viagem (ex: "Eurotrip 2024"). As despesas são sempre vinculadas a uma viagem específica.

### 3. Gerenciando Categorias
A aplicação vem com categorias padrão (como **Comida**, **Transporte**, **Ingressos** e **Hospedagem**). 
Você pode criar novas categorias ou editar as existentes no menu de **Categorias** para melhor se adaptar ao seu estilo de viagem.

### 4. Lançando Gastos
No painel principal da sua viagem atual, você pode clicar para adicionar um novo gasto:
- Selecione a **Data**.
- Escolha a **Categoria**.
- Dê um **Título**/Descrição.
- Insira o **Valor**.

### 5. Visualização e Resumo
Na listagem da tela principal, você pode ver todos os gastos lançados, editá-los ou excluí-los. Há também a aba de **Resumo**, que soma os gastos por categoria e os exibe graficamente ou de forma condensada, ajudando você a entender para onde seu dinheiro está indo. Em casos de viagem em grupo, a aba **Acertos** exibirá quem deve pagar quem.

---

## ✨ Funcionalidades Principais
* **Autenticação Segura:** Seus dados protegidos por login.
* **Múltiplas Viagens & Modos:** Gerencie viagens individuais ou **Viagens em Grupo**.
* **Divisão de Gastos (Splits):** Em viagens de grupo, registre quem pagou, quem deve e gerencie a liquidação de contas (Acertos/Settlements) automaticamente.
* **Internacionalização (i18n):** Suporte nativo e totalmente traduzido para Português (PT-BR) e Inglês.
* **Mobile-First UX:** Interface moderna, condensada e ergométrica projetada fofamente para telas de toque com navegação acelerada.
* **Categorias Personalizáveis:** Crie etiquetas que façam sentido para você.
* **Docker Ready:** Deploy robusto em produção com Gunicorn e migrations automáticas.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3.11** + **Flask 3.1.3**
- **PostgreSQL 15** (Banco de dados relacional)
- **Alembic / Flask-Migrate** (Migrações e versionamento de esquema de banco de dados)
- **Gunicorn** (Servidor HTTP WSGI de produção)
- **Bootstrap 5** (Design System e Grid responsivo)
- **Flask-Babel** (Motor de internacionalização nativa)
- **Docker & Docker Compose** (Containerização e Orquestração)
