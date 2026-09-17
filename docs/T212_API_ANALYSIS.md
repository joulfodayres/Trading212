# 📚 Trading 212 API - Análise Completa

**Baseado em:** OpenAPI v3.0.1 (api.yaml)
**Data:** 2026-09-17
**Status:** ✅ Documentação Oficial Completa

---

## 🎯 Conclusão Imediata: SEM WEBHOOKS ❌

**A Trading 212 API NÃO oferece:**
- ❌ Webhooks
- ❌ Callbacks
- ❌ WebSockets
- ❌ Event streaming
- ❌ Real-time notifications

**SOLUÇÃO:** Polling obrigatório com APScheduler

---

## 📋 Endpoints Disponíveis

### **1. ACCOUNTS (Informações da Conta)**

#### `GET /equity/account/summary`
```
Rate Limit: 1 req / 5s
Resposta: AccountSummary
  ├─ id (int64) - Account ID
  ├─ currency (string) - ISO 4217 (ex: EUR)
  ├─ totalValue (number) - Valor total em moeda da conta
  ├─ cash (Cash object)
  │  ├─ availableToTrade (number) - Fundos disponíveis
  │  ├─ inPies (number) - Dinheiro em pies
  │  └─ reservedForOrders (number) - Reservado para ordens pendentes
  └─ investments (Investments object)
     ├─ currentValue (number) - Valor atual dos investimentos
     ├─ totalCost (number) - Custo base
     ├─ unrealizedProfitLoss (number) - P&L não realizado
     └─ realizedProfitLoss (number) - P&L realizado (all-time)
```

**Uso:** Obter saldo, P&L total, fundos disponíveis

---

### **2. POSITIONS (Posições Abertas)**

#### `GET /equity/positions`
```
Rate Limit: 1 req / 1s (AGRESSIVO!)
Query Parameters:
  └─ ticker (optional) - Filtrar por ticker (ex: AAPL_US_EQ)

Resposta: Array de Position
  ├─ instrument (Instrument object)
  │  ├─ ticker (string) - Identificador único (ex: AAPL_US_EQ)
  │  ├─ isin (string) - ISIN do instrumento
  │  ├─ name (string) - Nome completo
  │  └─ currency (string) - ISO 4217
  ├─ quantity (number) - Total de shares
  ├─ currentPrice (number) - Preço atual (em moeda do instrumento)
  ├─ averagePricePaid (number) - Preço médio pago
  ├─ createdAt (datetime) - Quando a posição foi aberta
  ├─ quantityAvailableForTrading (number) - Shares disponíveis para trading
  ├─ quantityInPies (number) - Shares em pies
  └─ walletImpact (PositionWalletImpact)
     ├─ currentValue (number) - Valor de mercado atual
     ├─ totalCost (number) - Custo total
     ├─ unrealizedProfitLoss (number) - P&L da posição
     └─ fxImpact (number) - Impacto de câmbio (se moeda diferente)
```

**Uso:** Base para Grid Trading - detectar mudanças de preço

---

### **3. ORDERS (Gerenciar Ordens)**

#### `GET /equity/orders`
```
Rate Limit: 1 req / 5s
Resposta: Array de Order (apenas ordens PENDENTES)

Order object:
  ├─ id (int64) - Identificador único da ordem
  ├─ ticker (string) - AAPL_US_EQ
  ├─ instrument (Instrument)
  ├─ side (enum) - BUY ou SELL
  ├─ quantity (number) - Total requestado
  ├─ filledQuantity (number) - Já preenchido
  ├─ type (enum) - MARKET, LIMIT, STOP, STOP_LIMIT
  ├─ status (enum) - NEW, CONFIRMED, FILLED, PARTIALLY_FILLED, CANCELLED, etc
  ├─ createdAt (datetime)
  ├─ limitPrice (number) - Para LIMIT/STOP_LIMIT
  ├─ stopPrice (number) - Para STOP/STOP_LIMIT
  ├─ timeInForce (enum) - DAY ou GOOD_TILL_CANCEL
  └─ initiatedFrom (enum) - API, WEB, ANDROID, IOS, SYSTEM, AUTOINVEST
```

**⚠️ IMPORTANTE:** SÓ retorna ordens PENDENTES. Ordens FILLED/CANCELLED não aparecem aqui!

---

#### `GET /equity/orders/{id}`
```
Rate Limit: 1 req / 1s
Resposta: Single Order object
Uso: Checar status de uma ordem específica
```

---

#### `POST /equity/orders/market`
```
Rate Limit: 50 req / 1m (=~0.83 req/s)

Request body (MarketRequest):
  ├─ ticker (string) - AAPL_US_EQ
  ├─ quantity (number) - Positivo=BUY, Negativo=SELL
  └─ extendedHours (boolean, default: false)

Resposta: Order object (com status UNCONFIRMED ou NEW)

⚠️ IMPORTANTE:
  - Ordem pode ter "slippage" - preço final diferente
  - Negative quantity para SELL: use -10 para vender 10 shares
```

---

#### `POST /equity/orders/limit`
```
Rate Limit: 1 req / 2s

Request body (LimitRequest):
  ├─ ticker (string)
  ├─ quantity (number)
  ├─ limitPrice (number)
  └─ timeValidity (enum) - DAY ou GOOD_TILL_CANCEL

Resposta: Order object
Uso: Compra/venda a preço específico ou melhor
```

---

#### `POST /equity/orders/stop`
```
Rate Limit: 1 req / 2s

Request body (StopRequest):
  ├─ ticker (string)
  ├─ quantity (number)
  ├─ stopPrice (number)
  └─ timeValidity (enum)

Resposta: Order object
Uso: Stop loss - dispara ordem de mercado quando preço atinge stopPrice
```

---

#### `POST /equity/orders/stop_limit`
```
Rate Limit: 1 req / 2s

Request body (StopLimitRequest):
  ├─ ticker (string)
  ├─ quantity (number)
  ├─ stopPrice (number)
  ├─ limitPrice (number)
  └─ timeValidity (enum)

Resposta: Order object
Uso: Combina STOP + LIMIT para melhor proteção
```

---

#### `DELETE /equity/orders/{id}`
```
Rate Limit: 50 req / 1m

Resposta: 200 OK (sem body)
Uso: Cancelar ordem pendente

⚠️ NOTA: Cancelamento não garantido se ordem já está sendo preenchida
```

---

### **4. INSTRUMENTS (Catálogo de Instrumentos)**

#### `GET /equity/metadata/instruments`
```
Rate Limit: 1 req / 50s (MUITO LENTO!)

Resposta: Array de TradableInstrument
  ├─ ticker (string) - AAPL_US_EQ
  ├─ isin (string)
  ├─ name (string)
  ├─ shortName (string)
  ├─ type (enum) - STOCK, ETF, CRYPTO, INDEX, FOREX, etc
  ├─ currencyCode (string) - ISO 4217
  ├─ extendedHours (boolean)
  ├─ maxOpenQuantity (number) - Máximo de shares por posição
  ├─ addedOn (datetime)
  └─ workingScheduleId (int64)

⚠️ DATA ANTIGA: Refrescada a cada 10 minutos
```

---

#### `GET /equity/metadata/exchanges`
```
Rate Limit: 1 req / 30s

Resposta: Array de Exchange
  ├─ id (int64)
  ├─ name (string)
  └─ workingSchedules (array)
     └─ timeEvents (array)
        ├─ date (datetime)
        └─ type (enum) - OPEN, CLOSE, PRE_MARKET_OPEN, AFTER_HOURS_OPEN, etc
```

---

### **5. HISTORICAL DATA (Histórico)**

#### `GET /equity/history/orders`
```
Rate Limit: 6 req / 1m (=0.1 req/s)
Pagination: Cursor-based, limit max 50

Query Parameters:
  ├─ cursor (optional) - Para próxima página
  ├─ limit (default: 20, max: 50)
  └─ ticker (optional)

Resposta: PaginatedResponseHistoricalOrder
  ├─ items (array de HistoricalOrder)
  │  ├─ order (Order object)
  │  └─ fill (Fill object)
  │     ├─ filledAt (datetime)
  │     ├─ price (number)
  │     ├─ quantity (number)
  │     ├─ type (enum) - TRADE, STOCK_SPLIT, DIVIDEND, etc
  │     └─ walletImpact (detalhes de câmbio e impostos)
  └─ nextPagePath (string) - Para próxima página

⚠️ LENTO: Rate limit baixo. Usar com cuidado em loops.
```

---

#### `GET /equity/history/dividends`
```
Rate Limit: 6 req / 1m

Resposta: PaginatedResponseHistoryDividendItem
  ├─ instrument
  ├─ paidOn (datetime)
  ├─ quantity (number)
  ├─ amount (number)
  ├─ type (enum) - ORDINARY, BONUS, INTEREST, etc
  └─ ... muitos outros tipos
```

---

#### `GET /equity/history/transactions`
```
Rate Limit: 6 req / 1m

Query Parameters:
  ├─ time (optional) - Filtrar por data
  ├─ cursor (optional)
  └─ limit (max 50)

Resposta: Array de HistoryTransactionItem
  ├─ dateTime
  ├─ type (enum) - DEPOSIT, WITHDRAW, FEE, TRANSFER, INTEREST, LENDING_INTEREST
  ├─ amount
  └─ currency
```

---

#### `GET /api/v0/equity/history/exports` + `POST /api/v0/equity/history/exports`
```
ASYNC WORKFLOW:
1. POST /history/exports → reportId
2. GET /history/exports → Check status (Queued/Processing/Finished)
3. Quando Finished → downloadLink com CSV

Serve para: Gerar relatórios CSV completos (muito lento)
```

---

## ⚡ Rate Limits Resumo

| Endpoint | Limite | Observações |
|----------|--------|------------|
| GET `/account/summary` | 1 req / 5s | Polling: máx 12 req/min |
| GET `/positions` | 1 req / 1s | Polling: máx 60 req/min ⚡ RÁPIDO |
| GET `/orders` | 1 req / 5s | Polling: máx 12 req/min |
| GET `/orders/{id}` | 1 req / 1s | Polling: máx 60 req/min |
| POST `/orders/market` | 50 req / 1m | Burst: 0.83 req/s |
| POST `/orders/limit` | 1 req / 2s | Polling: máx 30 req/min |
| POST `/orders/stop` | 1 req / 2s | Polling: máx 30 req/min |
| POST `/orders/stop_limit` | 1 req / 2s | Polling: máx 30 req/min |
| DELETE `/orders/{id}` | 50 req / 1m | Burst: 0.83 req/s |
| GET `/instruments` | 1 req / 50s | ⚠️ MUITO LENTO - cache! |
| GET `/history/orders` | 6 req / 1m | Polling: máx 0.1 req/s |
| GET `/history/dividends` | 6 req / 1m | Polling: máx 0.1 req/s |
| GET `/history/transactions` | 6 req / 1m | Polling: máx 0.1 req/s |

**⚠️ NOTA:** Limites são **POR ACCOUNT**, não por API key ou IP!

---

## 🔐 Autenticação

**Tipo:** HTTP Basic Authentication

```bash
# Encoding das credenciais:
CREDENTIALS=$(echo -n "API_KEY:API_SECRET" | base64 | tr -d '\n')

# Request:
curl -X GET "https://live.trading212.com/api/v0/equity/account/summary" \
  -H "Authorization: Basic $CREDENTIALS"
```

**Python:**
```python
import requests

auth = (api_key, api_secret)  # requests faz o base64 automaticamente
response = requests.get(url, auth=auth)
```

---

## 📝 Limitações da API

### ✅ Suportado
- Apenas contas **Invest** ou **Stocks ISA**
- Ordens em **moeda primária** da conta
- Múltiplos tipos de ordem: MARKET, LIMIT, STOP, STOP_LIMIT
- Histórico completo de trades
- Divisões de stock, dividendos, etc

### ❌ NÃO Suportado
- ❌ Webhooks ou callbacks
- ❌ Multi-currency (moedas secundárias)
- ❌ Ordens por VALOR (só por QUANTIDADE)
- ❌ Margin trading / shorting
- ❌ Mais de 50 ordens pendentes por ticker
- ❌ Contas Demo não têm histórico real

---

## 🎯 Ordem de Negócio

### **SELL (Vender)**
```
quantity = -10  # NEGATIVO!

POST /equity/orders/market
{
  "ticker": "AAPL_US_EQ",
  "quantity": -10  # Vender 10 shares
}
```

### **BUY (Comprar)**
```
quantity = 10  # POSITIVO!

POST /equity/orders/market
{
  "ticker": "AAPL_US_EQ",
  "quantity": 10  # Comprar 10 shares
}
```

---

## 📊 Order Status Lifecycle

```
LOCAL (nunca enviado)
  ↓
UNCONFIRMED (enviado, aguardando confirmação)
  ↓
CONFIRMED (T212 confirmou)
  ↓
NEW (pronto para execução)
  ├─ PARTIALLY_FILLED (preenchimento parcial)
  │  └─ FILLED (completamente preenchido) ✅
  ├─ CANCELLING
  │  └─ CANCELLED ❌
  └─ REJECTED ❌

REPLACING → REPLACED (modificação de ordem)
```

---

## 🔄 Detecção de Execução (Grid Trading)

### **PROBLEMA:** Sem webhooks ❌

### **SOLUÇÃO:** Polling + Reconciliation

```python
# A cada 5 segundos:
current_orders = t212_client.get_pending_orders()
current_ids = {o['id'] for o in current_orders}

# Comparar com BD:
db_pending_ids = {t['t212_order_id'] for t in db_pending_trades}

# Ordens desaparecidas = foram FILLED
filled_ids = db_pending_ids - current_ids

for order_id in filled_ids:
    # Buscar detalhes em /history/orders
    history = t212_client.get_order_history()
    for historical in history['items']:
        if historical['order']['id'] == order_id:
            # Atualizar BD com preço de execução
            update_trade_status(order_id, "EXECUTED", historical['fill']['price'])
```

---

## 💡 Implementação para Grid Trading

### **Fluxo Recomendado:**

```python
# 1. A cada 5 segundos:
scheduler.add_job(
    monitor_orders,
    'interval',
    seconds=5
)

async def monitor_orders():
    # Polling de ordens pendentes
    pending = t212_client.get_pending_orders()
    
    # Detectar execuções
    for order in pending:
        if order['status'] == 'FILLED':
            await on_order_filled(order)

# 2. Quando ordem executada:
async def on_order_filled(order):
    # Calcular P&L
    pnl_percent = calculate_pnl(order)
    
    # Grid Trading logic:
    if pnl_percent > 1.0:  # Lucro > 1%
        # VENDER 50% para lock-in
        await place_sell_order(order['ticker'], qty=order['quantity']/2)
    elif pnl_percent < -1.0:  # Perda > 1%
        # COMPRAR mais para average-down
        await place_buy_order(order['ticker'], qty=order['quantity'])

# 3. Rate limit safe:
# - GET /positions: 1 req/1s = OK para polling a cada 1-2s
# - GET /orders: 1 req/5s = OK para polling a cada 5-10s
# - POST /orders/market: 50 req/1m = OK para até 1 ordem/s
```

---

## 📌 Diferenças: Demo vs Live

| Aspecto | Demo | Live |
|--------|------|------|
| **URL** | https://demo.trading212.com/api/v0 | https://live.trading212.com/api/v0 |
| **Dinheiro Real** | Não (papel) | ⚠️ Sim |
| **Histórico** | Pode não ter dados reais | Completo |
| **Rate Limits** | Iguais | Iguais |
| **Execução** | Instantânea (geralmente) | Sujeita a liquidity |

---

## 🛠️ Ferramentas Necessárias

```python
# Implementar no backend:

1. Trading212Client (✅ JÁ TEMOS)
   - All endpoints

2. APScheduler (FALTA)
   - run monitor_orders() a cada 5s

3. Reconciliation Logic (FALTA)
   - Detectar ordem FILLED
   - Buscar detalhes em /history/orders
   - Calcular P&L real

4. Grid Trading Engine (FALTA)
   - Aplicar lógica: +1% VENDER / -1% COMPRAR
   - Evitar loops infinitos

5. WebSocket (OPCIONAL - Futuro)
   - Broadcast updates aos clientes
   - Mesmo não tendo webhook T212, frontend quer updates
```

---

## 🎯 Próximos Passos

### **Phase 4 - Grid Trading:**

1. **Implementar APScheduler** ⭐⭐⭐
   ```python
   # backend/engine/scheduler.py
   # - monitor_orders() a cada 5s
   # - Detectar FILLED orders
   # - Disparar grid_trading_logic()
   ```

2. **Implementar Grid Trading Logic** ⭐⭐⭐
   ```python
   # backend/engine/strategy.py
   # - +1% de P&L → VENDER 50%
   # - -1% de P&L → COMPRAR mais
   # - Parâmetros configuráveis por ISIN
   ```

3. **Adicionar métodos ao Trading212Client** ⭐⭐
   ```python
   # backend/api/trading212.py
   # - place_limit_order() (já temos POST implementado)
   # - place_stop_order() (já temos POST implementado)
   # - place_stop_limit_order() (já temos POST implementado)
   # - search_instrument_by_ticker() (lista é enorme!)
   ```

4. **Reconciliation com Histórico** ⭐
   ```python
   # Quando GET /orders não mostra a ordem:
   # 1. Chamar GET /history/orders com limit=50
   # 2. Procurar order_id
   # 3. Se encontrar: status=FILLED, preço=fill['price']
   # 4. Se não encontrar: pode estar ainda em processamento
   ```

5. **Frontend WebSocket** (Futuro)
   ```python
   # broadcast order status updates
   # broadcast P&L updates
   # broadcast trade history
   ```

---

## 🚀 Resumo Executivo

| Pergunta | Resposta |
|----------|----------|
| **Webhooks?** | ❌ Não existem |
| **Polling?** | ✅ Obrigatório |
| **Rate limits?** | ✅ Generosos (permite polling a cada 1-5s) |
| **Ordem tipos?** | ✅ MARKET, LIMIT, STOP, STOP_LIMIT |
| **Detecção de execução?** | ✅ Via polling + reconciliation |
| **Grid Trading?** | ✅ Possível com APScheduler |
| **Delay máximo?** | ~5 segundos (polling interval) |

---

**Status:** ✅ Pronto para implementação Phase 4
**Data:** 2026-09-17
**Próximo:** Implementar APScheduler + Grid Trading Logic
