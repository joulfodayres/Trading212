# ⏰ Filtro de Data em /history/orders — Limitações

**Data:** 2026-09-17  
**Pergunta:** Quando usar /history/orders, tenho que fazer fetch a TUDO desde o início dos tempos, ou posso filtrar por data?

---

## ❌ Resposta Curta:

**NÃO há filtro de data em `/history/orders`!**

```
GET /api/v0/equity/history/orders
├─ cursor (paginação) ✅
├─ ticker (filtro por instrumento) ✅
├─ limit (máximo 50) ✅
└─ time (FILTRO DE DATA) ❌ NÃO EXISTE
```

---

## 📊 Comparação: /history/orders vs /history/transactions

| Endpoint | Parâmetros | Filtro de Data? |
|----------|-----------|-----------------|
| `GET /equity/history/orders` | `cursor`, `ticker`, `limit` | ❌ **NÃO** |
| `GET /equity/history/transactions` | `cursor`, `time`, `limit` | ✅ **SIM** |
| `GET /equity/history/dividends` | `cursor`, `ticker`, `limit` | ❌ **NÃO** |

---

## 🔍 Detalhamento

### **/history/orders** — SEM filtro de data

```yaml
Endpoint: GET /api/v0/equity/history/orders
Rate Limit: 6 req / 1m
Parâmetros:
  - cursor (int64, opcional) - Paginação
  - ticker (string, opcional) - Filtrar por instrumento
  - limit (int, opcional, default: 20, max: 50) - Items por página

Descrição Oficial:
  "Get historical orders data"
  (Nenhuma menção a filtro de data)
```

**Conclusão:** Tens que fazer paginação desde o início até encontrares.

---

### **/history/transactions** — COM filtro de data ✅

```yaml
Endpoint: GET /api/v0/equity/history/transactions
Rate Limit: 6 req / 1m
Parâmetros:
  - cursor (string, opcional) - Paginação
  - time (datetime ISO 8601, opcional) - ⭐ FILTRO DE DATA
  - limit (int, opcional, default: 20, max: 50) - Items por página

Descrição Oficial:
  "Retrieve transactions starting from the specified time"
  ✅ SIM TEM FILTRO!
```

**Formato do parâmetro `time`:**

```bash
# ISO 8601 format
GET /equity/history/transactions?time=2026-09-17T10:00:00Z

# Com timezone
GET /equity/history/transactions?time=2026-09-17T10:00:00+00:00

# Com timezone offset
GET /equity/history/transactions?time=2026-09-17T10:00:00-05:00
```

---

## ⚠️ O Problema Prático

### **Se quiseres histórico de ordens desde ontem:**

```python
# ❌ ERRADO - Esperar que exista parâmetro time
response = requests.get(
    "https://demo.trading212.com/api/v0/equity/history/orders",
    params={
        "time": "2026-09-16T00:00:00Z"  # ❌ Não funciona!
    },
    auth=auth
)
# → Erro 400: Bad filtering arguments

# ✅ CORRETO - Fazer paginação e filtrar na aplicação
response = requests.get(
    "https://demo.trading212.com/api/v0/equity/history/orders",
    params={"limit": 50},
    auth=auth
)

data = response.json()
cutoff_date = datetime(2026, 9, 16, 0, 0, 0)

for historical_order in data['items']:
    order_date = datetime.fromisoformat(
        historical_order['fill']['filledAt']
    )
    
    if order_date >= cutoff_date:
        print(f"Ordem de {order_date}: {historical_order}")
    else:
        break  # Assumir que está ordenado por data DESC
```

---

## 🎯 Estratégias Alternativas

### **Estratégia 1: Filtrar na Aplicação (Simples mas Lento)**

```python
def get_orders_since(date_from: datetime):
    """Fetch ordens desde uma certa data (lento)"""
    all_orders = []
    cursor = None
    
    while True:
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={
                "limit": 50,
                "cursor": cursor
            },
            auth=auth
        )
        
        data = response.json()
        
        for historical_order in data['items']:
            fill_date = datetime.fromisoformat(
                historical_order['fill']['filledAt'].replace('Z', '+00:00')
            )
            
            if fill_date >= date_from:
                all_orders.append(historical_order)
            else:
                # Assumir ordenado por data DESC
                return all_orders
        
        if not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
        time.sleep(10)  # Rate limit
    
    return all_orders
```

**Problema:** Se queres ordens de 2 meses atrás, tens que fazer paginação até lá!

---

### **Estratégia 2: Guardar em BD (Recomendado)**

```python
# Primeira vez: fetch tudo
def sync_all_order_history():
    """Fazer sync completo do histórico"""
    cursor = None
    synced_count = 0
    
    while True:
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={"limit": 50, "cursor": cursor},
            auth=auth
        )
        
        data = response.json()
        
        for historical_order in data['items']:
            order_id = historical_order['order']['id']
            fill_date = historical_order['fill']['filledAt']
            
            # Guardar em BD (se ainda não existe)
            try:
                db.insert('order_history', {
                    't212_order_id': order_id,
                    'ticker': historical_order['order']['ticker'],
                    'side': historical_order['order']['side'],
                    'quantity': historical_order['fill']['quantity'],
                    'price': historical_order['fill']['price'],
                    'filled_at': fill_date,
                    'pnl': historical_order['fill']['walletImpact']['realisedProfitLoss']
                })
                synced_count += 1
            except IntegrityError:
                # Já existe
                pass
        
        if not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
        time.sleep(10)
    
    print(f"✅ Synced {synced_count} orders")
    return synced_count

# Depois: queries rápidas na BD
def get_orders_since(date_from):
    """Queries RÁPIDAS na BD local"""
    result = db.client.table('order_history')\
        .select('*')\
        .gte('filled_at', date_from.isoformat())\
        .order('filled_at', desc=True)\
        .execute()
    
    return result.data
```

**Vantagem:** Query rápida na BD em vez de chamar T212 repetidas vezes.

---

### **Estratégia 3: Incremental Sync (Melhor)**

```python
def incremental_sync_orders():
    """
    Sync apenas NOVAS ordens desde última sincronização
    
    Funciona porque:
    1. /history/orders retorna ordenado por data DESC
    2. Podemos parar quando encontramos última ordem conhecida
    """
    
    # Obter timestamp da última ordem sincronizada
    last_order = db.client.table('order_history')\
        .select('filled_at')\
        .order('filled_at', desc=True)\
        .limit(1)\
        .single()\
        .execute()
    
    last_sync_date = datetime.fromisoformat(last_order.data['filled_at'])
    
    # Fazer fetch e parar quando encontrar algo conhecido
    cursor = None
    new_orders = []
    
    while True:
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={"limit": 50, "cursor": cursor},
            auth=auth
        )
        
        data = response.json()
        found_existing = False
        
        for historical_order in data['items']:
            fill_date = datetime.fromisoformat(
                historical_order['fill']['filledAt'].replace('Z', '+00:00')
            )
            
            if fill_date <= last_sync_date:
                # ✅ Encontramos uma ordem que já temos
                found_existing = True
                break
            
            # Nova ordem
            new_orders.append(historical_order)
        
        if found_existing or not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
        time.sleep(10)
    
    # Guardar novas ordens
    for historical_order in new_orders:
        db.insert('order_history', {
            't212_order_id': historical_order['order']['id'],
            'filled_at': historical_order['fill']['filledAt'],
            # ... outros campos
        })
    
    return len(new_orders)
```

**Vantagem:** Fetch apenas últimas N ordens (até encontrar última conhecida).

---

## 📝 Comparação com /history/transactions

O endpoint de transações TEM filtro de data:

```bash
# Transações desde ontem
GET /equity/history/transactions?time=2026-09-16T00:00:00Z

# Transações nos últimos 30 dias
GET /equity/history/transactions?time=2026-08-17T00:00:00Z
```

**Porquê a diferença?**
- `/history/transactions`: Usado para relatórios fiscais (precisa filtro de data)
- `/history/orders`: API de desenvolvimento (simples, sem filtros complexos)

---

## 🔄 Fluxo Recomendado para Grid Trading

### **Setup Inicial (Uma única vez):**

```python
# 1. Sync histórico completo
sync_all_order_history()  # Pode levar tempo...

# 2. Guardar timestamp último sync
db.update('sync_log', {
    'last_sync_time': now(),
    'orders_synced': count
})
```

### **Operação Diária:**

```python
# APScheduler a cada 5 minutos
@scheduler.scheduled_job('interval', minutes=5)
async def sync_recent_orders():
    """Fetch apenas NOVAS ordens desde último sync"""
    
    # Incremental sync (rápido)
    new_count = incremental_sync_orders()
    
    # Query na BD (MUITO mais rápido que T212)
    today_orders = db.client.table('order_history')\
        .select('*')\
        .gte('filled_at', today_start.isoformat())\
        .execute()
    
    # Executar Grid Trading logic
    await process_grid_trading(today_orders.data)
```

---

## 💡 Impacto no Design

### **SEM filtro de data:**

| Aspecto | Impacto |
|--------|--------|
| **Primeiro sync** | Lento (precisa paginar tudo) |
| **Updates diários** | Rápido (só novas ordens) |
| **Queries por data** | BD local (rápido) |
| **Rate limits** | Respeitados com incremental sync |

---

## ⚠️ Armadilha: Assumir que existe

```python
# ❌ ERRADO - Assumir que time funciona
def bad_fetch_orders():
    date_from = datetime.now() - timedelta(days=7)
    
    response = requests.get(
        "https://demo.trading212.com/api/v0/equity/history/orders",
        params={
            "time": date_from.isoformat()  # ❌ ERRO 400!
        },
        auth=auth
    )
    # → Response: 400 Bad filtering arguments

# ✅ CORRETO - Usar /history/transactions para datas
def good_fetch_transactions():
    date_from = datetime.now() - timedelta(days=7)
    
    response = requests.get(
        "https://demo.trading212.com/api/v0/equity/history/transactions",
        params={
            "time": date_from.isoformat()  # ✅ FUNCIONA!
        },
        auth=auth
    )
```

---

## 🎯 Resumo

| Pergunta | Resposta |
|----------|----------|
| **Filtro de data em /history/orders?** | ❌ **Não** |
| **Como filtrar por data então?** | ✅ **Na aplicação** ou **BD local** |
| **Rate limits permitem fetch completo?** | ⚠️ **Sim, mas lento** (6 req/min) |
| **Qual é a estratégia ótima?** | ✅ **Incremental sync** (novas ordens apenas) |
| **Guardar em BD local?** | ✅ **Muito recomendado** |
| **Usar /history/transactions para datas?** | ✅ **Sim, se precisares de data-time** |

---

## 📌 Implementação Recomendada para ti

```python
# backend/db/sync.py

class OrderHistorySync:
    def __init__(self, t212_client, db):
        self.t212 = t212_client
        self.db = db
    
    async def sync_all(self):
        """Primeira vez - sync completo"""
        cursor = None
        count = 0
        
        while True:
            orders = self.t212.get_order_history(limit=50, cursor=cursor)
            
            for hist_order in orders['items']:
                await self._save_order(hist_order)
                count += 1
            
            if not orders.get('nextPagePath'):
                break
            
            cursor = extract_cursor(orders['nextPagePath'])
            await asyncio.sleep(10)  # Rate limit
        
        return count
    
    async def sync_incremental(self):
        """Sync apenas novas ordens"""
        last_order = await self._get_last_sync_order()
        last_date = last_order['filled_at'] if last_order else None
        
        cursor = None
        count = 0
        
        while True:
            orders = self.t212.get_order_history(limit=50, cursor=cursor)
            
            for hist_order in orders['items']:
                fill_date = hist_order['fill']['filledAt']
                
                if last_date and fill_date <= last_date:
                    # ✅ Encontramos última conhecida
                    return count
                
                await self._save_order(hist_order)
                count += 1
            
            if not orders.get('nextPagePath'):
                break
            
            cursor = extract_cursor(orders['nextPagePath'])
            await asyncio.sleep(10)
        
        return count
    
    async def query_since(self, date_from: datetime):
        """Query rápida na BD local"""
        result = self.db.client.table('order_history')\
            .select('*')\
            .gte('filled_at', date_from.isoformat())\
            .order('filled_at', desc=True)\
            .execute()
        
        return result.data
```

---

**Status:** ✅ Documentado  
**Data:** 2026-09-17  
**Conclusão:** Guardar em BD local é ESSENCIAL para não ficar preso a rate limits da T212!
