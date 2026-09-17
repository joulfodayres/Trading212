# 📊 Tabelas de Strategy Trading - Design & Decisões

**Data:** 2026-09-17  
**Ficheiro SQL:** `db/trading_strategy_tables.sql`  
**Status:** ✅ Pronto para executar em Supabase

---

## 🎯 Overview

Criámos 4 novas tabelas para gerenciar estratégias de trading, mantendo coerência com a BD existente.

**Tuas especificações originais → Implementação final:**

| Tua Tabela | Nome Final | Razão da Mudança |
|-----------|-----------|-----------------|
| `ISINS` | `isin_strategy_config` | Mais descritivo + RLS requer user_id |
| `ISINS_HISTORIC` | `isin_strategy_history` | Mais claro (history vs historic) |
| `STRATEGIES` | `strategy_definitions` | Diferencia de `strategies` existente |
| `STRATEGY_PARAMETERS` | `strategy_parameters` | Mantido (bom nome) |

---

## ⚠️ Decisões Críticas (Tu Tinhas Razão!)

### 1. **Timestamp como Chave Composta?**

**Teu Design:**
```sql
ISINS_HISTORIC:
  > id_isin: char [KEY]
  > ts_creation [KEY]    ← ⚠️ Problema!
```

**Problema Identificado:**
- Se 2 eventos ocorrem no **mesmo segundo** do mesmo ISIN → conflito
- Exemplo: UPDATE automação às 14:30:45.500 e 14:30:45.750 = mesmo timestamp

**Solução Implementada:**
```sql
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  ← Chave única
  user_id UUID NOT NULL,
  isin_id UUID NOT NULL,
  strategy_id UUID,
  automated BOOLEAN NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(user_id, isin_id, created_at)  ← Garante uma por segundo
);
```

✅ **Benefícios:**
- PKs sempre únicas (UUID)
- Queries rápidas (índice em id)
- Histórico preservado com precisão
- RLS simples (id NOT NULL)

---

### 2. **Falta de user_id (Crítica para RLS)**

**Teu Design:** Nenhuma referência a user

**Problema:**
```sql
-- ❌ SEM user_id: RLS é impossível!
CREATE POLICY "..." ON isin_strategy_config
  FOR SELECT USING (
    -- Como saber se o user tem permissão?
    -- Não há coluna user_id para comparar!
  );
```

**Solução:**
```sql
-- ✅ COM user_id: RLS funciona
CREATE POLICY "Users can view their own configs" ON isin_strategy_config
  FOR SELECT USING (user_id = auth.uid());
```

**Adicionado em TODAS as tabelas:**
- `isin_strategy_config` - Direct user_id
- `isin_strategy_history` - Direct user_id
- `strategy_definitions` - Direct user_id
- `strategy_parameters` - Via FK em strategy_definitions (nested RLS)

---

### 3. **Nomenclatura Coerente com BD Existente**

**Patterns que detectámos:**

```sql
-- Padrão 1: PKs são UUIDs
id UUID PRIMARY KEY DEFAULT gen_random_uuid()  ← SEMPRE

-- Padrão 2: Foreign keys tipificadas
user_id UUID NOT NULL REFERENCES users(id)
isin_id UUID REFERENCES isins(id)
strategy_id UUID REFERENCES strategies(id)

-- Padrão 3: Timestamps com time zone
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()

-- Padrão 4: Índices nomeados
CREATE INDEX idx_<tabela>_<coluna> ON <tabela>(<coluna>)

-- Padrão 5: Unique compostos para evitar duplicados
UNIQUE(user_id, isin_id)  ← Garante 1 config por ISIN por user
```

**Aplicámos em TODAS as 4 tabelas** ✅

---

## 📋 Tabelas Criadas - Detalhe

### 1️⃣ `isin_strategy_config` (Substituir tua "ISINS")

**Propósito:** Config ATUAL por ISIN

```sql
CREATE TABLE isin_strategy_config (
  id UUID PRIMARY KEY,                    ← Chave única
  user_id UUID NOT NULL,                  ← RLS (multi-user safe)
  isin_id UUID NOT NULL,                  ← Referência ao ISIN
  strategy_id UUID,                       ← Qual estratégia usar
  automated BOOLEAN DEFAULT FALSE,        ← Ligado/desligado
  created_at TIMESTAMP WITH TIME ZONE,    ← Quando criado
  updated_at TIMESTAMP WITH TIME ZONE,    ← Última atualização
  UNIQUE(user_id, isin_id)                ← Uma config por ISIN
);
```

**Use Case:**
```python
# Python
config = db.query(isin_strategy_config).filter_by(
    user_id=user_id,
    isin_id=isin_id
).first()

if config.automated:
    apply_strategy(config.strategy_id)
```

**Vantagens:**
- ✅ Rápido buscar config de um ISIN
- ✅ RLS garante user não vê ISINs alheios
- ✅ Updated_at permite auditoria

---

### 2️⃣ `isin_strategy_history` (Substituir tua "ISINS_HISTORIC")

**Propósito:** Histórico de mudanças

```sql
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY,                    ← Chave única
  user_id UUID NOT NULL,                  ← RLS
  isin_id UUID NOT NULL,                  ← Qual ISIN
  strategy_id UUID,                       ← Qual estratégia
  automated BOOLEAN NOT NULL,             ← Estado (true/false)
  created_at TIMESTAMP WITH TIME ZONE,    ← Momento da mudança
  updated_at TIMESTAMP WITH TIME ZONE,    ← Processado
  UNIQUE(user_id, isin_id, created_at)    ← Uma entrada por segundo
);
```

**Use Case:**
```python
# Auditoria: Quando foi ativada/desativada automação?
history = db.query(isin_strategy_history).filter_by(
    user_id=user_id,
    isin_id=isin_id,
    automated=True
).order_by(-created_at).limit(10)

for entry in history:
    print(f"Automação ativada em {entry.created_at} com {entry.strategy_id}")
```

**Vantagens:**
- ✅ Rastreia TODAS as mudanças
- ✅ Permite análise de padrões
- ✅ Compliance/auditoria
- ✅ UUID PK resolve "timestamp como chave"

---

### 3️⃣ `strategy_definitions` (Substituir tua "STRATEGIES")

**Propósito:** Definição de estratégias

```sql
CREATE TABLE strategy_definitions (
  id UUID PRIMARY KEY,                    ← Chave única
  user_id UUID NOT NULL,                  ← RLS (cada user tem suas estratégias)
  strategy_name VARCHAR NOT NULL,         ← Ex: "Grid Trading ±1%"
  strategy_desc TEXT,                     ← Descrição longa
  strategy_status VARCHAR CHECK (...),    ← 'E'=Enabled / 'D'=Disabled
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(user_id, strategy_name)          ← Um nome por user
);
```

**Use Case:**
```python
# Listar estratégias ativas do user
strategies = db.query(strategy_definitions).filter_by(
    user_id=user_id,
    strategy_status='E'  ← Habilitadas
).all()

for s in strategies:
    print(f"{s.strategy_name}: {s.strategy_desc}")
```

**Vantagens:**
- ✅ Separado de `strategies` existente (foco em definições)
- ✅ Status simples (char E/D, fácil de query)
- ✅ Descrição permite documentação
- ✅ RLS garante user vê só suas estratégias

---

### 4️⃣ `strategy_parameters` (Manter teu "STRATEGY_PARAMETERS")

**Propósito:** Parâmetros numéricos variáveis

```sql
CREATE TABLE strategy_parameters (
  id UUID PRIMARY KEY,                    ← Chave única
  strategy_id UUID NOT NULL,              ← FK para strategy_definitions
  pos INTEGER NOT NULL,                   ← Posição/versão (1, 2, 3...)
  param1..param10 DECIMAL(18, 8),         ← Até 10 parâmetros
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(strategy_id, pos)                ← Uma versão por posição
);
```

**Use Case:**
```python
# Grid Trading com ±1% (param1, param2)
params = db.query(strategy_parameters).filter_by(
    strategy_id=strategy_id,
    pos=1  ← Versão 1 ativa
).first()

buy_threshold = params.param1  # -1.0
sell_threshold = params.param2  # +1.0

# Próxima versão (AB testing):
params_v2 = db.query(strategy_parameters).filter_by(
    strategy_id=strategy_id,
    pos=2  ← Versão 2
).first()
```

**Vantagens:**
- ✅ Até 10 parâmetros (expansível)
- ✅ Múltiplas versões (AB testing, rollback)
- ✅ RLS herança via FK em strategy_definitions
- ✅ Tipos DECIMAL = precisão para finanças

---

## 🔐 Row-Level Security (RLS)

Todas as 4 tabelas têm RLS ativado. Exemplo:

```sql
-- Nível 1: Direct (user_id na tabela)
CREATE POLICY "Users can view their own configs" ON isin_strategy_config
  FOR SELECT USING (user_id = auth.uid());

-- Nível 2: Via FK (RLS herança)
CREATE POLICY "Users can view their own strategy parameters" ON strategy_parameters
  FOR SELECT USING (
    strategy_id IN (
      SELECT id FROM strategy_definitions WHERE user_id = auth.uid()
    )
  );
```

**Resultado:**
- ✅ User A não vê dados do User B
- ✅ Backend seguro sem lógica adicional
- ✅ Queries rejeitas automaticamente em Supabase

---

## 📊 Relações ER

```
users (1)
  └─┬─────────────────────────────────┐
    │                                 │
isin_strategy_config              strategy_definitions
  │ user_id ──────────────────────└── user_id
  │ isin_id ──────────────────→ isins.id
  └─ strategy_id ────────────→ strategy_definitions.id
                                  │
                            strategy_parameters
                              │ strategy_id

isin_strategy_history
  │ user_id ──────────────────────→ users.id
  │ isin_id ──────────────────→ isins.id
  └─ strategy_id ────────────→ strategy_definitions.id
```

---

## 🚀 Próximos Passos

### 1. **Executar SQL em Supabase**
```
1. Ir a: https://supabase.com/dashboard
2. Projeto Trading212
3. SQL Editor → Novo Query
4. Copiar `db/trading_strategy_tables.sql`
5. Executar
```

### 2. **Validar no Dashboard**
```
Tables:
  ✅ isin_strategy_config
  ✅ isin_strategy_history
  ✅ strategy_definitions
  ✅ strategy_parameters
```

### 3. **Criar Modelos SQLAlchemy**

Ficheiro: `backend/models/db.py`

```python
from sqlalchemy import String, Boolean, Integer, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship

class IsINStrategyConfig(Base):
    __tablename__ = "isin_strategy_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    isin_id = Column(UUID(as_uuid=True), ForeignKey("isins.id"), nullable=False)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategy_definitions.id"))
    automated = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class StrategyDefinitions(Base):
    __tablename__ = "strategy_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    strategy_name = Column(String, nullable=False)
    strategy_desc = Column(String)
    strategy_status = Column(String, default='E')  # E=Enabled, D=Disabled
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class StrategyParameters(Base):
    __tablename__ = "strategy_parameters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategy_definitions.id"), nullable=False)
    pos = Column(Integer, nullable=False)
    param1 = Column(Numeric(18, 8))
    param2 = Column(Numeric(18, 8))
    # ... param3 até param10
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

# + IsINStrategyHistory (similar)
```

### 4. **Criar Pydantic Schemas**

Ficheiro: `backend/models/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional

class StrategyParametersSchema(BaseModel):
    strategy_id: UUID
    pos: int
    param1: Optional[Decimal]
    param2: Optional[Decimal]
    # ... até param10

class StrategyDefinitionsSchema(BaseModel):
    strategy_name: str
    strategy_desc: Optional[str]
    strategy_status: str  # E ou D

class IsINStrategyConfigSchema(BaseModel):
    isin_id: UUID
    strategy_id: Optional[UUID]
    automated: bool
```

### 5. **Criar Endpoints FastAPI**

Ficheiro: `backend/routes/strategies.py`

```python
@router.get("/strategies")
async def list_strategies(current_user: User = Depends(get_current_user)):
    strategies = db.query(StrategyDefinitions).filter_by(user_id=current_user.id).all()
    return strategies

@router.post("/strategies")
async def create_strategy(strategy: StrategyDefinitionsSchema, current_user: User = Depends(get_current_user)):
    # ...
```

---

## ✅ Checklist Final

- [ ] Executar SQL em Supabase
- [ ] Verificar tabelas criadas
- [ ] Adicionar modelos SQLAlchemy
- [ ] Adicionar schemas Pydantic
- [ ] Criar endpoints FastAPI
- [ ] Testar CRUD via /docs
- [ ] Documentar em docs/

---

**Ficheiro de referência:** `db/trading_strategy_tables.sql`  
**Próximo:** Implementar backend + frontend para gerenciar estratégias

🚀 **Pronto para Phase 5 - Strategy Management!**
