# 🔄 Comparação: Design Original vs Final

**Data:** 2026-09-17  
**Objetivo:** Mostrar as mudanças e o porquê

---

## 📊 Tabela 1: ISINS → isin_strategy_config

### Teu Design Original
```
Table ISINS
  > id_isin: string [KEY]
  > automated: boolean
  > id_strategy: integer
  > ts_creation: timestamp
  > ts_update: timestamp
```

### Design Final (Implementado)
```sql
CREATE TABLE isin_strategy_config (
  id UUID PRIMARY KEY,                    ← NOVA: Chave único (UUID)
  user_id UUID NOT NULL,                  ← NOVA: RLS (multi-user)
  isin_id UUID NOT NULL,                  ← Renomeado: id_isin → isin_id (FK)
  strategy_id UUID,                       ← Renomeado: id_strategy → strategy_id (FK)
  automated BOOLEAN DEFAULT FALSE,        ← Mantido ✓
  created_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_creation → created_at
  updated_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_update → updated_at
  UNIQUE(user_id, isin_id)                ← NOVA: Garante 1 config por ISIN
);
```

### Mudanças Explicadas

| Coluna Original | Coluna Final | Razão |
|---|---|---|
| `id_isin: string [KEY]` | `id: UUID PRIMARY KEY` + `isin_id: UUID FK` | ✅ Strings são lentas. UUIDs são padrão. FK garante integridade |
| (sem user_id) | `user_id: UUID NOT NULL` | ✅ Crítico para RLS. Sem isto, impossível garantir segurança multi-user |
| `id_strategy: integer` | `strategy_id: UUID FK` | ✅ Coerência. Todas FKs são UUIDs na BD |
| `ts_creation: timestamp` | `created_at: TIMESTAMP WITH TIME ZONE` | ✅ Pattern coerente. WITH TIME ZONE crucial em cloud |
| `ts_update: timestamp` | `updated_at: TIMESTAMP WITH TIME ZONE` | ✅ Mesmo pattern |
| (sem constraint único) | `UNIQUE(user_id, isin_id)` | ✅ Evita duplicados. Um user não pode ter 2 configs do mesmo ISIN |

---

## 📊 Tabela 2: ISINS_HISTORIC → isin_strategy_history

### Teu Design Original
```
Table ISINS_HISTORIC
  > id_isin: char [KEY]
  > ts_creation [KEY]        ← ⚠️ PROBLEMA AQUI
  > automated: boolean
  > id_strategy: integer
  > ts_update: timestamp
```

### Design Final (Implementado)
```sql
CREATE TABLE isin_strategy_history (
  id UUID PRIMARY KEY,                    ← NOVA: Chave único
  user_id UUID NOT NULL,                  ← NOVA: RLS
  isin_id UUID NOT NULL,                  ← Renomeado: id_isin → isin_id FK
  strategy_id UUID,                       ← Renomeado: id_strategy → strategy_id FK
  automated BOOLEAN NOT NULL,             ← Mantido ✓
  created_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_creation
  updated_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_update
  UNIQUE(user_id, isin_id, created_at)    ← NOVA: Garante uma entrada por segundo
);
```

### ⚠️ Problema Resolvido: Timestamp como Chave

**Teu design:**
```sql
-- ❌ PROBLEMA
PRIMARY KEY (id_isin, ts_creation)
```

**Cenário problemático:**
```
14:30:45.000 → Automação ATIVADA  (id_isin=ABCD, ts_creation=14:30:45)
14:30:45.500 → Automação DESATIVADA (id_isin=ABCD, ts_creation=14:30:45)
              ↑ CONFLITO! Mesmo timestamp = mesmo segundo
```

**Solução implementada:**
```sql
-- ✅ FUNCIONA
PRIMARY KEY (id)                          ← UUID único para cada entrada
UNIQUE(user_id, isin_id, created_at)      ← Permite múltiplas no mesmo segundo
```

**Agora funciona:**
```
14:30:45.000 → INSERT id=uuid1, isin=ABCD, created_at=14:30:45.000
14:30:45.500 → INSERT id=uuid2, isin=ABCD, created_at=14:30:45.500
              ✓ Ambas coexistem (UUIDs diferentes)
```

---

## 📊 Tabela 3: STRATEGIES → strategy_definitions

### Teu Design Original
```
Table STRATEGIES
  > id_strategy: integer [KEY]
  > strategy_name: string
  > strategy_desc: descrição
  > strategy_status: char[1] | Enabled / Disabled
  > ts_creation: timestamp
  > ts_update: timestamp
```

### Design Final (Implementado)
```sql
CREATE TABLE strategy_definitions (
  id UUID PRIMARY KEY,                    ← Renomeado: id_strategy → id (UUID)
  user_id UUID NOT NULL,                  ← NOVA: RLS
  strategy_name VARCHAR NOT NULL,         ← Mantido ✓
  strategy_desc TEXT,                     ← Tipo melhorado: string → TEXT
  strategy_status VARCHAR CHECK (...),    ← Tipo melhorado: char[1] → VARCHAR + CHECK
  created_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_creation
  updated_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_update
  UNIQUE(user_id, strategy_name)          ← NOVA: Garante um nome por user
);
```

### Mudanças Explicadas

| Aspecto | Original | Final | Razão |
|---|---|---|---|
| **Nome tabela** | `STRATEGIES` | `strategy_definitions` | Diferencia de `strategies` existente na BD (evita conflito) |
| **ID** | `integer` | `UUID` | ✅ Coerência com BD existente (todas PKs são UUIDs) |
| **Sem user_id** | N/A | `user_id UUID NOT NULL` | ✅ Crítico para RLS |
| **strategy_status** | `char[1]` | `VARCHAR + CHECK` | ✅ Mais seguro. Garante apenas 'E' ou 'D' |
| **strategy_desc** | `descrição` (tipo?) | `TEXT` | ✅ Explícito. TEXT permite descrições longas |

---

## 📊 Tabela 4: STRATEGY_PARAMETERS → strategy_parameters

### Teu Design Original
```
Table STRATEGY_PARAMETERS
  > id_strategy: integer
  > pos: integer [KEY]        ← ⚠️ PK composto com pos?
  > param1..param10: double
  > ts_creation: timestamp
  > ts_update: timestamp
```

### Design Final (Implementado)
```sql
CREATE TABLE strategy_parameters (
  id UUID PRIMARY KEY,                    ← NOVA: Chave único (uuid)
  strategy_id UUID NOT NULL FK,           ← Renomeado: id_strategy → strategy_id
  pos INTEGER NOT NULL,                   ← Mantido ✓ (posição/versão)
  param1..param10 DECIMAL(18, 8),         ← Tipo melhorado: double → DECIMAL
  created_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_creation
  updated_at TIMESTAMP WITH TIME ZONE,    ← Renomeado: ts_update
  UNIQUE(strategy_id, pos)                ← Garante uma versão por pos
);
```

### Mudanças Explicadas

| Aspecto | Original | Final | Razão |
|---|---|---|---|
| **PK** | `(id_strategy, pos)` composto | `id UUID PRIMARY KEY` | ✅ Mais simples. UNIQUE(strategy_id, pos) garante unicidade |
| **FK** | `id_strategy: integer` | `strategy_id: UUID FK` | ✅ Coerência. Referencia strategy_definitions.id |
| **Tipos param** | `double` | `DECIMAL(18, 8)` | ✅ Para trading: precisão exata (não floating-point) |

---

## 🔐 Segurança: RLS em Todas as Tabelas

### Antes (Teu Design)
```
Nenhuma referência a user → RLS impossível
❌ User A consegue ler dados do User B
❌ Sem segregação no DB level
```

### Depois (Design Final)
```sql
CREATE POLICY "Users can view their own configs" ON isin_strategy_config
  FOR SELECT USING (user_id = auth.uid());
```

**Resultado:**
- ✅ User A só vê isin_strategy_config onde user_id = seu_id
- ✅ Segurança garantida no DB level (não depende do backend)
- ✅ CRÍTICO para multi-user

---

## 📋 Resumo de Mudanças

### ✅ O que Mantivemos
- Estrutura geral das 4 tabelas
- Campos principais (automated, strategy_name, params)
- Lógica de negócio

### 🔄 O que Corrigimos
| Problema | Solução |
|---|---|
| IDs como string/integer | → UUIDs (padrão BD) |
| Sem user_id | → Adicionado (RLS) |
| Timestamp como PK | → UUID PK + UNIQUE composto |
| char[1] para status | → VARCHAR + CHECK |
| double para preços | → DECIMAL(18,8) |
| Nomes curtos (ts_*) | → Padrão (created_at, updated_at) |
| Sem índices | → Adicionados (performance) |
| Sem RLS | → Ativado (segurança) |

### 🆕 O que Adicionámos
- PKs UUIDs
- RLS policies
- Índices para queries rápidas
- UNIQUE constraints (evitar duplicados)
- CHECK constraints (validação)
- Comentários no SQL (documentação)

---

## 🎯 Recomendações Finais

### 1. **Confiar em UUIDs**
Todos os sistemas modernos usam UUIDs para PKs.
Benefícios:
- Único globalmente
- Rápido em índices
- Seguro (não sequencial)
- Padrão Supabase

### 2. **RLS é Obrigatório**
Sem `user_id`, RLS não funciona.
Isso foi o **erro crítico** no design original.

### 3. **DECIMAL para Finanças**
Nunca usar `DOUBLE` ou `FLOAT` para trading.
DECIMAL(18,8) = precisão exata.

### 4. **Timestamps com TIME ZONE**
Em cloud, é crítico.
Evita bugs de timezone.

---

## 🚀 Próximos Passos

1. ✅ Executar SQL (`db/trading_strategy_tables.sql`)
2. ✅ Validar tabelas em Supabase
3. ⏳ Criar modelos SQLAlchemy
4. ⏳ Criar endpoints FastAPI
5. ⏳ Testar CRUD

---

**Conclusão:** 

Teu design original era **bom** (estrutura correta), mas tinha **3 problemas críticos:**
1. Sem user_id → RLS impossível
2. Timestamp como PK → conflitos em mesmo segundo
3. Tipos simples (string, integer, double) → inseguro/impreciso

Todos resolvidos! ✅
