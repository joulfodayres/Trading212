# 🔐 Autenticação JWT - Implementação Completa

**Data:** 2026-09-15  
**Status:** ✅ Implementado e testado  
**Ficheiro:** `backend/routes/auth.py`

---

## 📋 Resumo

Implementação completa de autenticação real com **JWT (JSON Web Tokens)** no backend FastAPI. O sistema:

- ✅ Autentica utilizadores com **Supabase Auth** (valida passwords de forma segura)
- ✅ Cria **JWT tokens** assinados com chave secreta (válidos por 24h)
- ✅ Verifica tokens em todos os endpoints autenticados
- ✅ Utiliza **Bearer token** no Authorization header (RFC 6750)
- ✅ Logging detalhado de todas as operações
- ✅ Tratamento robusto de erros (HTTP status codes apropriados)

---

## 🚀 Endpoints Implementados

### 1. **POST /api/auth/login** → Login com JWT

Autentica utilizador e retorna JWT token.

**Request:**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "utilizador@example.com",
  "password": "senha123"
}
```

**Response (201 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "ab1036ff-937d-46e5-8f5b-bab07f1fb100",
  "email": "utilizador@example.com",
  "message": "Login realizado com sucesso"
}
```

**Status codes:**
- `200 OK` - Login bem-sucedido
- `401 Unauthorized` - Email/password inválidos
- `422 Unprocessable Entity` - Validação Pydantic falhou

---

### 2. **POST /api/auth/register** → Criar conta nova

Cria nova conta em Supabase Auth e retorna JWT.

**Request:**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "novo@example.com",
  "password": "MinhaSenh@123",
  "password_confirm": "MinhaSenh@123"
}
```

**Validações:**
- Email deve ser válido (Pydantic EmailStr)
- Password mínimo 8 caracteres
- Passwords devem coincidir
- Email deve ser único (erro 409 se já existe)

**Response (201 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "novo-uuid-aqui",
  "email": "novo@example.com",
  "message": "Conta criada com sucesso"
}
```

**Status codes:**
- `200 OK` - Registo bem-sucedido
- `400 Bad Request` - Validação falhou (password < 8 chars, etc)
- `409 Conflict` - Email já registado
- `422 Unprocessable Entity` - Formato inválido

---

### 3. **POST /api/auth/logout** → Logout

Simples confirmação de logout (JWT invalidado no cliente).

**Request:**
```bash
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

**Status codes:**
- `200 OK` - Logout bem-sucedido
- `401 Unauthorized` - Token inválido/ausente

---

### 4. **GET /api/auth/me** → Obter info do user autenticado

Retorna informações do utilizador autenticado.

**Request:**
```bash
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "ab1036ff-937d-46e5-8f5b-bab07f1fb100",
    "email": "utilizador@example.com",
    "is_admin": false
  },
  "message": "Informações de utilizador obtidas com sucesso"
}
```

**Status codes:**
- `200 OK` - Sucesso
- `401 Unauthorized` - Token inválido/ausente/expirado

---

### 5. **POST /api/auth/verify-token** → Verificar validade do token

Valida um JWT token e retorna user info.

**Request:**
```bash
POST /api/auth/verify-token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "ab1036ff-937d-46e5-8f5b-bab07f1fb100",
  "email": "utilizador@example.com"
}
```

**Status codes:**
- `200 OK` - Token válido
- `401 Unauthorized` - Token inválido/expirado

---

## 🔑 JWT Token Structure

### Payload (claims)

O JWT contém as seguintes informações:

```python
{
  "user_id": "ab1036ff-937d-46e5-8f5b-bab07f1fb100",
  "email": "utilizador@example.com",
  "exp": 1726424340,                           # Expiration time (Unix timestamp)
  "iat": 1726338140                            # Issued at time (Unix timestamp)
}
```

### Assinatura

- **Algoritmo:** HS256 (HMAC-SHA256)
- **Chave secreta:** `settings.JWT_SECRET_KEY` (de `.env`)
- **Válido por:** 24 horas (configurável em `settings.JWT_EXPIRATION_HOURS`)

### Formato completo

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJ1c2VyX2lkIjoiYWIxMDM2ZmYtOTM3ZC00NmU1LThmNWItYmFiMDdmMWZiMTAwIiwi...
.K1s2H7d9f_H3j2k5L8m9Q0r1S2t3U4v5W6x7Y8z9A0
```

Estrutura: `HEADER.PAYLOAD.SIGNATURE`

---

## 🔐 Fluxo de Autenticação

### Login Flow

```
1. Cliente envia POST /api/auth/login (email + password)
2. Backend valida com Supabase Auth
   ├─ Se falhar: retorna 401
   └─ Se sucesso: obter user_id
3. Backend cria JWT token (user_id + email + expiry)
4. Retorna token ao cliente
5. Cliente armazena token (localStorage/sessionStorage)
6. Próximas requisições: Authorization: Bearer <token>
```

### Verificação de Token

```
1. Cliente envia requisição com Authorization header
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
2. Backend extrai token do header
3. Backend decodifica e verifica assinatura com JWT_SECRET_KEY
4. Se válido e não expirado: aceita requisição
5. Se inválido/expirado: retorna 401 Unauthorized
```

### Logout Flow

```
1. Cliente envia POST /api/auth/logout com token válido
2. Backend retorna confirmação
3. Cliente remove token de localStorage
```

---

## 📚 Schemas Pydantic

### LoginRequest
```python
class LoginRequest(BaseModel):
    email: EmailStr          # Validado por Pydantic
    password: str            # Mínimo 8 chars em Supabase
```

### RegisterRequest
```python
class RegisterRequest(BaseModel):
    email: EmailStr          # Deve ser único
    password: str            # Mínimo 8 chars validado no endpoint
    password_confirm: str    # Deve ser igual a password
```

### TokenResponse
```python
class TokenResponse(BaseModel):
    access_token: str        # JWT token
    token_type: str          # "Bearer"
    user_id: str             # UUID
    email: str               # Email do user
    message: str             # "Login realizado com sucesso"
```

### UserResponse
```python
class UserResponse(BaseModel):
    user: UserInfo           # id, email, is_admin
    message: str
```

---

## 🛡️ Segurança

### Proteções implementadas:

1. **JWT assinado** com chave secreta (não pode ser forjado)
2. **Supabase Auth** para validação de passwords (não hashing local)
3. **Bearer token** em Authorization header (RFC 6750 compliant)
4. **Expiração de token** (24 horas)
5. **Validação de email** (Pydantic EmailStr)
6. **Logging detalhado** de todas as operações
7. **HTTP status codes** apropriados para cada erro

### Proteções TODO (próximas fases):

- [ ] Refresh tokens (30 dias) para renovar sem fazer login
- [ ] Rate limiting em `/login` e `/register` (prevenir brute force)
- [ ] Email verification no register (confirmar email)
- [ ] Password reset flow
- [ ] CORS restringido a frontend URL (não `*`)
- [ ] HTTPS obrigatório em produção (Render já faz)

---

## 💻 Helpers/Utilities

### `create_jwt_token(user_id, email, expires_delta=None)`

Cria um JWT token assinado.

```python
token = create_jwt_token(
    user_id="ab1036ff-937d-46e5-8f5b-bab07f1fb100",
    email="utilizador@example.com",
    expires_delta=timedelta(hours=48)  # Optional
)
# Retorna: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### `verify_jwt_token(token)`

Verifica e decodifica token.

```python
payload = verify_jwt_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
# Retorna: {"user_id": "...", "email": "...", "exp": 1726424340, ...}
# Levanta HTTPException(401) se inválido/expirado
```

### `get_current_user_from_token(token)`

Extrai user info do token.

```python
user = get_current_user_from_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
# Retorna: {"id": "ab1036ff...", "email": "utilizador@example.com"}
```

### `get_current_user(authorization_header)` (Dependency)

FastAPI dependency para extrair user do Authorization header.

```python
@router.get("/exemplo")
async def exemplo_endpoint(current_user: dict = Depends(get_current_user)):
    return {"user": current_user["email"]}
```

Uso:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://localhost:8000/api/exemplo
```

---

## 🧪 Exemplos de Uso

### Test 1: Registar novo utilizador

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@example.com",
    "password": "SenhaForte123",
    "password_confirm": "SenhaForte123"
  }'
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
  "email": "novo@example.com",
  "message": "Conta criada com sucesso"
}
```

### Test 2: Fazer login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@example.com",
    "password": "SenhaForte123"
  }'
```

### Test 3: Obter info do user (usando token)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

Resposta:
```json
{
  "user": {
    "id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "email": "novo@example.com",
    "is_admin": false
  },
  "message": "Informações de utilizador obtidas com sucesso"
}
```

### Test 4: Fazer logout

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

### Test 5: Erro com token expirado/inválido

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid_token"
```

Resposta (401):
```json
{
  "detail": "Token inválido ou expirado"
}
```

---

## 📝 Logging

Todas as operações geram logs estruturados:

```
[INFO] 🔐 Tentativa de login: utilizador@example.com
[INFO] ✅ Login bem-sucedido: utilizador@example.com (ID: ab1036ff-937d-46e5-8f5b-bab07f1fb100)
[INFO] 📝 Tentativa de registo: novo@example.com
[INFO] ✅ Registo bem-sucedido: novo@example.com (ID: d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6)
[INFO] ✅ Logout: utilizador@example.com
[INFO] 📋 Fetch user info: utilizador@example.com
[ERROR] ❌ Falha de login: utilizador@example.com (credenciais inválidas)
[ERROR] Erro ao verificar JWT: Token has expired
```

---

## 🔄 Integração com outros endpoints

Para proteger um endpoint com autenticação:

```python
from fastapi import Depends
from routes.auth import get_current_user

@router.get("/api/isins")
async def list_isins(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    email = current_user["email"]
    
    # Agora temos user_id para filtrar dados por user
    # Exemplo: buscar ISINs apenas deste user em BD
    isins = await db.isins.select("*").eq("user_id", user_id).execute()
    return isins
```

---

## ⚙️ Configuração

Variáveis de ambiente necessárias (em `.env`):

```env
# JWT
JWT_SECRET_KEY=trading212-bot-secret-key-change-later
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Supabase
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]
```

Já configuradas em `config/settings.py` via Pydantic BaseSettings.

---

## ✅ Checklist

- [x] Endpoints `/login` e `/register` funcionando
- [x] JWT tokens criados corretamente (python-jose)
- [x] Verificação de tokens em endpoints autenticados
- [x] Logging detalhado (emojis + mensagens em PT)
- [x] Tratamento robusto de erros
- [x] Schemas Pydantic para validação
- [x] Dependency injection (FastAPI best practice)
- [x] Suportado em `/api/auth/*` router
- [x] Testável via curl/Postman
- [ ] TODO: BD (users table) para guardar user info
- [ ] TODO: Refresh tokens (30 dias)
- [ ] TODO: Rate limiting em login/register
- [ ] TODO: Email verification
- [ ] TODO: Password reset

---

## 📞 Próximas Fases

### Fase 2: Integração com BD

- [ ] Guardar user em tabela `users` no Supabase
- [ ] Buscar `is_admin` de BD em `/me` endpoint
- [ ] Implementar middleware para extrair user_id automaticamente

### Fase 3: Security Enhancements

- [ ] Refresh tokens (token expiração curta + refresh longo)
- [ ] Rate limiting (max 5 tentativas de login em 15 min)
- [ ] Email verification (enviar link de confirmação)
- [ ] Password reset flow (enviar email com link)

### Fase 4: Frontend Integration

- [ ] Integrar `/login` com React auth form
- [ ] Armazenar token em localStorage
- [ ] Auto-login se token válido
- [ ] Logout + remover token
- [ ] Redirecionar não-autenticados para login

---

## 📚 Referências

- **JWT Spec:** https://tools.ietf.org/html/rfc7519
- **python-jose:** https://python-jose.readthedocs.io/
- **FastAPI Auth:** https://fastapi.tiangolo.com/tutorial/security/
- **Supabase Auth:** https://supabase.com/docs/guides/auth

---

**Implementado em:** 2026-09-15  
**Versão:** 1.0  
**Status:** ✅ Pronto para integração com frontend
