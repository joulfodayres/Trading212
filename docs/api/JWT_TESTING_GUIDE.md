# 🧪 Testing Guide - JWT Authentication

**Objetivo:** Testar os endpoints de autenticação implementados  
**Ferramentas:** curl, Postman, ou REST Client (VS Code)

---

## 1️⃣ Quick Start (curl)

### Test 1.1: Registar novo utilizador

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Senha123",
    "password_confirm": "Senha123"
  }'
```

**Resposta esperada (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
  "email": "teste@example.com",
  "message": "Conta criada com sucesso"
}
```

### Test 1.2: Fazer login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Senha123"
  }'
```

**Resposta esperada (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
  "email": "teste@example.com",
  "message": "Login realizado com sucesso"
}
```

### Test 1.3: Obter info do user (usando token)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
{
  "user": {
    "id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "email": "teste@example.com",
    "is_admin": false
  },
  "message": "Informações de utilizador obtidas com sucesso"
}
```

### Test 1.4: Fazer logout

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

### Test 1.5: Verificar token

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X POST http://localhost:8000/api/auth/verify-token \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
{
  "valid": true,
  "user_id": "d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
  "email": "teste@example.com"
}
```

---

## 2️⃣ Error Cases

### Test 2.1: Erro - Password inválida

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "PasswordErrada"
  }'
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Email ou password inválidos"
}
```

### Test 2.2: Erro - Email não existe

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "naoexiste@example.com",
    "password": "Senha123"
  }'
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Email ou password inválidos"
}
```

### Test 2.3: Erro - Email já registado

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "Senha123",
    "password_confirm": "Senha123"
  }'
```

**Resposta esperada (409 Conflict):**
```json
{
  "detail": "Este email já está registado ou erro ao criar conta"
}
```

### Test 2.4: Erro - Passwords não coincidem

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@example.com",
    "password": "Senha123",
    "password_confirm": "OutraSenha"
  }'
```

**Resposta esperada (400 Bad Request):**
```json
{
  "detail": "Passwords não coincidem"
}
```

### Test 2.5: Erro - Password muito curta

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo@example.com",
    "password": "abc",
    "password_confirm": "abc"
  }'
```

**Resposta esperada (400 Bad Request):**
```json
{
  "detail": "Password deve ter mínimo 8 caracteres"
}
```

### Test 2.6: Erro - Email inválido

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nao_e_email",
    "password": "Senha123"
  }'
```

**Resposta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Test 2.7: Erro - Token inválido

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid_token"
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Token inválido ou expirado"
}
```

### Test 2.8: Erro - Header ausente

```bash
curl -X GET http://localhost:8000/api/auth/me
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Authorization header ausente"
}
```

### Test 2.9: Erro - Header malformado

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: invalid_header"
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Authorization header malformado"
}
```

---

## 3️⃣ Postman Collection

### Importar em Postman

```json
{
  "info": {
    "name": "Trading 212 Auth",
    "description": "Collection de testes de autenticação"
  },
  "item": [
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"teste@example.com\", \"password\": \"Senha123\", \"password_confirm\": \"Senha123\"}"
        },
        "url": {
          "raw": "http://localhost:8000/api/auth/register",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "auth", "register"]
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"email\": \"teste@example.com\", \"password\": \"Senha123\"}"
        },
        "url": {
          "raw": "http://localhost:8000/api/auth/login",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "auth", "login"]
        }
      }
    },
    {
      "name": "Get Me",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8000/api/auth/me",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "auth", "me"]
        }
      }
    },
    {
      "name": "Logout",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8000/api/auth/logout",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "auth", "logout"]
        }
      }
    },
    {
      "name": "Verify Token",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8000/api/auth/verify-token",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "auth", "verify-token"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "token",
      "value": "seu_token_aqui"
    }
  ]
}
```

**Como usar:**
1. Copiar JSON acima
2. Postman → Import → Raw text → Colar
3. Fazer requisição Register (guarda token em {{token}})
4. Usar {{token}} nas outras requisições

---

## 4️⃣ VS Code REST Client

### Criar arquivo `requests.http`:

```http
### Variáveis
@baseUrl = http://localhost:8000
@email = teste@example.com
@password = Senha123
@token = 

### Register
POST {{baseUrl}}/api/auth/register
Content-Type: application/json

{
  "email": "teste@example.com",
  "password": "Senha123",
  "password_confirm": "Senha123"
}

### Login
POST {{baseUrl}}/api/auth/login
Content-Type: application/json

{
  "email": "{{email}}",
  "password": "{{password}}"
}

### Get Me
GET {{baseUrl}}/api/auth/me
Authorization: Bearer {{token}}

### Logout
POST {{baseUrl}}/api/auth/logout
Authorization: Bearer {{token}}

### Verify Token
POST {{baseUrl}}/api/auth/verify-token
Authorization: Bearer {{token}}

### Error - Invalid Password
POST {{baseUrl}}/api/auth/login
Content-Type: application/json

{
  "email": "{{email}}",
  "password": "WrongPassword"
}

### Error - Token Invalid
GET {{baseUrl}}/api/auth/me
Authorization: Bearer invalid_token
```

**Como usar:**
1. Instalar extensão "REST Client" em VS Code
2. Criar arquivo `requests.http` com conteúdo acima
3. Clicar "Send Request" em cima de cada bloco
4. Resultados aparecem em aba "Response"

---

## 5️⃣ Script Python para Testes

### Criar `test_auth.py`:

```python
import requests
import json
import time

BASE_URL = "http://localhost:8000"
EMAIL = f"teste_{int(time.time())}@example.com"  # Email único cada vez
PASSWORD = "Senha123"
TOKEN = None

def test_register():
    global TOKEN
    print(f"\n📝 [TEST] Registar: {EMAIL}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "password_confirm": PASSWORD
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["access_token"]
    TOKEN = data["access_token"]
    print("✅ Sucesso")

def test_login():
    global TOKEN
    print(f"\n🔐 [TEST] Login: {EMAIL}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["access_token"]
    TOKEN = data["access_token"]
    print("✅ Sucesso")

def test_get_me():
    print(f"\n👤 [TEST] Get /me")
    
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["user"]["email"] == EMAIL
    print("✅ Sucesso")

def test_verify_token():
    print(f"\n✔️ [TEST] Verify token")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/verify-token",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["valid"] is True
    print("✅ Sucesso")

def test_logout():
    print(f"\n🚪 [TEST] Logout")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    print("✅ Sucesso")

def test_invalid_password():
    print(f"\n❌ [TEST] Login com password errada")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": EMAIL,
            "password": "WrongPassword"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 401
    print("✅ Sucesso (erro esperado)")

if __name__ == "__main__":
    print("🧪 Testing Trading 212 Auth API")
    print("=" * 50)
    
    try:
        test_register()
        test_login()
        test_get_me()
        test_verify_token()
        test_invalid_password()
        test_logout()
        
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
```

**Executar:**
```bash
python test_auth.py
```

---

## 6️⃣ FastAPI Swagger UI

**Abrir no browser:** http://localhost:8000/docs

- Listar todos os endpoints
- Testar diretamente na interface (Try it out)
- Ver schemas Pydantic
- Copiar curl commands

---

## 7️⃣ Logs no Backend

### Ver logs em tempo real:

```bash
# Terminal do backend (se estiver em desenvolvimento)
# Deve ver:
[INFO] 🔐 Tentativa de login: teste@example.com
[INFO] ✅ Login bem-sucedido: teste@example.com (ID: d1c2b3a4-e5f6-47g8-h9i0-j1k2l3m4n5o6)
```

---

## ✅ Checklist de Testes

- [ ] Register com email novo → sucesso (200)
- [ ] Register com email duplicado → erro (409)
- [ ] Register com password < 8 chars → erro (400)
- [ ] Register com passwords diferentes → erro (400)
- [ ] Login com email/password corretos → sucesso (200)
- [ ] Login com password errada → erro (401)
- [ ] Login com email inexistente → erro (401)
- [ ] GET /me com token válido → sucesso (200)
- [ ] GET /me sem token → erro (401)
- [ ] GET /me com token inválido → erro (401)
- [ ] Verify token com token válido → sucesso (200)
- [ ] Verify token com token expirado → erro (401)
- [ ] Logout com token válido → sucesso (200)
- [ ] Logout sem token → erro (401)

---

## 🐛 Troubleshooting

### Backend não responde

```bash
# Verificar se está rodando
curl http://localhost:8000/health
# Deve retornar: {"status":"healthy"}
```

### Erro 401 em todos os endpoints

```bash
# Verificar se JWT_SECRET_KEY está em .env
grep JWT_SECRET_KEY backend/.env

# Se não tiver, gerar:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Supabase connection error

```bash
# Verificar credenciais
grep SUPABASE backend/.env

# Testar connection
python -c "from supabase import create_client; from config.settings import settings; client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY); print('OK')"
```

---

## 📞 Next Steps

1. Testar todos os endpoints com curl/Postman
2. Integrar com frontend React
3. Armazenar token em localStorage
4. Adicionar rate limiting
5. Implementar refresh tokens
