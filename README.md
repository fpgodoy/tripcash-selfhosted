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
   git clone <URL_DO_REPOSITORIO>
   cd tripcash-selfhosted-main
   ```

2. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto. O `docker-compose.yml` já possui valores padrão para facilitar testes locais, mas **nunca use os valores padrão em produção**.
   ```env
   SECRET_KEY=uma_string_longa_e_aleatoria_aqui
   DB_USER=tripuser
   DB_PASSWORD=sua_senha_forte_aqui
   DB_NAME=tripcashdb
   ```

   > **Dica:** para gerar um `SECRET_KEY` seguro, use:
   > ```bash
   > python -c "import secrets; print(secrets.token_hex(32))"
   > ```

3. **Suba os containers:**
   ```bash
   docker-compose up -d
   ```

4. **Inicialize o Banco de Dados (apenas na primeira vez):**
   ```bash
   docker-compose exec web flask init-db
   ```

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
Ao acessar a aplicação pela primeira vez, clique em **Register** para criar seu usuário. Após o registro, faça o login para acessar seu painel pessoal.

### 2. Criando sua primeira Viagem
Logo após o primeiro login, você será redirecionado para criar uma viagem (ex: "Eurotrip 2024"). As despesas são sempre vinculadas a uma viagem específica.

### 3. Gerenciando Categorias (Labels)
A aplicação vem com 4 categorias padrão: **Food**, **Transport**, **Tickets** e **Accommodation**. 
Você pode criar novas categorias ou editar as existentes no menu de **Labels** para melhor se adaptar ao seu estilo de viagem.

### 4. Lançando Gastos
No painel principal da sua viagem atual, você pode clicar para adicionar um novo gasto:
- Selecione a **Data**.
- Escolha a **Categoria**.
- Dê um **Título**/Descrição.
- Insira o **Valor**.

### 5. Visualização e Resumo
No menu **List**, você pode ver todos os gastos lançados, editá-los ou excluí-los. Há também uma funcionalidade de resumo que soma os gastos por categoria e data, ajudando você a entender para onde seu dinheiro está indo.

---

## ✨ Funcionalidades Principais
* **Autenticação Segura:** Seus dados protegidos por login.
* **Múltiplas Viagens:** Gerencie diferentes destinos separadamente.
* **Categorias Personalizáveis:** Crie etiquetas que façam sentido para você.
* **Interface Low-JS:** Focada em velocidade e compatibilidade, com visual limpo via Bootstrap.
* **Docker Ready:** Deploy em segundos em qualquer servidor.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3.11** + **Flask 3.1.3**
- **PostgreSQL 15** (Banco de dados relacional)
- **Gunicorn** (Servidor de produção)
- **Bootstrap** (Interface responsiva)
- **Docker & Docker Compose** (Containerização)
- **Flask-Babel** (Internacionalização PT/EN)

---

## 📋 Monitoramento de Logs

A aplicação está configurada para registrar logs de acesso e erros via Gunicorn, capturados pelo Docker com rotação automática (máx. 5 arquivos × 10 MB para web, 3 × 10 MB para o banco).

### Comandos úteis

```bash
# Ver logs em tempo real
docker-compose logs -f web

# Ver últimas 50 linhas
docker-compose logs --tail=50 web

# Filtrar por período
docker-compose logs --since 1h web

# Logs do banco de dados
docker-compose logs --tail=30 db

# Buscar um endpoint específico
docker-compose logs web | grep "POST /auth/login"
```

### Exemplo de saída
```
web-1 | [INFO] Starting gunicorn 25.1.0
web-1 | 192.168.1.5 - - [13/Mar/2026] "GET / HTTP/1.1" 200 2345
web-1 | 192.168.1.5 - - [13/Mar/2026] "POST /auth/login HTTP/1.1" 302 -
```

> O serviço `web` reinicia automaticamente em caso de falha (`restart: unless-stopped`).