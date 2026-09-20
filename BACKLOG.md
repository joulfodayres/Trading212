# 📋 Trading 212 Bot - Backlog

## 🎯 Próximas Features (Prioridade)

### 1. 🎛️ Tabelas para Edição de Parâmetros de Estratégia
**Status:** TODO
**Descrição:** 
- Interface no dashboard para editar parâmetros de estratégia (param1, param2 por posição)
- Tabela interativa mostrando positions (-1, 0, 1, etc)
- CRUD de strategy_parameters via API
- Validação de valores (param1 negativo, param2 positivo, ranges razoáveis)
- Botão "Guardar" que atualiza BD e notifica frontend com toast/dialog

**Dependências:**
- [ ] Backend: POST/PUT/DELETE endpoints em `/api/v1/strategies/{id}/parameters`
- [ ] Frontend: Página StrategyParameters com tabela editável
- [ ] DB: Já existe strategy_parameters table

**Impacto:** Permite customização dinâmica de estratégias sem reload de código

---

### 2. 📁 Upload de Ficheiros Reais do T212
**Status:** TODO
**Descrição:**
- Endpoint para upload de CSV/Excel exportados da T212
- Parser para ler histórico de trades, posições, contas
- Import de ISINs + histórico para BD
- Validação de dados (ISINs válidos, valores numéricos, datas corretas)
- Feedback ao user (X ISINs importados, Y erros, Z avisos)

**Dependências:**
- [ ] Backend: POST `/api/v1/upload/t212-data` (file upload)
- [ ] Backend: CSV parser + validator
- [ ] Frontend: Upload form com drag-and-drop
- [ ] DB: Verificar se precisa nova tabela de histórico

**Impacto:** Permite começar com dados reais em vez de mock data

---

### 3. 📊 Fazer Gráficos e Estatísticas dos Ficheiros Reais
**Status:** TODO
**Descrição:**
- Dashboard de estatísticas: total P&L, gain%, volatility, etc
- Gráficos (Recharts):
  - Equity curve (Portfolio value over time)
  - Win/Loss ratio
  - Monthly returns
  - Drawdown analysis
  - ISINs performance comparison
- Tabelas de trades executadas (histórico)
- Filtros por data, por ISIN, por estratégia

**Dependências:**
- [ ] Frontend: Gráficos com Recharts
- [ ] Backend: Endpoints para cálculos estatísticos
- [ ] Data: Histórico de trades/posições na BD

**Impacto:** Visibilidade total da performance, permite backtesting visual

---

### 4. 🎚️ Botão para Ligar/Desligar o Engine de Automação
**Status:** TODO
**Descrição:**
- Toggle switch no header/dashboard para ON/OFF global do automation engine
- Toggle por ISIN (automation_enabled já existe, falta UI)
- Status visual: "Automation: ON ✅" ou "Automation: OFF ❌"
- Ao desligar: cancela todas as ordens pendentes (W) ou deixa correr?
- Confirmação: "Tens a certeza? Isto vai [ação]"

**Dependências:**
- [ ] Backend: PUT `/api/v1/automation/enable` e `/api/v1/automation/disable`
- [ ] Frontend: Toggle component em Sidebar + Toolbar
- [ ] DB: Verificar se usa app_parameters.grid_trading_enabled

**Impacto:** Controlo total do sistema, segurança (é fácil parar)

---

### 5. 💬 Dialog Box quando se Automatiza o ISIN: Mostrar Alterações
**Status:** TODO
**Descrição:**
- Quando user clica "Automatizar este ISIN":
  1. Dialog pop-up mostrando o que vai acontecer:
     - Strategy a usar: "Grid Trading 1%"
     - Investment inicial: "€10.00"
     - Grid levels: "-0.1% / +0.1%"
     - Primeira ordem esperada em: "15s (próximo ciclo)"
  2. Mostrar parâmetros por posição (pos=-1, 0, 1)
  3. Botão de confirmação: "Confirmar & Automatizar"
  4. Após confirmação:
     - Set initial_trade=TRUE, automation_enabled=TRUE
     - Toast: "✅ ISIN automatizado! Primeira ciclo em ~15s"
     - Redirect para dashboard mostrando o ISIN em "monitorização"

**Dependências:**
- [ ] Frontend: Modal/Dialog component
- [ ] Backend: GET `/api/v1/strategy/{id}/preview` (retorna parâmetros, estimativas)
- [ ] Frontend: Componente de confirmação reutilizável

**Impacto:** User experience, evita erros (confirmar intenção antes de mudar)

---

## 📅 Timeline Estimada

| Ordem | Item | Complexidade | Tempo (horas) | Dependências |
|-------|------|-------------|--------------|-------------|
| 1 | #4 - Toggle ON/OFF | ⭐ Baixa | 2-3h | Backend endpoints simples |
| 2 | #1 - Tabelas Parâmetros | ⭐⭐ Média | 4-6h | CRUD endpoints + UI |
| 3 | #5 - Dialog Confirmação | ⭐⭐ Média | 3-4h | UI component + backend preview |
| 4 | #2 - Upload Ficheiros | ⭐⭐⭐ Alta | 6-8h | Parser CSV + validação |
| 5 | #3 - Gráficos & Stats | ⭐⭐⭐ Alta | 8-10h | Recharts + backend stats |

**Total:** ~25-35 horas

---

## 🔗 Relacionadas (Não Nesta Lista)
- WebSocket real-time updates
- Mais estratégias (RSI, SMA, etc)
- Mobile app
- Backtesting engine
- Live trading (não DEMO)

---

## ✅ Checklist
- [ ] Priorizar backlog com user
- [ ] Definir sprints (1 feature por semana?)
- [ ] Começar por #4 (mais rápido, low-risk)
- [ ] Testar Phase 4 automation engine com real ISINs
- [ ] Monitorar performance em produção

---

**Última atualização:** 2026-09-20
**Status:** Backlog criado, pronto para desenvolvimento
