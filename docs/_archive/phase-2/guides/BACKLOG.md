# 📋 BACKLOG - Trading 212 Bot MVP

**Status:** Aguardando aprovação para começar desenvolvimento
**Última atualização:** 2026-09-13

---

## 📌 Como usar este Backlog

- **Priority (P):** P1 (crítico) → P4 (nice-to-have)
- **Effort (E):** 1 (1-2h) → 5 (2+ dias)
- **Status:** `[ ]` (TODO) → `[x]` (DONE)

---

## 🎯 FASE 1B: Design & UI/UX (Trading 212 Style)

### **Feature 1.1: Redesign Visual com estilo Trading 212**
- **Priority:** P1 (Crítico - Foundation)
- **Effort:** 4
- **Status:** [ ]
- **Descrição:** Redesenhar toda a UI com estilo visual Trading 212 (dark theme profissional, cores vibrantes, dados financeiros bem estruturados)
- **Subtasks:**
  - [ ] Frontend: Criar design system com cores Trading 212
    - [ ] Cor primária: Verde escuro (`#00C853` ou similar)
    - [ ] Cor secundária: Laranja/Amarelo (`#FF9800`)
    - [ ] Fundo: Muito escuro (`#0A0E27` ou `#1A1F3A`)
    - [ ] Neutrals: Grays para texto (`#E0E0E0`, `#A0A0A0`)
  - [ ] Frontend: Criar CSS utilities avançadas (Tailwind config customizado)
  - [ ] Frontend: Componentes reutilizáveis:
    - [ ] Card com gradiente e sombras suaves
    - [ ] Badge status (green, red, orange)
    - [ ] Button com hover/active states profissionais
    - [ ] Input/Select com focus states
    - [ ] Tabela com striping, hover, sorting visual
  - [ ] Frontend: Login Page (redesign)
    - [ ] Background com gradiente escuro
    - [ ] Form centered com shadow/glassmorphism
    - [ ] Logo Trading 212 Bot
    - [ ] Inputs com icon
    - [ ] Botão com loading state
    - [ ] Link de "Esqueceu password?"
  - [ ] Frontend: Dashboard (redesign)
    - [ ] Sidebar dark com hover effects
    - [ ] Header com logo + user menu + logout
    - [ ] Main content area com padding generoso
    - [ ] Cards KPI no topo (saldo, P&L, etc)
    - [ ] Tabela ISINs com design profissional
  - [ ] Frontend: Tabela ISINs (redesign)
    - [ ] Header com sorting indicators (↑↓)
    - [ ] Rows com hover background
    - [ ] Columns: ISIN, Ticker, Nome, Preço, P&L (red/green), Automação (toggle), Ações
    - [ ] P&L column: color-coded (verde se +, vermelho se -)
    - [ ] Automação: toggle switch com animation
    - [ ] **Ações: APENAS toggle de automação (sem edit, sem delete)**
    - [ ] Status indicators: pulse animation se activo
  - [ ] Frontend: Forms (redesign)
    - [ ] Modal backgrounds com blur
    - [ ] Form labels elegantes
    - [ ] Input focus states com border color
    - [ ] Validation messages em vermelho
    - [ ] Success messages em verde
    - [ ] Submit/Cancel buttons lado a lado
  - [ ] Frontend: Notificações (Toast)
    - [ ] Toast com position fixed top-right
    - [ ] Icons (check, error, warning, info)
    - [ ] Auto-dismiss após 5s
    - [ ] Manual close button
    - [ ] Color-coded background (verde success, vermelho error)
  - [ ] Frontend: Animações suaves
    - [ ] Transitions 200-300ms (inputs, buttons, modals)
    - [ ] Skeleton loaders enquanto carregam dados
    - [ ] Fade-in animations
    - [ ] Toggle switch animation
  - [ ] Frontend: Responsive design
    - [ ] Mobile: sidebar collapse em hamburger menu
    - [ ] Mobile: tabela horizontal scroll se necessário
    - [ ] Tablet: layout adaptado
  - [ ] Frontend: Testes visuais
    - [ ] Testar contraste (WCAG AA)
    - [ ] Testar em mobile/tablet
    - [ ] Testar cores no modo dark

- **Dependências:** Nenhuma (foundation)
- **Arquivos modificados:**
  - `frontend/src/index.css` (custom CSS + Tailwind config)
  - `frontend/tailwind.config.ts` (colors, spacing customized)
  - `frontend/src/pages/LoginPage.tsx`
  - `frontend/src/pages/DashboardPage.tsx`
  - `frontend/src/components/Sidebar.tsx`
  - `frontend/src/components/ISINTable.tsx`
  - `frontend/src/components/[new components]` (Button, Card, Badge, Toast, etc)

- **Notas Técnicas:**
  - Usar Tailwind CSS com custom config
  - Considerar Shadcn/ui para componentes prontos (opcional)
  - Manter acessibilidade (alt text, aria labels)
  - Design mobile-first
  - Cores deve ser WCAG AA contraste
  - Usar Lucide React para icons

- **Referência Visual:**
  - Trading 212 website: https://trading212.com
  - Color scheme: Dark theme com acentos verde/laranja
  - Typography: Sans-serif profissional (Inter, Roboto, ou similar)
  - Spacing: 8px grid (8, 16, 24, 32, etc)

---

## 🎯 FASE 2: Autenticação Real

### **Feature 2.1: Login Real com Supabase Auth ⭐ PRIORITY**
- **Priority:** P1 (Crítico)
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Implementar autenticação real (não stub) com Supabase Auth. Utilizador consegue fazer login com credenciais reais e aceder ao dashboard.
- **Subtasks:**
  
  **Backend:**
  - [ ] POST `/auth/login` - Fazer login com email/password
    - [ ] Chamar Supabase Auth API com credenciais
    - [ ] Retornar JWT token se sucesso
    - [ ] Retornar erro 401 se credenciais inválidas
    - [ ] Response: `{access_token, user: {id, email}}`
  - [ ] POST `/auth/register` - Criar nova conta
    - [ ] Validar email (formato correto)
    - [ ] Validar password (mínimo 8 caracteres)
    - [ ] Chamar Supabase Auth API
    - [ ] Guardar user em `users` table
    - [ ] Retornar JWT token
  - [ ] POST `/auth/logout` - Logout
    - [ ] Invalidar JWT (RevokeToken)
    - [ ] Retornar 200 OK
  - [ ] GET `/auth/me` - Verificar utilizador autenticado
    - [ ] Verificar JWT token válido
    - [ ] Retornar user info: `{id, email, is_admin}`
    - [ ] Retornar 401 se token inválido/expirado
  - [ ] Middleware de autenticação
    - [ ] Verifica header `Authorization: Bearer <token>`
    - [ ] Valida JWT com Supabase
    - [ ] Injeta `current_user` em todos os endpoints protegidos
    - [ ] Retorna 401 se token ausente/inválido
  - [ ] Error handling
    - [ ] 400: Validação falhou (email inválido, password fraca)
    - [ ] 401: Credenciais inválidas ou token expirado
    - [ ] 409: Email já existe (register)
  
  **Frontend:**
  - [ ] LoginPage.tsx - Form de login FUNCIONAL
    - [ ] Input email (required, type=email)
    - [ ] Input password (required, type=password)
    - [ ] Botão "Entrar" (submit)
    - [ ] Loading state enquanto faz login
    - [ ] Erro visual se falhar (ex: credenciais inválidas)
    - [ ] Link "Criar conta" que leva a register page
    - [ ] Form validation antes de submit
  - [ ] RegisterPage.tsx - Form de registo FUNCIONAL
    - [ ] Input email (required, type=email)
    - [ ] Input password (required, 8+ chars)
    - [ ] Input confirm password (match com password)
    - [ ] Botão "Criar conta"
    - [ ] Loading state
    - [ ] Errors visuais por campo
    - [ ] Link "Voltar a login"
    - [ ] Password strength indicator (fraca/média/forte)
  - [ ] Auth API client (api/auth.ts)
    - [ ] `login(email, password)` → chama POST /auth/login
    - [ ] `register(email, password)` → chama POST /auth/register
    - [ ] `logout()` → chama POST /auth/logout
    - [ ] `getMe()` → chama GET /auth/me
    - [ ] Error handling (throw exceptions)
  - [ ] Auth Store (Zustand)
    - [ ] State: `{user, token, isLoading, error}`
    - [ ] Action: `login(email, password)`
    - [ ] Action: `register(email, password)`
    - [ ] Action: `logout()`
    - [ ] Action: `checkAuth()` (verifica se sessão ainda válida)
    - [ ] Persist token em localStorage
    - [ ] Auto-restore token on app load
  - [ ] Protected Routes
    - [ ] Se não tem token → redirect a /login
    - [ ] Se token expirado → logout automático
    - [ ] Testar com página protegida (/dashboard)
  - [ ] JWT no localStorage
    - [ ] Guardar token após login
    - [ ] Adicionar token a cada request (header Authorization)
    - [ ] Apagar token após logout
  - [ ] Testes end-to-end
    - [ ] Criar conta com email novo
    - [ ] Login com email/password corretos
    - [ ] Falhar login com password incorreto
    - [ ] Falhar login com email não-existe
    - [ ] Logout funciona
    - [ ] Token expirado → auto logout
    - [ ] Refresco página → mantém sessão (localStorage)

- **Dependências:** Feature 1.1 (UI redesign para visual profissional)
- **Critério de Aceitação:**
  - ✅ Consegue fazer login com `teste@trading212.com` (ou outro real)
  - ✅ Token JWT guardado no localStorage
  - ✅ Token enviado em Authorization header
  - ✅ Dashboard só acessível após login
  - ✅ Logout limpa token e redireciona a /login
  - ✅ Refresh página mantém sessão (token recuperado do localStorage)
  - ✅ Erro claro se credenciais erradas
  - ✅ Registo funciona (criar novo user)

- **Notas Técnicas:**
  - Supabase Auth usa JWT padrão (pode verificar em jwt.io)
  - Token expira em 24h (configurável)
  - Refresh token pode ser usado para renovar (opcional por enquanto)
  - Password min 8 chars (Supabase default)
  - Email validation com regex padrão
  
- **Utilizador de Teste:**
  ```
  Email: teste@trading212.com
  Password: teste123
  (será criado no Supabase via dashboard ou via este endpoint)
  ```

### **Feature 2.2: User Management (Admin)**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Endpoints para admin gerir utilizadores
- **Subtasks:**
  - [ ] Backend: GET `/admin/users` - Listar todos os users
  - [ ] Backend: PUT `/admin/users/{id}` - Editar permissões
  - [ ] Backend: DELETE `/admin/users/{id}` - Deletar user
  - [ ] Frontend: Página de Admin (listar users)
  - [ ] Testes: Verificar RLS (Row Level Security)
- **Dependências:** Feature 2.1
- **Notas:** Apenas acessível por users com `is_admin = true`

### **Feature 2.3: Profile/Settings Page**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Página de perfil do user
- **Subtasks:**
  - [ ] Frontend: Criar page `/profile`
  - [ ] Frontend: Mostrar dados do user (email, created_at)
  - [ ] Frontend: Opção para mudar password
  - [ ] Frontend: Opção para delete account
  - [ ] Backend: PUT `/auth/profile` - Atualizar perfil
  - [ ] Backend: POST `/auth/change-password` - Mudar password
- **Dependências:** Feature 2.1
- **Notas:** Form com validação

---

## 🎯 FASE 3: CRUD ISINs

### **Feature 3.1: GET /isins - Listar ISINs**
- **Priority:** P1 (Crítico)
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Endpoint para listar todos os ISINs do user autenticado
- **Subtasks:**
  - [ ] Backend: Implementar GET `/api/isins`
  - [ ] Backend: Filtrar por user_id (via JWT)
  - [ ] Backend: Retornar campos: id, isin, ticker, name, currency, automation_enabled, created_at
  - [ ] Backend: Pagination (limit=20, offset=0)
  - [ ] Frontend: Conectar tabela ISINTable ao endpoint real
  - [ ] Frontend: Remover mock data
  - [ ] Testes: Verificar RLS (não vê ISINs de outros users)
- **Dependências:** Feature 2.1 (Auth)
- **Notas:** Response: `[{id, isin, ticker, name, ...}]`

### **Feature 3.2: POST /isins - Adicionar ISIN**
- **Priority:** P1 (Crítico)
- **Effort:** 4
- **Status:** [ ]
- **Descrição:** Adicionar novo ISIN e fetch dados da API T212
- **Subtasks:**
  - [ ] Backend: Validar input (ISIN não pode duplicar)
  - [ ] Backend: Chamar T212 API para fetch dados do instrumento
  - [ ] Backend: Guardar em `isins` table com fields_json
  - [ ] Backend: Implementar GET `/api/isins/{id}/details` - Fetch live data T212
  - [ ] Backend: Rate limiting (respeitar T212 limits)
  - [ ] Frontend: Form para adicionar novo ISIN (modal ou page)
  - [ ] Frontend: Feedback visual (loading, success, error)
  - [ ] Frontend: Atualizar tabela após sucesso
  - [ ] Testes: Verificar integração com T212 API
- **Dependências:** Feature 2.1, 3.1
- **Notas:** POST body: `{isin: string}` → Fetch T212 → Retorna {id, isin, ticker, name, ...}

### **Feature 3.3: PUT /isins/{id} - Editar ISIN**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Editar configurações de um ISIN (nome custom, etc)
- **Subtasks:**
  - [ ] Backend: Implementar PUT `/api/isins/{id}`
  - [ ] Backend: Validar que o ISIN pertence ao user
  - [ ] Frontend: Modal de edição (nome, notas)
  - [ ] Frontend: Atualizar tabela após sucesso
  - [ ] Testes: Verificar RLS
- **Dependências:** Feature 3.1, 3.2
- **Notas:** Body: `{name?: string, fields_json?: object}`

### **Feature 3.4: DELETE /isins/{id} - Deletar ISIN**
- **Priority:** P2
- **Effort:** 1
- **Status:** [ ]
- **Descrição:** Deletar um ISIN
- **Subtasks:**
  - [ ] Backend: Implementar DELETE `/api/isins/{id}`
  - [ ] Backend: Validar que pertence ao user
  - [ ] Backend: Cascade delete trades associated
  - [ ] Frontend: Botão delete com confirmação
  - [ ] Frontend: Atualizar tabela
  - [ ] Testes: Verificar cascade delete
- **Dependências:** Feature 3.1, 3.3
- **Notas:** Soft delete (opcional) ou hard delete

### **Feature 3.5: ISIN Detail Page**
- **Priority:** P2
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Página detalhada de um ISIN com info completa
- **Subtasks:**
  - [ ] Frontend: Criar page `/isins/{id}`
  - [ ] Frontend: Mostrar dados do ISIN (isin, ticker, name, preço, etc)
  - [ ] Frontend: Mostrar histórico de trades para este ISIN
  - [ ] Frontend: Mostrar P&L do ISIN
  - [ ] Frontend: Botão para voltar à lista
  - [ ] Backend: GET `/api/isins/{id}` com dados completos
  - [ ] Backend: GET `/api/isins/{id}/trades` - Trades do ISIN
- **Dependências:** Feature 3.1
- **Notas:** Mostrar máximo de info disponível

---

## 🎯 FASE 3B: Configuração

### **Feature 3B.0: Sync Automático ISINs da Carteira T212** ⭐ NEW
- **Priority:** P1 (Crítico)
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Sync automático de ISINs da carteira T212 na primeira carga da dashboard. Todos os ISINs sincronizados começam com automação OFF por default.
- **Subtasks:**
  
  **Backend:**
  - [ ] GET `/api/isins/sync-from-trading212`
    - [ ] Chamar T212 API `/equity/positions`
    - [ ] Parsear resposta (cada posição = 1 ISIN)
    - [ ] Para cada ISIN:
      - [ ] Verificar se já existe em `isins` table (user_id + isin)
      - [ ] Se não existe: criar novo registo com `automation_enabled = FALSE`
      - [ ] Se existe: atualizar quantity e price_at (não mudar automation_enabled)
    - [ ] Retornar lista de ISINs sincronizados
    - [ ] Retornar 401 se credenciais T212 não configuradas
    - [ ] Retornar 400 se config não existe
  - [ ] Extrair dados T212 posições
    - [ ] Chamar `/equity/positions`
    - [ ] Parsear resposta JSON
    - [ ] Extrair: ticker, isin, quantity, average_price, current_price, currency
  
  **Frontend:**
  - [ ] DashboardPage.tsx - Sync automático on mount
    - [ ] Verificar se é primeira carga (flag em localStorage: `last_sync_date`)
    - [ ] Se primeira carga (sem flag ou flag antiga > 24h):
      - [ ] Mostrar loading skeleton na tabela
      - [ ] Chamar `/api/isins/sync-from-trading212`
      - [ ] Guardar timestamp de sync em localStorage
      - [ ] Atualizar tabela com resultados
      - [ ] Mostrar toast "Carteira sincronizada com sucesso"
    - [ ] Se não é primeira carga:
      - [ ] Carregar ISINs normalmente do GET `/api/isins`
  - [ ] Botão "Sincronizar Carteira" MANUAL (sempre disponível)
    - [ ] Localizado perto do título "Meus ISINs"
    - [ ] Permite forçar sync mesmo se já fez hoje
    - [ ] Loading spinner enquanto sincroniza
    - [ ] Toast success se completou
    - [ ] Toast error se falhou
    - [ ] Atualizar tabela de ISINs após sucesso
  - [ ] Verificar estado de automação
    - [ ] Tabela mostra toggle "OFF" para todos os ISINs sincronizados
    - [ ] User pode ativar manualmente clicando no toggle

  **BD:**
  - [ ] Campo `automation_enabled` sempre inicializa como FALSE
  - [ ] Quando sync, não muda automation_enabled se ISIN já existe
  - [ ] Campo `last_synced_at` (TIMESTAMP) opcional para tracking

  **Testes:**
  - [ ] Primeira carga: sync automático
  - [ ] Segunda carga (mesma sessão): não faz sync de novo
  - [ ] Segunda carga (novo dia): faz sync de novo
  - [ ] Todos os ISINs sincronizados têm automation OFF
  - [ ] Botão manual sincroniza sempre
  - [ ] Sync com conta DEMO
  - [ ] ISINs duplicatas não ocorrem
  - [ ] Atualizar preços e quantities em syncs subsequentes

- **Dependências:** Feature 3B.1 (credenciais T212 configuradas), Feature 2.1 (auth)
- **Notas Técnicas:**
  - Endpoint T212: `GET /equity/positions`
  - Response esperada:
    ```json
    [
      {
        "ticker": "VOO",
        "isin": "US9220427424",
        "quantity": 147.75,
        "average_price": 16.37,
        "current_price": 16.45,
        "pnl": 12.34,
        "pnl_percent": 0.75
      }
    ]
    ```
  - Rate limit: 1 req/1s (respeitar!)
  - User pode sincronizar várias vezes (não duplica)
  - Flag `last_sync_date` em localStorage (formato ISO datetime)
  - Se sync falha (ex: credenciais erradas), mostra erro e não muda BD

- **Critério de Aceitação:**
  - ✅ Primeira carga da dashboard → sync automático
  - ✅ Tabela preenchida com ISINs reais
  - ✅ Todos com toggle automação OFF
  - ✅ Segunda carga (hoje) → sem sync automático
  - ✅ Botão "Sincronizar Carteira" funciona manualmente
  - ✅ Sync seguinte (amanhã) → faz sync de novo
  - ✅ Cada ISIN mostra ticker, nome, preço, quantidade
  - ✅ Se já existe ISIN, atualiza preço/quantidade (não duplica)
  - ✅ Toast mostra sucesso/erro

---

## 🎯 FASE 3B: Configuração

### **Feature 3B.1: GET/PUT /config - Guardar T212 Credentials**
- **Priority:** P1 (Crítico)
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Guardar e recuperar credenciais T212 de forma segura (encriptadas)
- **Subtasks:**
  - [ ] Backend: Implementar GET `/api/config`
  - [ ] Backend: Implementar PUT `/api/config`
  - [ ] Backend: Encriptar API key e secret com Fernet
  - [ ] Backend: Desencriptar apenas quando necessário
  - [ ] Backend: Guardar em `config` table
  - [ ] Frontend: Form de configuração (input API key, API secret)
  - [ ] Frontend: Avisar que dados não são mostrados após guardar
  - [ ] Frontend: Botão para testar conexão
  - [ ] Testes: Verificar encriptação/desencriptação
- **Dependências:** Feature 2.1 (Auth)
- **Notas:** IMPORTANTE: Nunca retornar credenciais desencriptadas ao frontend!

### **Feature 3B.2: POST /config/test - Testar Conexão T212**
- **Priority:** P2
- **Effort:** 1
- **Status:** [ ]
- **Descrição:** Testar se credenciais T212 estão corretas
- **Subtasks:**
  - [ ] Backend: Implementar POST `/api/config/test`
  - [ ] Backend: Chamar T212 API com credenciais
  - [ ] Backend: Retornar sucesso/erro
  - [ ] Frontend: Botão "Test Connection"
  - [ ] Frontend: Mostrar resultado (✅ ou ❌)
- **Dependências:** Feature 3B.1
- **Notas:** Chamar `/equity/account/summary` para testar

### **Feature 3B.3: Strategy Parameters**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Guardar parâmetros da estratégia (Grid Trading)
- **Subtasks:**
  - [ ] Backend: Guardar em `config.strategy_params` (JSONB)
  - [ ] Frontend: Form para configurar parâmetros:
    - [ ] `buy_threshold_percent` (ex: 1%)
    - [ ] `sell_threshold_percent` (ex: 1%)
    - [ ] `buy_quantity_percent` (ex: 50%)
    - [ ] `sell_quantity_percent` (ex: 50%)
    - [ ] `check_interval_seconds` (ex: 300)
  - [ ] Frontend: Validação (deve ser > 0)
- **Dependências:** Feature 3B.1
- **Notas:** Parâmetros por user (não global)

---

## 🎯 FASE 4: Automação & Estratégias

### **Feature 4.1: Toggle Automation ON/OFF (por ISIN)**
- **Priority:** P1 (Crítico)
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Ligar/desligar automação de trading por ISIN
- **Subtasks:**
  - [ ] Backend: Implementar PUT `/api/isins/{id}/automation/toggle`
  - [ ] Backend: Atualizar `automation_enabled` na tabela `isins`
  - [ ] Backend: Guardar timestamp em `updated_at`
  - [ ] Frontend: Toggle switch em cada linha da tabela
  - [ ] Frontend: Atualizar estado no click
  - [ ] Frontend: Feedback visual
  - [ ] Testes: Verificar que apenas muda quando ON
- **Dependências:** Feature 3.1, 3B.1
- **Notas:** Estado guardado em BD, persiste após reload

### **Feature 4.2: Scheduler Setup (APScheduler)**
- **Priority:** P1 (Crítico)
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Setup do scheduler que corre a cada 5 minutos
- **Subtasks:**
  - [ ] Backend: Implementar APScheduler
  - [ ] Backend: Job que roda a cada 5 min (configurável)
  - [ ] Backend: Verifica ISINs com `automation_enabled = true`
  - [ ] Backend: Para cada ISIN, executa estratégia
  - [ ] Backend: Logging de cada execução
  - [ ] Backend: Error handling (não falha tudo se um falhar)
  - [ ] Testes: Verificar que scheduler inicia com a app
- **Dependências:** Feature 4.1
- **Notas:** Usar APScheduler no `main.py` startup

### **Feature 4.3: Grid Trading Strategy Logic**
- **Priority:** P1 (Crítico)
- **Effort:** 4
- **Status:** [ ]
- **Descrição:** Implementar lógica de Grid Trading (compra em -1%, vende em +1%)
- **Subtasks:**
  - [ ] Backend: Implementar classe `GridTradingStrategy`
  - [ ] Backend: Método para calcular sinais (BUY/SELL/HOLD)
  - [ ] Backend: Lógica:
    - [ ] Fetch preço atual do ISIN via T212 API
    - [ ] Comparar com average price paid
    - [ ] Se desceu Y% → Sinal BUY
    - [ ] Se subiu Y% → Sinal SELL
  - [ ] Backend: Guardar histórico de sinais em `signals` table
  - [ ] Backend: Logging de sinais
  - [ ] Testes: Verificar cálculos matemáticos
- **Dependências:** Feature 4.1, 4.2
- **Notas:** Y% = `strategy_params.buy_threshold_percent`

### **Feature 4.4: Trade Executor**
- **Priority:** P1 (Crítico)
- **Effort:** 4
- **Status:** [ ]
- **Descrição:** Executar trades via T212 API
- **Subtasks:**
  - [ ] Backend: Implementar classe `TradeExecutor`
  - [ ] Backend: Método para colocar ordem (BUY/SELL)
  - [ ] Backend: Chamar T212 API `/equity/orders/market`
  - [ ] Backend: Guardar ordem em `trades` table
  - [ ] Backend: Guardar T212 order ID
  - [ ] Backend: Error handling (ordem falhou?)
  - [ ] Backend: Retry logic (opcional)
  - [ ] Backend: Logging detalhado
  - [ ] Testes: Verificar integração T212 API
- **Dependências:** Feature 4.3
- **Notas:** 
  - Usar market orders (execução imediata)
  - Buy = quantidade positiva
  - Sell = quantidade negativa (com -)

### **Feature 4.5: Risk Manager**
- **Priority:** P2
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Validação de risco antes de executar trades
- **Subtasks:**
  - [ ] Backend: Implementar classe `RiskManager`
  - [ ] Backend: Validações:
    - [ ] Max position size (% do capital)
    - [ ] Stop-loss level
    - [ ] Max drawdown
    - [ ] Max trades por dia
  - [ ] Backend: Bloquear execução se falhar validação
  - [ ] Backend: Logging do porquê foi bloqueado
  - [ ] Frontend: Mostrar warnings de risco
- **Dependências:** Feature 4.4
- **Notas:** Parâmetros configuráveis em `strategy_params`

### **Feature 4.6: Trade History & Logging**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Ver histórico de trades e logs
- **Subtasks:**
  - [ ] Backend: GET `/api/trades` - Listar trades do user
  - [ ] Backend: GET `/api/trades/{id}` - Detalhe trade
  - [ ] Backend: GET `/api/logs` - Ver logs do sistema
  - [ ] Frontend: Page `/history` - Histórico de trades
  - [ ] Frontend: Tabela com: data, tipo (BUY/SELL), quantidade, preço, P&L, status
  - [ ] Frontend: Filtros (data, tipo, status)
  - [ ] Frontend: Export CSV (opcional)
- **Dependências:** Feature 4.4
- **Notas:** Paginação obrigatória

---

## 🎯 FASE 5: Real-time Updates

### **Feature 5.1: WebSocket Setup**
- **Priority:** P3
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Implementar WebSocket para atualizações live
- **Subtasks:**
  - [ ] Backend: Setup WebSocket com FastAPI
  - [ ] Backend: Endpoint `/ws`
  - [ ] Backend: Conectar usuario via JWT
  - [ ] Frontend: Setup WebSocket client
  - [ ] Frontend: Conectar ao `/ws` com autenticação
  - [ ] Frontend: Reconectar automaticamente se desconectar
  - [ ] Testes: Verificar conexão/desconexão
- **Dependências:** Feature 4.1
- **Notas:** Usar `websockets` library

### **Feature 5.2: Live Position Updates**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Atualizar posições em tempo real
- **Subtasks:**
  - [ ] Backend: Scheduler envia updates via WebSocket
  - [ ] Backend: Quando preço de um ISIN muda
  - [ ] Frontend: Recebe update e atualiza table
  - [ ] Frontend: Mostra badge de "updated" (novo preço)
  - [ ] Testes: Verificar que updates chegam em real-time
- **Dependências:** Feature 5.1
- **Notas:** Enviar apenas para user que tem esse ISIN

### **Feature 5.3: Live P&L Tracking**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Mostrar P&L em tempo real
- **Subtasks:**
  - [ ] Backend: Calcular P&L para cada posição
  - [ ] Backend: Enviar via WebSocket
  - [ ] Frontend: Mostrar P&L em valor e percentagem
  - [ ] Frontend: Color code (verde se lucro, vermelho se perda)
  - [ ] Testes: Verificar cálculos
- **Dependências:** Feature 5.2
- **Notas:** P&L = (currentPrice - avgPrice) * quantity

### **Feature 5.4: Trade Notifications**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Notificações quando um trade é executado
- **Subtasks:**
  - [ ] Backend: Enviar notificação via WebSocket quando trade é executado
  - [ ] Frontend: Toast notification (tipo: success/error/info)
  - [ ] Frontend: Mostrar detalhes (tipo, quantidade, preço, P&L)
  - [ ] Frontend: Opção para ver detalhe do trade
  - [ ] Testes: Verificar notificações
- **Dependências:** Feature 5.1, 4.4
- **Notas:** Toast deve desaparecer após 5s (ou manual close)

---

## 🎯 FASE 6: Dashboard Avançado

### **Feature 6.1: Gráficos com Recharts**
- **Priority:** P3
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Adicionar gráficos para visualizar dados
- **Subtasks:**
  - [ ] Frontend: Instalar Recharts
  - [ ] Frontend: Gráfico de P&L (linha - últimos 7 dias)
  - [ ] Frontend: Gráfico de portfolio (pie - alocação)
  - [ ] Frontend: Gráfico de trades (bar - buy vs sell)
  - [ ] Frontend: Responsivo em mobile
  - [ ] Testes: Verificar que gráficos renderizam
- **Dependências:** Feature 4.6
- **Notas:** Usar dados do histórico de trades

### **Feature 6.2: ISIN Price Chart (T212 Integration)**
- **Priority:** P3
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Mostrar gráfico de preço do ISIN
- **Subtasks:**
  - [ ] Backend: Verificar se T212 API tem endpoint de histórico
  - [ ] Backend: Se não tem, usar fonte externa (yfinance, etc)
  - [ ] Backend: GET `/api/isins/{id}/chart` - Histórico de preços
  - [ ] Frontend: Mostrar gráfico em detail page
  - [ ] Frontend: Selector de timeframe (1d, 5d, 1m, etc)
  - [ ] Testes: Verificar dados do gráfico
- **Dependências:** Feature 3.5
- **Notas:** Ou usar embed do TradingView

### **Feature 6.3: Dashboard KPIs**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Mostrar KPIs principais no dashboard
- **Subtasks:**
  - [ ] Frontend: Mostrar no topo:
    - [ ] Saldo total (€)
    - [ ] P&L total (€ + %)
    - [ ] Número de posições abertas
    - [ ] Trades executados (hoje, semana, mês)
    - [ ] Win rate (%)
  - [ ] Frontend: Cards com formato visual atrativo
  - [ ] Backend: Endpoints para calcular KPIs
- **Dependências:** Feature 4.6
- **Notas:** Atualizar em tempo real

### **Feature 6.4: Filters & Search**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Filtros avançados na tabela de ISINs
- **Subtasks:**
  - [ ] Frontend: Filtro por automation status (ON/OFF)
  - [ ] Frontend: Filtro por P&L (lucro/perda)
  - [ ] Frontend: Search por ISIN/ticker/nome
  - [ ] Frontend: Sort por coluna (clicando no header)
  - [ ] Testes: Verificar filtros
- **Dependências:** Feature 3.1
- **Notas:** Client-side filtering (ou server-side se muitos dados)

---

## 🎯 FASE 7: Testes & QA

### **Feature 7.1: Unit Tests (Backend)**
- **Priority:** P2
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Testes unitários do backend
- **Subtasks:**
  - [ ] Setup pytest
  - [ ] Testes para autenticação
  - [ ] Testes para CRUD ISINs
  - [ ] Testes para estratégia
  - [ ] Testes para executor
  - [ ] Coverage > 70%
- **Dependências:** Todas as features anteriores
- **Notas:** Usar fixtures para mock data

### **Feature 7.2: Integration Tests**
- **Priority:** P2
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Testes de integração completos
- **Subtasks:**
  - [ ] Setup test database (Supabase test project)
  - [ ] Testes end-to-end: add ISIN → enable automation → check trade
  - [ ] Testes de T212 API integration
  - [ ] Testes de WebSocket
- **Dependências:** Feature 7.1
- **Notas:** Usar environment variables de teste

### **Feature 7.3: Frontend Tests (Vitest)**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Testes do frontend
- **Subtasks:**
  - [ ] Setup Vitest
  - [ ] Testes de componentes principais
  - [ ] Testes de integração (login → dashboard)
  - [ ] Coverage > 50%
- **Dependências:** Todas as features frontend
- **Notas:** Usar React Testing Library

### **Feature 7.4: Performance Testing**
- **Priority:** P3
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Testes de performance
- **Subtasks:**
  - [ ] Load testing (quantos users simultâneos?)
  - [ ] Response time (< 200ms)
  - [ ] Frontend bundle size (< 200KB)
  - [ ] BD query performance (< 100ms)
- **Dependências:** Todas as features
- **Notas:** Usar Lighthouse para frontend

---

## 🎯 FASE 8: Documentação & Deployment

### **Feature 8.1: API Documentation (Swagger Enhanced)**
- **Priority:** P2
- **Effort:** 1
- **Status:** [ ]
- **Descrição:** Melhorar documentação do Swagger
- **Subtasks:**
  - [ ] Adicionar descrições detalhadas aos endpoints
  - [ ] Adicionar exemplos de request/response
  - [ ] Documentar error codes
  - [ ] Adicionar auth examples
- **Dependências:** Todas as features
- **Notas:** FastAPI gera Swagger automaticamente

### **Feature 8.2: User Documentation**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Documentação para utilizadores finais
- **Subtasks:**
  - [ ] Guia de setup (primeira vez)
  - [ ] Guia de como adicionar ISIN
  - [ ] Guia de como configurar estratégia
  - [ ] Guia de risk management
  - [ ] FAQ
- **Dependências:** Todas as features
- **Notas:** Hospedar em `/docs` ou Wiki

### **Feature 8.3: Monitoring & Alerts**
- **Priority:** P2
- **Effort:** 2
- **Status:** [ ]
- **Descrição:** Setup de monitoring
- **Subtasks:**
  - [ ] Setup Sentry (error tracking)
  - [ ] Setup logging (Datadog ou similar)
  - [ ] Alertas se app cai
  - [ ] Alertas se T212 API falha
  - [ ] Dashboard de health
- **Dependências:** Deployment completo
- **Notas:** Render tem logs built-in

### **Feature 8.4: Backup Strategy**
- **Priority:** P2
- **Effort:** 1
- **Status:** [ ]
- **Descrição:** Garantir que dados são backupeados
- **Subtasks:**
  - [ ] Supabase: Backups automáticos (já ativa por default)
  - [ ] Verificar retenção de backups
  - [ ] Plano de disaster recovery
  - [ ] Teste de restore
- **Dependências:** Deployment completo
- **Notas:** Supabase cuida disto automaticamente

---

## 🎯 FASE 9: Expansão Futura (Nice-to-Have)

### **Feature 9.1: Mais Estratégias**
- **Priority:** P4
- **Effort:** 3 cada
- **Status:** [ ]
- **Descrição:** Adicionar mais estratégias de trading
- **Subtasks:**
  - [ ] RSI Strategy (Relative Strength Index)
  - [ ] SMA Crossover (Simple Moving Average)
  - [ ] MACD Strategy
  - [ ] Bollinger Bands
- **Dependências:** Feature 4.3 (base strategy framework)
- **Notas:** Usar strategy pattern para fácil extensão

### **Feature 9.2: Mobile App**
- **Priority:** P4
- **Effort:** 5+
- **Status:** [ ]
- **Descrição:** App mobile (iOS/Android)
- **Subtasks:**
  - [ ] React Native ou Flutter
  - [ ] Mesma funcionalidade do web
  - [ ] Push notifications
  - [ ] Offline mode (opcional)
- **Dependências:** Todas as features
- **Notas:** Depois do web estar estável

### **Feature 9.3: Live Trading (não DEMO)**
- **Priority:** P4
- **Effort:** 4
- **Status:** [ ]
- **Descrição:** Mudar de DEMO para trading real
- **Subtasks:**
  - [ ] Adicionar environment variable para T212_ENVIRONMENT = 'live'
  - [ ] Warnings visuais (RED) que é LIVE
  - [ ] Confirmação manual antes de executar trades
  - [ ] Max position size muito menor
  - [ ] Extensive testing com paper trading
- **Dependências:** Todas as features
- **Notas:** ⚠️ CUIDADO: dinheiro real!

### **Feature 9.4: Backtesting Engine**
- **Priority:** P4
- **Effort:** 5+
- **Status:** [ ]
- **Descrição:** Testar estratégias com dados históricos
- **Subtasks:**
  - [ ] Backend: Implementar backtesting logic
  - [ ] Backend: Integrar com yfinance ou similar
  - [ ] Frontend: Page de backtesting
  - [ ] Frontend: Gráficos de resultados
  - [ ] Frontend: Comparação de estratégias
- **Dependências:** Feature 9.1
- **Notas:** Usar OHLC data (Open, High, Low, Close)

### **Feature 9.5: API Pública**
- **Priority:** P4
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Permitir terceiros usar API
- **Subtasks:**
  - [ ] Implementar API keys por user
  - [ ] Rate limiting per key
  - [ ] Documentação
  - [ ] Billing (opcional)
- **Dependências:** Todas as features
- **Notas:** OAuth2 completo

### **Feature 9.6: Multi-Account Support**
- **Priority:** P4
- **Effort:** 3
- **Status:** [ ]
- **Descrição:** Permitir múltiplas contas T212 por user
- **Subtasks:**
  - [ ] Redesenhar data model (accounts table)
  - [ ] Backend: Suportar múltiplas contas
  - [ ] Frontend: Selector de conta
  - [ ] Supabase migrations
- **Dependências:** Feature 3B.1
- **Notas:** BigO: O(n) queries em vez de O(1)

---

## 📊 Priorização

### **P1 - CRÍTICO (MVP essencial)**
```
Feature 1.1: Redesign UI/UX com estilo Trading 212 ⭐ FOUNDATION
Feature 2.1: Login/Register com Supabase Auth
Feature 3.1: GET /isins
Feature 3.2: POST /isins (add ISIN)
Feature 3B.1: GET/PUT /config (credenciais T212)
Feature 4.1: Toggle Automation ON/OFF
Feature 4.2: Scheduler Setup
Feature 4.3: Grid Trading Strategy
Feature 4.4: Trade Executor
```

### **P2 - IMPORTANTE (MVP completo)**
```
Feature 2.2: User Management
Feature 3.3: PUT /isins (editar)
Feature 3.4: DELETE /isins
Feature 3B.2: POST /config/test
Feature 3B.3: Strategy Parameters
Feature 4.5: Risk Manager
Feature 4.6: Trade History & Logging
Feature 7.1: Unit Tests
Feature 8.1: API Documentation
Feature 8.2: User Documentation
```

### **P3 - NICE-TO-HAVE (Polish)**
```
Feature 2.3: Profile/Settings Page
Feature 3.5: ISIN Detail Page
Feature 5.1-5.4: Real-time Updates & WebSocket
Feature 6.1-6.4: Dashboard Avançado
Feature 7.2: Integration Tests
```

### **P4 - EXPANSÃO FUTURA**
```
Feature 9.1-9.6: Mais estratégias, mobile, live trading, etc
```

---

## 📈 Estimativa de Timeline

### **Sem começar nada:**
- ⏳ **Semana 1-2 (P1 features):** ~40-50 horas
- ⏳ **Semana 3 (P2 features):** ~30-40 horas
- ⏳ **Semana 4-5 (P3 features):** ~30-40 horas
- ⏳ **Total MVP completo:** ~5-6 semanas (trabalho full-time)

### **Effort per feature:**
- Effort 1: 1-2 horas
- Effort 2: 2-4 horas
- Effort 3: 4-8 horas
- Effort 4: 8-16 horas
- Effort 5+: 20+ horas

---

## 🚦 Status Legend

- `[ ]` - TODO (não começado)
- `[~]` - IN PROGRESS (a trabalhar)
- `[x]` - DONE (completo e testado)

---

## ⚠️ Dependências Críticas

```
2.1 (Auth) → 3.1 (CRUD) → 4.1 (Automation)
                       ↓
                    3B.1 (Config)
                       ↓
                    4.2 (Scheduler)
                       ↓
                    4.3 (Strategy) → 4.4 (Executor)
```

Se faltam autenticação, nada de features de user funciona.
Se falta CRUD ISINs, não há dados para tratar.
Se falta Strategy, a automação não faz nada.

---

## 📝 Notas Gerais

- **Testes:** Adicionar testes para cada feature (TDD)
- **Documentação:** Atualizar CLAUDE.md com cada feature
- **Commits:** Commit granular (feature branch + PR)
- **Code Review:** Review antes de merge a main
- **Deployment:** Auto-deploy on merge a main

---

## 🎯 Próximo Passo

**Aguardando aprovação para começar o desenvolvimento.**

Quando disser "Começar desenvolvimento", vou:

1. Criar feature branches para cada task
2. Implementar uma feature por vez
3. Fazer testes automatizados
4. Criar commits detalhados
5. Fazer PRs para review
6. Atualizar este backlog à medida que vou fazendo

**Pronto quando disser!** 🚀

---

**Last Updated:** 2026-09-13
**Status:** ⏳ Awaiting approval
**Total Stories:** 30+
**Total Effort:** ~150 hours (MVP completo)
