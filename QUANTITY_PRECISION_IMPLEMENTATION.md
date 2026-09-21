# AutomationEngine - Adaptive Quantity Precision Implementation

## Mudanças Implementadas

### 1. Database Schema
**Ficheiro:** `db/migration_add_quantity_precision.sql`
- Adiciona coluna `quantity_precision INTEGER DEFAULT 3` à tabela `isins`
- Esta coluna armazena o número de casas decimais que T212 aceita para cada ISIN
- Backfill de todos os ISINs existentes com default 3

### 2. ORM Model
**Ficheiro:** `backend/models/db.py`
- Classe `ISIN`: Adiciona campo `quantity_precision = Column(Integer, default=3)`
- Documentação: "Decimal places T212 accepts for this ISIN"

### 3. AutomationEngine - Phase 1
**Ficheiro:** `backend/services/automation_engine.py` - `_phase_1_setup_isin()`

**Alterações:**
- Carrega `quantity_precision` do ISIN ao iniciar
- Arredonda `buy_quantity` e `sell_quantity` ao valor de `quantity_precision`
- Arredonda `buy_price` e `sell_price` a 3 decimals
- Chama novo método `_place_order_with_precision_retry()` em vez de direto

**Fluxo:**
```
1. Load ISIN (com quantity_precision=3 por default)
2. Calcula buy_quantity, sell_quantity
3. Round quantity a quantity_precision decimals
4. Chama _place_order_with_precision_retry (BUY)
5. Chama _place_order_with_precision_retry (SELL)
6. Se sucesso, salva ordens
```

### 4. AutomationEngine - Phase 3
**Ficheiro:** `backend/services/automation_engine.py` - `_phase_3_place_new_pair()`

**Alterações:**
- Mesma lógica que Phase 1
- Carrega `quantity_precision` do ISIN
- Arredonda quantidades e preços
- Chama `_place_order_with_precision_retry()` para BUY e SELL

### 5. Novo Método: `_place_order_with_precision_retry()`
**Ficheiro:** `backend/services/automation_engine.py`

**Funcionalidade:**
```
1. Tenta colocar ordem (BUY ou SELL)
2. Se sucesso → retorna response
3. Se erro "invalid quantity precision X":
   a. Extrai X do erro (ex: "invalid quantity precision 2" → 2)
   b. Updates ISIN.quantity_precision = X em BD
   c. Arredonda quantity a X decimals
   d. RETENTA a ordem com novo valor
   e. Se sucesso 2ª vez → retorna response
   f. Se falha 2ª vez → retorna None
4. Se outro erro → retorna None
```

**Vantagens:**
- Automático: Detecta e adapta-se à precision correta
- Resiliente: Tenta uma vez, se falhar por precision, retenta
- Persistente: Guarda em BD o valor correto para futuras tentativas
- Logging: Detalha cada passo

## Fluxo Completo do Erro de Precision

### Cenário 1: Precision Correta (default)
```
Phase 1 → Carrega quantity_precision=3
         → Arredonda quantity a 3 decimals
         → Chama place_buy_limit_order()
         → Sucesso! (HTTP 200)
         → Salva ordem
```

### Cenário 2: Precision Incorreta (descoberta em tempo de execução)
```
Phase 1 → Carrega quantity_precision=3 (default)
         → Arredonda quantity a 3 decimals (ex: 0.578)
         → Chama place_buy_limit_order()
         → T212 API retorna: 400 "invalid quantity precision 2"
         → Detecta erro de precision
         → Extrai 2 do erro
         → Updates ISIN: quantity_precision = 2
         → Arredonda quantity a 2 decimals (ex: 0.58)
         → RETENTA place_buy_limit_order()
         → Sucesso! (HTTP 200)
         → Salva ordem
         
Phase 2/3 → Carrega quantity_precision=2 (já atualizado)
          → Usa 2 decimals desde o início
          → Sem mais erros de precision
```

## Impacto

### Antes
- Fixo a 3 decimals em T212Service
- Se T212 aceitava 2: erro, falha
- Se T212 aceitava 4: ok, mas talvez impreciso

### Depois
- Adaptativo por ISIN
- Primeira tentativa com default 3
- Se falhar por precision, detecta e retenta
- Futuras tentativas usam o valor correto
- Sem intervenção manual

## Files Modified (SEM COMMIT)

1. `db/migration_add_quantity_precision.sql` - SQL migration
2. `backend/models/db.py` - ORM model (+ quantity_precision field)
3. `backend/services/automation_engine.py`:
   - `_phase_1_setup_isin()` - Loads precision, uses retry logic
   - `_phase_3_place_new_pair()` - Loads precision, uses retry logic
   - `_place_order_with_precision_retry()` - NEW method

## Próximos Passos

1. ❌ NÃO fiz commit (conforme pedido)
2. Aplicar migration SQL em BD Supabase (manualmente ou via script)
3. Testar com GUI para ver se precision adaptativa funciona
4. Fazer commit quando confirmes que está OK
