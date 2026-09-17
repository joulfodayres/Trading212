# 📋 Acesso a Histórico de Ordens Específicas

**Data:** 2026-09-17  
**Pergunta:** Depois de uma ordem executada, há hipótese de aceder ao histórico dessa ordem específica por ID?

---

## ✅ Resposta Curta:

**SIM, mas com NUANCES:**

| Situação | Endpoint | Funciona? |
|----------|----------|-----------|
| Ordem PENDENTE (não executada ainda) | `GET /equity/orders/{id}` | ✅ **SIM** |
| Ordem EXECUTADA (preenchida) | `GET /equity/orders/{id}` | ❌ **NÃO** (retorna 404) |
| Ordem EXECUTADA (historicamente) | `GET /equity/history/orders?ticker=...` | ✅ **SIM** (mas com paginação) |
| Ordem EXECUTADA (por ID direto) | **NÃO EXISTE** | ❌ **NÃO** |

---

## 🔍 Detalhamento

### **1. GET /equity/orders/{id}** — Ordens PENDENTES APENAS

```
Endpoint: GET /api/v0/equity/orders/{id}
Rate Limit: 1 req / 1s
Resposta: Order object (schema completo)

Retorna:
  ✅ Ordens CONFIRMADAS
  ✅ Ordens NOVO
  ✅ Ordens PARCIALMENTE_PREENCHIDAS
  ❌ Ordens PREENCHIDAS (FILLED)
  ❌ Ordens CANCELADAS
  ❌ Ordens REJEITADAS

Error: 404 Not Found se ordem não está em estado pendente
```

**Problema:** Quando uma ordem é PREENCHIDA, desaparece deste endpoint!

---

### **2. GET /equity/history/orders** — Histórico COM PAGINAÇÃO

```
Endpoint: GET /api/v0/equity/history/orders
Rate Limit: 6 req / 1m (=0.1 req/s, MUITO LENTO!)

Query Parameters:
  ├─ limit (optional, default: 20, max: 50)
  ├─ cursor (optional, para próxima página)
  └─ ticker (optional, filtrar por ticker)

Resposta:
{
  "items": [
    {
      "order": { Order object completo },
      "fill": { Fill object com preço de execução }
    },
    ...
  ],
  "nextPagePath": "/api/v0/equity/history/orders?limit=20&cursor=1760346100000"
}
```

**⚠️ PROBLEMA:** 
- Retorna LISTA, não um item específico por ID
- Sem filtro por order_id
- Tens que fazer paginação até encontrares
- **LENTO** (6 req/min)

---

## 💡 Fluxo de Detecção (CORRETO)

### **Quando colocas uma ordem:**

```python
# 1. Place order
response = t212_client.place_market_order(
    ticker="AAPL_US_EQ",
    quantity=10
)
order_id = response['id']  # ex: 123456789

# Guardar na BD
db.insert('trades', {
    'id': uuid4(),
    't212_order_id': order_id,  # 123456789
    'status': 'PENDING',
    'ticker': 'AAPL_US_EQ',
    'created_at': now()
})
```

### **Enquanto order está PENDENTE (primeiros 5-10 segundos):**

```python
# 2. Check pending order by ID
response = t212_client.get_order_by_id(order_id)  # ✅ FUNCIONA

if response['status'] == 'FILLED':
    print("✅ Ordem PREENCHIDA")
elif response['status'] == 'PARTIALLY_FILLED':
    print("⏳ Ordem PARCIALMENTE PREENCHIDA")
else:
    print("⏳ Ainda pendente:", response['status'])
```

### **DEPOIS que ordem é PREENCHIDA:**

```python
# 3. GET /orders/{id} agora retorna 404 ❌
response = t212_client.get_order_by_id(order_id)
# → Error: 404 Not Found

# 4. Tens que ir ao histórico ✅
# MAS não há endpoint direto por ID!
# Opção A: Procurar em GET /history/orders (LENTO, paginação)
# Opção B: Confiar que a ordem foi preenchida se desapareceu de GET /orders

# Opção A (Segura mas lenta):
history = t212_client.get_order_history(limit=50)
for historical_order in history['items']:
    if historical_order['order']['id'] == order_id:
        print(f"✅ Encontrada! Preço: {historical_order['fill']['price']}")
        break

# Opção B (Rápida mas menos precisa):
# Se a ordem desapareceu de GET /orders
# → Assumir que foi PREENCHIDA
# → Fazer polling de GET /positions para detectar mudança na quantity
```

---

## 🎯 Estratégia Recomendada para Grid Trading

### **Fase 1: Monitorar Ordem Pendente (0-10 segundos)**

```python
async def monitor_pending_order(order_id):
    max_retries = 10  # ~10 segundos
    
    for i in range(max_retries):
        try:
            order = t212_client.get_order_by_id(order_id)
            
            if order['status'] == 'FILLED':
                return ('FILLED', order)
            elif order['status'] == 'PARTIALLY_FILLED':
                # Aguardar mais
                await asyncio.sleep(1)
            elif order['status'] == 'REJECTED':
                return ('REJECTED', order)
            elif order['status'] == 'CANCELLED':
                return ('CANCELLED', order)
            else:
                # NEW, CONFIRMED, etc
                await asyncio.sleep(1)
        
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # Ordem desapareceu! Provavelmente FILLED
                return ('PROBABLY_FILLED', None)
            raise
    
    return ('TIMEOUT', None)
```

### **Fase 2: Confirmar Execução (se necessário)**

```python
async def confirm_execution(order_id, ticker):
    """
    Se ordem desapareceu de GET /orders,
    confirmar em histórico
    """
    
    # Fazer polling de /history/orders até encontrar
    cursor = None
    max_pages = 5  # Limitar procura aos últimos 5 páginas
    
    for page in range(max_pages):
        history = t212_client.get_order_history(
            ticker=ticker,
            limit=50,
            cursor=cursor
        )
        
        for historical_order in history['items']:
            if historical_order['order']['id'] == order_id:
                fill = historical_order['fill']
                return {
                    'status': 'FILLED',
                    'price': fill['price'],
                    'quantity': fill['quantity'],
                    'filled_at': fill['filledAt'],
                    'type': fill['type']
                }
        
        if not history['nextPagePath']:
            break
        
        cursor = extract_cursor(history['nextPagePath'])
    
    return {'status': 'NOT_FOUND_IN_HISTORY'}
```

---

## 📊 Endpoints Relacionados

| Endpoint | Descrição | Rate Limit | Para Detectar Execução? |
|----------|-----------|-----------|------------------------|
| `GET /orders/{id}` | Ordem pendente por ID | 1 req/1s | ✅ PENDENTES |
| `GET /orders` | Todas as ordens pendentes | 1 req/5s | ✅ LISTA COMPLETA |
| `GET /history/orders` | Histórico COM paginação | 6 req/1m | ✅ PREENCHIDAS (lento) |
| `GET /positions` | Posições abertas | 1 req/1s | ✅ INDIRETAMENTE (quantidade mudou) |

---

## ⚠️ Limitações & Workarounds

### **Limitação 1: Sem GET /history/orders/{id}**

**Problema:** Não há endpoint direto para buscar ordem executada por ID

**Workaround:**
```python
# Opção 1: Confiar em GET /orders desaparecimento
if get_order_by_id(order_id) raises 404:
    # → Ordem foi FILLED

# Opção 2: Procurar em histórico com ticker
history = get_order_history(ticker=ticker, limit=50)
# E filtrar por order_id na aplicação

# Opção 3: Usar GET /positions
# Se quantity aumentou/diminuiu → ordem foi preenchida
positions_before = get_positions()
# ... aguardar execução ...
positions_after = get_positions()
if positions_after['quantity'] != positions_before['quantity']:
    # → Ordem foi FILLED
```

### **Limitação 2: Rate Limit Baixo em /history/orders**

**Problema:** `6 req/1m` é muito lento

**Workaround:**
```python
# Cache de histórico em BD
# Última vez que sincronizamos: T0
# Se agora é T0 + 5min, sincronizar

# Usar cursor-based pagination
# Guardar `nextPagePath` após cada fetch
# Só fazer polling se realmente necessário

# Preferir GET /orders (mais rápido)
# GET /history/orders apenas como fallback
```

### **Limitação 3: Sem notificações de execução**

**Problema:** Sem webhooks, tens que fazer polling

**Workaround:**
```python
# APScheduler a cada 5 segundos:
@scheduler.scheduled_job('interval', seconds=5)
async def check_orders():
    pending_orders = get_pending_orders()
    
    # Se uma ordem sumiu:
    # → Provavelmente foi FILLED
    # → Dispara grid_trading_logic()
```

---

## 🛠️ Implementação no Código

### **Adicionar ao Trading212Client:**

```python
# backend/api/trading212.py

def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
    """GET /equity/orders/{id} — Ordem pendente por ID"""
    url = f"{self.base_url}/equity/orders/{order_id}"
    response = self.session.get(url)
    self._handle_rate_limit(response)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        logger.warning(f"Order {order_id} not found (probably FILLED)")
        raise OrderNotFoundError(f"Order {order_id} not found")
    else:
        logger.error(f"Erro ao obter ordem: {response.status_code}")
        raise Exception(f"Erro T212 API: {response.status_code}")

def search_order_in_history(self, order_id: int, ticker: str) -> Optional[Dict[str, Any]]:
    """
    Procurar ordem executada em histórico
    (Operação LENTA - usar com cuidado)
    """
    cursor = None
    pages_checked = 0
    max_pages = 5
    
    while pages_checked < max_pages:
        try:
            history = self.get_order_history(ticker=ticker, limit=50, cursor=cursor)
            
            for historical_order in history.get('items', []):
                if historical_order['order']['id'] == order_id:
                    return historical_order
            
            next_path = history.get('nextPagePath')
            if not next_path:
                break
            
            # Extrair cursor do nextPagePath
            cursor = extract_cursor_from_path(next_path)
            pages_checked += 1
        
        except Exception as e:
            logger.error(f"Error searching order history: {e}")
            break
    
    return None
```

---

## 🎯 Fluxo Recomendado para Grid Trading

```python
# Sequência de eventos:

# 1. COLOCAR ORDEM (T=0)
order = t212_client.place_market_order(ticker="AAPL_US_EQ", quantity=10)
order_id = order['id']

# Guardar em BD
db.insert('trades', {
    't212_order_id': order_id,
    'status': 'PENDING',
    'created_at': now()
})

# 2. MONITORAR POR 10 SEGUNDOS (T=0 → T=10)
for i in range(10):
    try:
        order_status = t212_client.get_order_by_id(order_id)
        
        if order_status['status'] == 'FILLED':
            # ✅ PREENCHIDA
            db.update('trades', {'status': 'FILLED'})
            await trigger_grid_trading_logic(order_id)
            break
    
    except OrderNotFoundError:
        # Ordem desapareceu = provavelmente FILLED
        db.update('trades', {'status': 'PROBABLY_FILLED'})
        await trigger_grid_trading_logic(order_id)
        break
    
    await asyncio.sleep(1)

# 3. SE AINDA PENDENTE (T>10)
# Deixar em BD e monitorar no próximo ciclo de APScheduler
```

---

## 📌 Resumo Executivo

| Caso de Uso | Solução |
|-------------|---------|
| **"Qual é o status da minha ordem 123?"** (pendente) | `GET /orders/123` ✅ |
| **"Qual é o status da minha ordem 123?"** (executada) | `GET /orders/123` → 404 ❌, usar histórico |
| **"Que preço executou a ordem 123?"** | `GET /history/orders?ticker=X`, procurar |
| **"Foi a ordem 123 executada?"** | Se `GET /orders/123` → 404 = Sim ✅ |
| **"Detectar execução em tempo real"** | Polling `GET /orders` a cada 5s |
| **"Confirmar execução após desaparecer"** | Polling `GET /history/orders` (lento) |

---

**Status:** ✅ Documentado  
**Próximo:** Implementar no backend  
**Data:** 2026-09-17
