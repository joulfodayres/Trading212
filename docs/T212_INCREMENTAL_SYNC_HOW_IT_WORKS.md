# 🔄 Incremental Sync — Como Funciona?

**Data:** 2026-09-17  
**Pergunta:** Como é que consegues pesquisar apenas as ordens "incrementais" (novas) a partir da API do T212 se não há filtro de data?

---

## 💡 A Resposta (Simples mas Engenhosa)

**Não há filtro de data, MAS...**

A API retorna ordenada por **data DESC** (mais recentes primeiro). Então:

```
GET /history/orders?limit=50

Retorna:
1. Ordem de agora (2026-09-17 15:00)  ← NOVA
2. Ordem de agora (2026-09-17 14:50)  ← NOVA
3. Ordem de ontem (2026-09-16 16:00)  ← NOVA
4. Ordem de ontem (2026-09-16 09:00)  ← NOVA
5. Ordem de 2 dias atrás (2026-09-15 10:00)  ← JÁ TEMOS NA BD
6. ...

PARAR AQUI! ✅ Encontramos a última ordem conhecida
```

---

## 🎯 Algoritmo de Incremental Sync

### **Conceito:**

```python
last_known_order_id = 987654315  # Guardado em BD

response = api.get_order_history(limit=50)

new_orders = []

for order in response['items']:  # Iteradas por ordem DESC
    order_id = order['order']['id']
    
    if order_id == last_known_order_id:
        # ✅ Encontramos a última que temos
        BREAK  # Parar paginação!
    else:
        # Nova ordem
        new_orders.append(order)
```

**Resultado:** Fizemos 1 request (ou poucas) em vez de 100+

---

## 📋 Implementação Passo-a-Passo

### **Passo 1: Primeira vez (Full Sync)**

```python
async def full_sync_order_history():
    """
    PRIMEIRA VEZ APENAS
    Fetch histórico COMPLETO desde o início dos tempos
    """
    
    cursor = None
    total_synced = 0
    
    print("🔄 Iniciando full sync (pode levar tempo)...")
    
    while True:
        # Fetch página
        response = t212_client.get_order_history(
            limit=50,
            cursor=cursor
        )
        
        # Salvar cada ordem em BD
        for historical_order in response['items']:
            order_id = historical_order['order']['id']
            
            # Inserir em BD (com UNIQUE constraint para evitar duplicatas)
            try:
                db.client.table('order_history').insert({
                    't212_order_id': order_id,
                    'ticker': historical_order['order']['ticker'],
                    'quantity': historical_order['fill']['quantity'],
                    'price': historical_order['fill']['price'],
                    'filled_at': historical_order['fill']['filledAt'],
                    'pnl': historical_order['fill']['walletImpact']['realisedProfitLoss']
                }).execute()
                
                total_synced += 1
            except Exception as e:
                # Já existe na BD
                pass
        
        print(f"  ✓ Página com {len(response['items'])} ordens (total: {total_synced})")
        
        # Verificar próxima página
        if not response.get('nextPagePath'):
            print(f"✅ Full sync completo! {total_synced} ordens guardadas.")
            break
        
        cursor = extract_cursor(response['nextPagePath'])
        
        # Respeitar rate limit
        await asyncio.sleep(10)  # 6 req/min
    
    return total_synced
```

---

### **Passo 2: Guardar o "checkpoint" (last_order_id)**

```python
async def save_sync_checkpoint():
    """Guardar qual foi a última ordem sincronizada"""
    
    # Obter última ordem da BD (mais recente)
    last_order = db.client.table('order_history')\
        .select('t212_order_id, filled_at')\
        .order('filled_at', desc=True)\
        .limit(1)\
        .single()\
        .execute()
    
    if last_order.data:
        checkpoint = {
            'last_order_id': last_order.data['t212_order_id'],
            'last_order_date': last_order.data['filled_at'],
            'sync_time': now()
        }
        
        # Guardar checkpoint
        db.client.table('sync_log').update(checkpoint)\
            .eq('id', 1)\
            .execute()
        
        print(f"✅ Checkpoint: order_id={checkpoint['last_order_id']}")
        
        return checkpoint
    
    return None
```

---

### **Passo 3: Incremental Sync (Diariamente)**

```python
async def incremental_sync_order_history():
    """
    ⭐ INCREMENTAL SYNC - Fetch apenas NOVAS ordens
    
    Algoritmo:
    1. Fetch primeira página (mais recentes)
    2. Comparar cada ordem com último checkpoint
    3. Parar quando encontrar ordem conhecida
    """
    
    # Obter checkpoint (última ordem que temos)
    checkpoint = db.client.table('sync_log')\
        .select('last_order_id')\
        .single()\
        .execute().data
    
    last_known_id = checkpoint['last_order_id']
    
    print(f"🔄 Incremental sync. Last known order: {last_known_id}")
    
    # Fetch primeira página
    response = t212_client.get_order_history(
        limit=50  # Máximo por página
        # Sem cursor = começa do início (mais recentes)
    )
    
    new_orders = []
    found_last_known = False
    
    # Iterar APENAS a primeira página
    for historical_order in response['items']:
        order_id = historical_order['order']['id']
        
        if order_id == last_known_id:
            # ✅ Encontramos a última que temos!
            print(f"  ✓ Encontrada última ordem conhecida: {order_id}")
            found_last_known = True
            break  # ⭐ PARAR AQUI!
        
        # Nova ordem
        new_orders.append(historical_order)
        print(f"  ✓ Nova ordem: {order_id}")
    
    # Salvar novas ordens em BD
    for historical_order in new_orders:
        db.client.table('order_history').insert({
            't212_order_id': historical_order['order']['id'],
            'ticker': historical_order['order']['ticker'],
            'quantity': historical_order['fill']['quantity'],
            'price': historical_order['fill']['price'],
            'filled_at': historical_order['fill']['filledAt'],
            'pnl': historical_order['fill']['walletImpact']['realisedProfitLoss']
        }).execute()
    
    # Atualizar checkpoint
    if new_orders:
        await save_sync_checkpoint()
        print(f"✅ Incremental sync: {len(new_orders)} novas ordens")
    else:
        print(f"✅ Incremental sync: Nenhuma ordem nova")
    
    if not found_last_known and response.get('nextPagePath'):
        # ⚠️ Arriscar: última conhecida pode ter sumido (improvável)
        print("⚠️ Aviso: Última ordem conhecida não foi encontrada!")
        print("   Isso significa que há MUITAS ordens novas (>50)")
    
    return len(new_orders)
```

---

### **Passo 4: Usar no APScheduler**

```python
# backend/engine/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=0, minute=0)
async def daily_sync():
    """Sync incremental todos os dias às 00:00"""
    try:
        new_count = await incremental_sync_order_history()
        logger.info(f"✅ Daily sync: {new_count} ordens novas")
    except Exception as e:
        logger.error(f"❌ Daily sync failed: {e}")

@scheduler.scheduled_job('interval', minutes=5)
async def grid_trading_loop():
    """Grid Trading a cada 5 minutos"""
    try:
        # Query BD (RÁPIDO - sem chamar T212)
        today_orders = db.client.table('order_history')\
            .select('*')\
            .gte('filled_at', today_start.isoformat())\
            .execute()
        
        # Executar lógica de Grid Trading
        await process_grid_trading(today_orders.data)
    
    except Exception as e:
        logger.error(f"❌ Grid trading failed: {e}")

scheduler.start()
```

---

## 🎯 Visualmente

```
PRIMEIRA VEZ:
┌─────────────────────────────────────────┐
│ T212 API                                │
│ ┌───────────────────────────────────┐  │
│ │ Ordem 100 (agora)                 │  │
│ │ Ordem 99                          │  │
│ │ Ordem 98                          │  │
│ │ ...                               │  │
│ │ Ordem 1 (há 2 anos)               │  │
│ └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ Full Sync (paginação)
         ↓
    ┌─────────────┐
    │ BD Local    │
    │ Ordem 1-100 │ ✅ Guardadas
    └─────────────┘
    
    Checkpoint: last_order_id = 100


PRÓXIMA VEZ (Alguns dias depois):
┌─────────────────────────────────────────┐
│ T212 API                                │
│ ┌───────────────────────────────────┐  │
│ │ Ordem 110 (nova, agora)           │  │ ← Fetch
│ │ Ordem 109 (nova)                  │  │ ← Fetch
│ │ Ordem 108 (nova)                  │  │ ← Fetch
│ │ Ordem 107 (nova)                  │  │ ← Fetch
│ │ Ordem 106 (nova)                  │  │ ← Fetch
│ │ Ordem 105 (nova)                  │  │ ← Fetch
│ │ Ordem 104 (nova)                  │  │ ← Fetch
│ │ Ordem 103 (nova)                  │  │ ← Fetch
│ │ Ordem 102 (nova)                  │  │ ← Fetch
│ │ Ordem 101 (nova)                  │  │ ← Fetch
│ │ Ordem 100 ← ENCONTRADO!           │  │ ← PARAR!
│ │ Ordem 99  (já temos)              │  │ (não fetch)
│ │ ...                               │  │
│ └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ Incremental Sync (1 request!)
         ↓
    ┌─────────────┐
    │ BD Local    │
    │ Ordem 1-110 │ ✅ Guardadas
    └─────────────┘
    
    Checkpoint: last_order_id = 110
```

---

## ⚠️ Casos Edge (Cuidado!)

### **Case 1: Muitas ordens novas (>50)**

```python
# Se fizeste 50 ordens em 5 minutos
# Primeira página tem 50, mas não encontras última conhecida

if not found_last_known and response.get('nextPagePath'):
    # ⚠️ Há MAIS ordens novas que limite de página
    # Continuar paginação
    cursor = extract_cursor(response['nextPagePath'])
    
    while True:
        response = t212_client.get_order_history(
            limit=50,
            cursor=cursor
        )
        
        for order in response['items']:
            if order['order']['id'] == last_known_id:
                found_it = True
                break
            # ... salvar ordem
        
        if found_it or not response.get('nextPagePath'):
            break
        
        cursor = extract_cursor(response['nextPagePath'])
        await asyncio.sleep(10)
```

---

### **Case 2: Última ordem foi deletada/cancelada**

```python
# Improvável, mas possível:
# GET /history/orders não mostra mais a ordem

# Solução: Usar ticker + date range (manual)
def handle_missing_last_order():
    # Fallback: usar ticker + limite de data
    # Exemplo: "fetch últimos 7 dias de AAPL"
    
    week_ago = datetime.now() - timedelta(days=7)
    
    response = t212_client.get_order_history(
        ticker='AAPL_US_EQ',
        limit=50
    )
    
    # Filtrar manualmente por data (aplicação)
    for order in response['items']:
        order_date = datetime.fromisoformat(
            order['fill']['filledAt'].replace('Z', '+00:00')
        )
        
        if order_date < week_ago:
            break  # Parar
```

---

## 🎯 Trade-offs

| Estratégia | Requisições | Velocidade | Complexidade |
|-----------|------------|-----------|-------------|
| Full sync sempre | 100+ | 🐢 Muito lento | ⭐ Simples |
| Incremental (bem) | 1-5 | ⚡ Muito rápido | ⭐⭐⭐ Complexa |
| Incremental (com fallback) | 1-20 | ⚡ Rápido | ⭐⭐⭐⭐ Mais complexa |

---

## 📌 Resumo do Algoritmo

```
SETUP:
1. Full sync (primeira vez, uma única vez)
2. Guardar: last_order_id = 100

DAILY:
1. GET /history/orders?limit=50  (primeira página)
2. Para cada ordem:
   - Se order_id == last_known_id → BREAK ✅
   - Senão → Guardar como nova
3. UPDATE last_order_id com primeira ordem

RESULTADO:
- Primeira sincronização: ~100 requisições (6 req/min = ~16 minutos)
- Sincronizações seguintes: ~1 requisição! (rápido!)
```

---

## ✅ Implementação Final

```python
class OrderHistoryManager:
    def __init__(self, t212_client, db):
        self.t212 = t212_client
        self.db = db
    
    async def initialize(self):
        """Chamada UMA VEZ na primeira execução"""
        result = await self.full_sync_order_history()
        print(f"✅ Sistema iniciado com {result} ordens históricas")
    
    async def daily_update(self):
        """Chamada TODOS os dias via APScheduler"""
        new_count = await self.incremental_sync_order_history()
        print(f"✅ {new_count} ordens novas sincronizadas")
    
    async def get_orders_since(self, date_from: datetime):
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
**Conclusão:** Incremental sync = elegante + eficiente!
