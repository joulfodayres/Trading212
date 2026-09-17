# 📚 GET /api/v0/equity/history/orders — Parâmetros Completos

**Data:** 2026-09-17  
**Baseado em:** api.yaml OpenAPI 3.0.1  
**Rate Limit:** 6 req / 1 minuto (0.1 req/s - MUITO LENTO)

---

## 📋 Parâmetros Query

### **1. `limit` (Opcional)**

```
Tipo: integer (32-bit)
Valor Padrão: 20
Valor Máximo: 50
Valor Mínimo: 1
```

**O que é:** Número máximo de itens a retornar numa única requisição.

**Exemplos:**

```bash
# Retorna últimos 20 trades (default)
GET /api/v0/equity/history/orders

# Retorna últimos 10 trades
GET /api/v0/equity/history/orders?limit=10

# Retorna últimos 50 trades (máximo)
GET /api/v0/equity/history/orders?limit=50

# ❌ ERRO - Limite máximo excedido
GET /api/v0/equity/history/orders?limit=100  # Retorna erro 400
```

**Uso Prático:**

```python
# Quero buscar todos os trades de hoje
# Fazendo fetch por página de 50

limit = 50  # Máximo permitido
cursor = None

all_trades = []

while True:
    # Fetch page
    response = requests.get(
        "https://demo.trading212.com/api/v0/equity/history/orders",
        params={
            "limit": limit,
            "cursor": cursor
        },
        auth=(api_key, api_secret)
    )
    
    data = response.json()
    all_trades.extend(data['items'])
    
    # Check if more pages
    if not data['nextPagePath']:
        break
    
    # Extract cursor for next page
    cursor = extract_cursor(data['nextPagePath'])
```

---

### **2. `cursor` (Opcional)**

```
Tipo: integer (64-bit)
Valor Padrão: None (começa do início)
Descrição: Pointer para um item específico no dataset
```

**O que é:** Um identificador opaco (timestamp ou ID) que marca onde está na lista. Usado para paginação.

**⚠️ IMPORTANTE:** 
- **NUNCA construir manualmente!**
- **SEMPRE usar o valor exato de `nextPagePath` retornado**
- O cursor retornado vem como parte do `nextPagePath`

**Exemplos:**

```bash
# Primeira página (SEM cursor)
GET /api/v0/equity/history/orders?limit=20

# Resposta:
{
  "items": [ ... 20 items ... ],
  "nextPagePath": "/api/v0/equity/history/orders?limit=20&cursor=1760346100000"
}

# Segunda página (COM cursor)
GET /api/v0/equity/history/orders?limit=20&cursor=1760346100000

# Resposta:
{
  "items": [ ... 20 mais items ... ],
  "nextPagePath": "/api/v0/equity/history/orders?limit=20&cursor=1660015723000"
}

# Terceira página
GET /api/v0/equity/history/orders?limit=20&cursor=1660015723000

# Resposta final:
{
  "items": [ ... últimos items ... ],
  "nextPagePath": null  # Sem próxima página
}
```

**⚠️ Armadilha Comum:**

```python
# ❌ ERRADO - Tentar construir cursor manualmente
cursor = int(time.time())  # Não funciona!
response = requests.get(url, params={"cursor": cursor})

# ✅ CORRETO - Usar exatamente o que a API retornou
prev_response = requests.get(url)
next_page_path = prev_response.json()['nextPagePath']
next_cursor = extract_cursor(next_page_path)
next_response = requests.get(url, params={"cursor": next_cursor})
```

**Implementação Correta:**

```python
def extract_cursor(next_page_path: str) -> int:
    """Extrair cursor de nextPagePath"""
    # nextPagePath formato:
    # "/api/v0/equity/history/orders?limit=20&cursor=1760346100000"
    
    from urllib.parse import urlparse, parse_qs
    
    parsed = urlparse(next_page_path)
    params = parse_qs(parsed.query)
    
    cursor_str = params.get('cursor', [None])[0]
    return int(cursor_str) if cursor_str else None

# Uso:
response = requests.get(url)
next_path = response.json()['nextPagePath']

if next_path:
    cursor = extract_cursor(next_path)
    next_response = requests.get(url, params={"cursor": cursor})
```

---

### **3. `ticker` (Opcional)**

```
Tipo: string
Valor Padrão: None (sem filtro)
Descrição: Filtrar histórico por ticker específico
```

**O que é:** Limita os resultados apenas às ordens de um instrumento específico.

**Formato:** Ticker como retornado pela API (ex: `AAPL_US_EQ`)

**Exemplos:**

```bash
# Histórico de TUDO
GET /api/v0/equity/history/orders?limit=50

# Histórico apenas de Apple
GET /api/v0/equity/history/orders?limit=50&ticker=AAPL_US_EQ

# Histórico apenas de Microsoft
GET /api/v0/equity/history/orders?limit=50&ticker=MSFT_US_EQ

# Múltiplos tickers (NÃO SUPORTADO em uma requisição)
# ❌ Não funciona:
GET /api/v0/equity/history/orders?ticker=AAPL_US_EQ&ticker=MSFT_US_EQ

# Solução: Fazer duas requisições
GET /api/v0/equity/history/orders?ticker=AAPL_US_EQ
GET /api/v0/equity/history/orders?ticker=MSFT_US_EQ
```

**Casos de Uso:**

```python
# 1. Encontrar ordem específica por ID
def find_order_in_history(order_id: int, ticker: str):
    """Procurar ordem específica no histórico"""
    cursor = None
    max_pages = 5  # Limitar procura
    
    for page in range(max_pages):
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={
                "limit": 50,
                "ticker": ticker,  # ✅ Filtrar por ticker
                "cursor": cursor
            },
            auth=(api_key, api_secret)
        )
        
        data = response.json()
        
        for historical_order in data['items']:
            if historical_order['order']['id'] == order_id:
                return historical_order  # ✅ Encontrada!
        
        if not data['nextPagePath']:
            break
        
        cursor = extract_cursor(data['nextPagePath'])
    
    return None  # Não encontrada

# 2. Todas as ordens de um ETF específico (Grid Trading)
def get_etf_trade_history(ticker: str):
    """Obter histórico completo de um ETF"""
    all_trades = []
    cursor = None
    
    while True:
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={
                "limit": 50,
                "ticker": ticker
            },
            auth=(api_key, api_secret)
        )
        
        data = response.json()
        all_trades.extend(data['items'])
        
        if not data['nextPagePath']:
            break
        
        cursor = extract_cursor(data['nextPagePath'])

    return all_trades

# 3. Análise de desempenho por ticker
def analyze_ticker_performance(ticker: str):
    """Calcular P&L total por ticker"""
    trades = get_etf_trade_history(ticker)
    
    total_pnl = 0
    total_trades = len(trades)
    
    for historical_order in trades:
        fill = historical_order['fill']
        pnl = fill['walletImpact']['realisedProfitLoss']
        total_pnl += pnl
    
    avg_pnl_per_trade = total_pnl / total_trades if total_trades > 0 else 0
    
    return {
        'ticker': ticker,
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'avg_pnl_per_trade': avg_pnl_per_trade
    }
```

---

## 📤 Estrutura de Resposta

```json
{
  "items": [
    {
      "order": {
        "id": 987654321,
        "ticker": "AAPL_US_EQ",
        "instrument": {
          "ticker": "AAPL_US_EQ",
          "isin": "US0378331005",
          "name": "Apple Inc.",
          "currency": "USD"
        },
        "side": "BUY",
        "quantity": 10.5,
        "type": "MARKET",
        "status": "FILLED",
        "createdAt": "2026-09-17T14:30:00Z",
        "filledQuantity": 10.5,
        "currency": "USD",
        "timeInForce": "DAY",
        "strategy": "QUANTITY",
        "initiatedFrom": "API",
        "extendedHours": false
      },
      "fill": {
        "id": 123456,
        "filledAt": "2026-09-17T14:31:00Z",
        "price": 226.50,
        "quantity": 10.5,
        "type": "TRADE",
        "tradingMethod": "TOTV",
        "walletImpact": {
          "currency": "USD",
          "netValue": 2378.25,
          "realisedProfitLoss": 0,
          "fxRate": 1.0,
          "taxes": []
        }
      }
    },
    {
      "order": {
        "id": 987654320,
        "ticker": "MSFT_US_EQ",
        "side": "SELL",
        "quantity": -5.0,
        ...
      },
      "fill": {
        "filledAt": "2026-09-17T15:45:00Z",
        "price": 425.30,
        "quantity": -5.0,
        "type": "TRADE",
        "walletImpact": {
          "netValue": 2126.50,
          "realisedProfitLoss": 125.50,  # ✅ P&L REALIZADO
          ...
        }
      }
    }
  ],
  "nextPagePath": "/api/v0/equity/history/orders?limit=20&cursor=1660015723000"
}
```

---

## 🔑 Campos Importantes da Resposta

### **Order Object (metadata)**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int64 | Order ID único da T212 |
| `ticker` | string | Ticker (ex: AAPL_US_EQ) |
| `side` | enum | BUY ou SELL |
| `quantity` | number | Quantidade (negativo = SELL) |
| `type` | enum | MARKET, LIMIT, STOP, STOP_LIMIT |
| `status` | enum | FILLED, CANCELLED, REJECTED, etc |
| `createdAt` | datetime | Quando a ordem foi colocada |
| `filledQuantity` | number | Quanto foi preenchido |
| `initiatedFrom` | enum | API, WEB, ANDROID, IOS, SYSTEM |

### **Fill Object (execução)**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `price` | number | **Preço de execução** ✅ |
| `quantity` | number | Quantidade executada |
| `filledAt` | datetime | **Quando executou** ✅ |
| `type` | enum | TRADE, STOCK_SPLIT, DIVIDEND, etc |
| `tradingMethod` | enum | TOTV ou OTC |

### **WalletImpact (financeiro)**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `netValue` | number | Valor líquido da transação |
| `realisedProfitLoss` | number | **P&L realizado** ✅ |
| `currency` | string | Moeda (ex: USD) |
| `fxRate` | number | Taxa de câmbio aplicada |
| `taxes` | array | Impostos aplicados |

---

## 💡 Exemplos Práticos

### **Exemplo 1: Fetch página por página**

```python
def get_all_trades(limit=50):
    """Fetch TODAS as ordens (cuidado: rate limit!)"""
    all_trades = []
    cursor = None
    
    while True:
        # Rate limit: 6 req/min = 10 segundos entre requisições
        time.sleep(10)  # ⚠️ IMPORTANTE!
        
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params=params,
            auth=(api_key, api_secret)
        )
        
        data = response.json()
        all_trades.extend(data['items'])
        
        print(f"Fetched {len(data['items'])} trades, total: {len(all_trades)}")
        
        if not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
    
    return all_trades
```

### **Exemplo 2: Encontrar ordem específica**

```python
def find_order_execution_details(order_id: int, ticker: str):
    """Encontrar detalhes de execução de uma ordem"""
    
    params = {
        "limit": 50,
        "ticker": ticker
    }
    
    cursor = None
    pages_checked = 0
    
    while pages_checked < 5:  # Limitar a 5 páginas
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={**params, "cursor": cursor} if cursor else params,
            auth=(api_key, api_secret)
        )
        
        data = response.json()
        
        for historical_order in data['items']:
            if historical_order['order']['id'] == order_id:
                # ✅ Encontrada!
                fill = historical_order['fill']
                return {
                    'order_id': order_id,
                    'ticker': ticker,
                    'executed_price': fill['price'],
                    'executed_quantity': fill['quantity'],
                    'executed_at': fill['filledAt'],
                    'realized_pnl': fill['walletImpact']['realisedProfitLoss'],
                    'net_value': fill['walletImpact']['netValue']
                }
        
        if not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
        pages_checked += 1
        time.sleep(10)  # Rate limit
    
    return None  # Não encontrada
```

### **Exemplo 3: Análise de P&L**

```python
def calculate_pnl_by_ticker():
    """Calcular P&L total por ticker"""
    
    results = {}
    
    # Fetch histórico
    params = {"limit": 50}
    cursor = None
    
    while True:
        response = requests.get(
            "https://demo.trading212.com/api/v0/equity/history/orders",
            params={**params, "cursor": cursor} if cursor else params,
            auth=(api_key, api_secret)
        )
        
        data = response.json()
        
        for historical_order in data['items']:
            ticker = historical_order['order']['ticker']
            pnl = historical_order['fill']['walletImpact']['realisedProfitLoss']
            
            if ticker not in results:
                results[ticker] = {'trades': 0, 'pnl': 0}
            
            results[ticker]['trades'] += 1
            results[ticker]['pnl'] += pnl
        
        if not data.get('nextPagePath'):
            break
        
        cursor = extract_cursor(data['nextPagePath'])
        time.sleep(10)
    
    # Formatado
    for ticker, data in sorted(results.items()):
        print(f"{ticker}: {data['trades']} trades, P&L = €{data['pnl']:.2f}")
    
    return results
```

---

## ⚠️ Armadilhas Comuns

### **1. Não respeitar rate limit**

```python
# ❌ ERRADO - Faz 6 requests em sequência
for i in range(6):
    response = requests.get(url)

# ✅ CORRETO - Aguarda entre requisições
for i in range(6):
    response = requests.get(url)
    time.sleep(10)  # 6 req/min = 10 seg intervalo
```

### **2. Construir cursor manualmente**

```python
# ❌ ERRADO
next_cursor = int(time.time()) - 3600  # Tentar construir
response = requests.get(url, params={"cursor": next_cursor})

# ✅ CORRETO
# Usar exatamente o que a API retornou
next_cursor = extract_cursor(prev_response['nextPagePath'])
```

### **3. Esquecer que ticker filtra resultados**

```python
# ❌ ERRADO - Espera todas as ordens
response = requests.get(url, params={"ticker": "AAPL_US_EQ"})
# Apenas retorna ordens de AAPL!

# ✅ CORRETO - Saber que ticker limita resultados
# Se quero TODAS: não usar ticker
# Se quero AAPL apenas: usar ticker=AAPL_US_EQ
```

### **4. nextPagePath é CAMINHO COMPLETO**

```python
# ❌ ERRADO - Tentar extrair só o cursor
url = "https://api.com/orders?limit=20&cursor=123"
cursor = "123"  # ✓ Correto extrair
params = {"cursor": cursor}  # MAS...

# ✅ CORRETO - nextPagePath é path relativo
next_page_path = "/api/v0/equity/history/orders?limit=20&cursor=123"
# Usar o full path ou extrair params

# Opção 1: Usar full path se a base URL for igual
requests.get(
    "https://demo.trading212.com" + next_page_path,
    auth=auth
)

# Opção 2: Extrair cursor e construir
cursor = extract_cursor(next_page_path)
requests.get(
    "https://demo.trading212.com/api/v0/equity/history/orders",
    params={"limit": 50, "cursor": cursor},
    auth=auth
)
```

---

## 📊 Combinações de Parâmetros

| Caso de Uso | Parâmetros | Resultado |
|-------------|-----------|-----------|
| Últimos 20 trades | `limit=20` | Os 20 mais recentes |
| Últimos 50 trades | `limit=50` | Os 50 mais recentes (máximo) |
| Página 2 de trades | `limit=50&cursor=123456` | Próximos 50 após cursor |
| Trades de AAPL | `ticker=AAPL_US_EQ` | Todas as ordens de AAPL |
| Últimos 20 de AAPL | `limit=20&ticker=AAPL_US_EQ` | Últimos 20 trades de AAPL |
| Todas as ordens | Sem parâmetros | Começa do início (com paginação) |

---

## 🎯 Resumo dos Parâmetros

| Parâmetro | Tipo | Obrigatório | Default | Máximo | Descrição |
|-----------|------|------------|---------|--------|-----------|
| `limit` | int | Não | 20 | 50 | Número de items por página |
| `cursor` | int64 | Não | None | - | Pointer para paginação |
| `ticker` | string | Não | None | - | Filtrar por instrumento |

**Rate Limit:** 6 req / 1 minuto (esperar ~10 segundos entre requisições)

**Retorna:** Array paginado de HistoricalOrder + nextPagePath

---

**Status:** ✅ Documentado  
**Data:** 2026-09-17
