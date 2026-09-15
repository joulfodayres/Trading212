"""
Rotas de autenticação com JWT e Supabase
"""
from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Inicializar cliente Supabase (lazy - apenas quando necessário)
_supabase_client = None

def get_supabase() -> Client:
    """Obter cliente Supabase (lazy initialization)"""
    global _supabase_client
    if _supabase_client is None:
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    return _supabase_client

# Configurar password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===== SCHEMAS =====

class LoginRequest(BaseModel):
    """Requisição de login"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Requisição de registo"""
    email: EmailStr
    password: str
    password_confirm: str


class TokenResponse(BaseModel):
    """Resposta com token JWT"""
    access_token: str
    token_type: str = "Bearer"
    user_id: str
    email: str
    message: str


class AuthResponse(BaseModel):
    """Resposta de autenticação (compatível com API)"""
    access_token: str
    user: dict
    message: str


class UserInfo(BaseModel):
    """Informações do utilizador"""
    id: str
    email: str
    is_admin: bool


class UserResponse(BaseModel):
    """Resposta com user info"""
    user: UserInfo
    message: str


# ===== JWT HELPERS =====

def create_jwt_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um JWT token assinado com a chave secreta

    Args:
        user_id: ID do utilizador
        email: Email do utilizador
        expires_delta: Tempo de expiração (padrão: 24 horas)

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    expire = datetime.utcnow() + expires_delta
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_jwt_token(token: str) -> dict:
    """
    Verifica e decodifica um JWT token

    Args:
        token: JWT token string

    Returns:
        Payload do token (contém user_id e email)

    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        email = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return payload
    except JWTError as e:
        logger.error(f"Erro ao verificar JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def get_current_user_from_token(token: str) -> dict:
    """
    Verifica token JWT e retorna user info
    Levanta HTTPException 401 se inválido

    Args:
        token: JWT token string

    Returns:
        Dicionário com dados do user
    """
    payload = verify_jwt_token(token)
    return {
        "id": payload.get("user_id"),
        "email": payload.get("email")
    }


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency para extrair user do Authorization header
    Espera formato: "Bearer <token>"

    Args:
        authorization: Authorization header

    Returns:
        Dicionário com dados do user
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header ausente"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Scheme de autenticação inválido"
            )
        return get_current_user_from_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header malformado"
        )


# ===== ENDPOINTS =====

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Fazer login com email e password
    Retorna JWT access_token (válido por 24h)

    Request body:
    - email: EmailStr
    - password: str

    Response:
    - access_token: JWT token
    - token_type: "Bearer"
    - user_id: UUID do utilizador
    - email: Email do utilizador
    - message: Mensagem de sucesso
    """
    try:
        logger.info(f"🔐 Tentativa de login: {request.email}")

        # Autenticar com Supabase Auth
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not response or not response.user:
            logger.warning(f"❌ Falha de login: {request.email} (credenciais inválidas)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou password inválidos"
            )

        user = response.user
        user_id = str(user.id)

        # Criar JWT token próprio
        access_token = create_jwt_token(user_id, request.email)

        logger.info(f"✅ Login bem-sucedido: {request.email} (ID: {user_id})")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            user_id=user_id,
            email=request.email,
            message="Login realizado com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao fazer login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou password inválidos"
        )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Criar nova conta com email e password
    Retorna JWT access_token (válido por 24h)

    Request body:
    - email: EmailStr
    - password: str (mínimo 8 caracteres)
    - password_confirm: str (deve ser igual a password)

    Response:
    - access_token: JWT token
    - token_type: "Bearer"
    - user_id: UUID do utilizador
    - email: Email do utilizador
    - message: Mensagem de sucesso
    """
    try:
        logger.info(f"📝 Tentativa de registo: {request.email}")

        # Validações
        if len(request.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password deve ter mínimo 8 caracteres"
            )

        if request.password != request.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords não coincidem"
            )

        # Criar conta em Supabase Auth
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })

        if not response or not response.user:
            logger.warning(f"❌ Falha de registo: {request.email} (email já registado ou erro interno)")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email já está registado ou erro ao criar conta"
            )

        user = response.user
        user_id = str(user.id)

        # TODO: Guardar user em BD (users table) com is_admin=False
        # await db.users.insert({
        #     "id": user_id,
        #     "email": request.email,
        #     "is_admin": False
        # })

        # Criar JWT token
        access_token = create_jwt_token(user_id, request.email)

        logger.info(f"✅ Registo bem-sucedido: {request.email} (ID: {user_id})")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            user_id=user_id,
            email=request.email,
            message="Conta criada com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao registar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar conta"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (invalida JWT no cliente)

    Headers:
    - Authorization: Bearer <token>

    Response:
    - message: Confirmação de logout
    """
    try:
        logger.info(f"✅ Logout: {current_user.get('email')}")
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:
        logger.error(f"❌ Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao fazer logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Obter informações do utilizador autenticado

    Headers:
    - Authorization: Bearer <token>

    Response:
    - user: UserInfo (id, email, is_admin)
    - message: Mensagem

    Levanta 401 se token inválido ou ausente
    """
    try:
        logger.info(f"📋 Fetch user info: {current_user.get('email')}")

        return UserResponse(
            user=UserInfo(
                id=current_user.get("id"),
                email=current_user.get("email", ""),
                is_admin=False  # TODO: Buscar de BD (users table)
            ),
            message="Informações de utilizador obtidas com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter informações"
        )


@router.post("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verificar se um token JWT é válido

    Headers:
    - Authorization: Bearer <token>

    Response:
    - valid: bool (sempre True se chegar aqui)
    - user_id: UUID
    - email: Email

    Levanta 401 se token inválido ou ausente
    """
    try:
        return {
            "valid": True,
            "user_id": current_user.get("id"),
            "email": current_user.get("email")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao verificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


@router.post("/test-token")
async def get_test_token():
    """
    🧪 DEBUG ONLY - Obter JWT token de teste para testes do CRUD
    Retorna um token válido para o utilizador de teste (teste@trading212.com)

    ⚠️ REMOVE EM PRODUÇÃO

    Response:
    - token: JWT token válido por 24h
    - user_id: UUID do utilizador de teste
    - email: Email do utilizador de teste
    """
    if settings.FASTAPI_ENV == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint de teste não disponível em produção"
        )

    try:
        logger.info("🧪 Gerando token de teste")

        # Fixed test user ID
        test_user_id = "ab1036ff-937d-46e5-8f5b-bab07f1fb100"
        test_email = "teste@trading212.com"

        # Create JWT token
        access_token = create_jwt_token(test_user_id, test_email)

        return {
            "token": access_token,
            "access_token": access_token,  # Compatibilidade
            "user_id": test_user_id,
            "email": test_email,
            "message": "Token de teste gerado com sucesso"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao gerar token de teste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar token de teste"
        )
