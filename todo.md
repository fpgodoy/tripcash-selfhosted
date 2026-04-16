# 📋 TODO: Tripcash Application

## 🚀 Foco Atual (Tarefas Pendentes)

### ⚙️ Backend, Arquitetura & Banco de Dados

### 🎨 Frontend, UI & UX
- [x] **[Frontend/UI] Categoria padrão:** Definir a categoria "Comida" como a opção selecionada por padrão no formulário de nova despesa.
- [ ] **[Frontend/CSS] Responsividade e UX Mobile/Desktop:** Ajustar classes CSS (ou framework) para que os botões de ação principal (ex: "Registrar", "Nova Despesa") ocupem 100% da largura em dispositivos móveis e fiquem agrupados/lado a lado no desktop. Ajustar padding para touch targets adequados.
- [x] **[Frontend] Tradução do Empty State:** Localizar o template HTML da tela inicial e aplicar a tradução para português na mensagem exibida quando não há viagens ativas cadastradas.

---

## ✅ Histórico de Concluídos

### Refatoração e Qualidade de Código
- [x] **[Refatoração] Padronização de Código (PEP 8):** 162 violações corrigidas (flake8 zerado). Removidos imports não utilizados (F401), variáveis mortas (F841), trailing whitespace (W291/W293), blank lines (E302/E303), corrigido `!= None` → `is not None` (E711), semicolons (E702), `abort` faltante (F821). Filtro Jinja2 `currencyFormat` renomeado para `currency_format` (snake_case) com atualização em todos os templates. Blueprints já estavam implementados — nenhuma reestruturação necessária.

### Regras de Negócio e Permissões
- [x] **[Backend/DB] Filtrar visibilidade de despesas individuais:** Query de `list()` e `total()` em `list.py` atualizada. Participantes não-donos só visualizam despesas com `is_split = TRUE`; donos veem tudo. `trip_owner_id` incluído na query de seleção de viagem ativa.
- [x] **[Arquitetura] Avaliação FastAPI (Research):** Análise técnica documentada com prós/contras, estimativa de esforço (~11-18 dias), alternativas intermediárias e recomendação: manter Flask no curto prazo e priorizar Blueprints.
- [x] **[Backend/Frontend] Corrigir erro na edição de despesa por participantes:** Edição agora permitida; corrigido o crash/500 no Flask e o redirecionamento após o salvamento no formulário.
- [x] **[Backend/Frontend] Controle de edição da Viagem:** Validação de `owner_id` implementada; botões de edição/exclusão ocultos para participantes convidados.
- [x] **[Backend/Frontend/DB] Tornar Categorias Padrão Imutáveis:** Bloqueio de UPDATE/DELETE no SQLAlchemy para categorias globais; botões de edição desabilitados visualmente no frontend para estes itens.
- [x] **[Backend/Frontend/DB] Restrição de Categorias (Viagens em Grupo):** Filtragem no select de categorias do formulário e aviso em texto adicionado para viagens compartilhadas.

### Configurações e Infraestrutura
- [x] **[Backend/DB] Setup de Migrations no PostgreSQL (Start Fresh):** `psycopg2` configurado; `Flask-Migrate` instalado; schema público recriado e migração inicial (`flask db init`, `migrate`, `upgrade`) aplicada com sucesso.
- [x] **[Backend/Config] Toggle para Registro de Usuários:** Variável `ALLOW_REGISTRATION=False` configurada no `.env` e controle de exibição de rotas/links implementado.

### Interface e Design
- [x] **[Frontend/UI] Indicador de Viagem Ativa:** Nome da viagem fixado no topo (mobile) e estado ativo destacado no card da viagem na tela de gerenciamento.
- [x] **[Frontend/CSS] Padronização de Cores:** Variáveis CSS consolidadas (`--primary`, `--background`); uso de cores vibrantes restrito a ações principais.
- [x] **[Frontend] Renomear Botões da Tela Inicial:** Labels atualizados ("Nova despesa", "Ver lista", "Resumo", "Acerto de Contas", "Gerenciar Viagens", "Gerenciar Categorias").