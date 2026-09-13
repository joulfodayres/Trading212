"""
Rotas de autenticação com Supabase Auth
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import logging
from config.settings import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Inicializar cliente Supabase
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


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


class AuthResponse(BaseModel):
    """Resposta de autenticação"""
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


# ===== HELPERS =====

def get_current_user_from_token(token: str) -> dict:
    """
    Verifica token JWT e retorna user info
    Levanta HTTPException 401 se inválido
    """
    try:
        # Verificar token com Supabase
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        return user.dict()
    except Exception as e:
        logger.error(f"Erro ao verificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


# ===== ENDPOINTS =====

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Fazer login com email e password
    Retorna JWT access_token
    """
    try:
        # Autenticar com Supabase
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not response or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos"
            )

        user = response.user
        session = response.session

        logger.info(f"✅ Login bem-sucedido: {request.email}")

        return AuthResponse(
            access_token=session.access_token,
            user={
                "id": str(user.id),
                "email": user.email,
                "is_admin": False  # TODO: Buscar de BD
            },
            message="Login realizado com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Criar nova conta com email e password
    Retorna JWT access_token
    """
    try:
        # Validar passwords
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

        # Registar com Supabase
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email já está registado"
            )

        user = response.user
        session = response.session

        # TODO: Guardar user em BD (users table)

        logger.info(f"✅ Registo bem-sucedido: {request.email}")

        return AuthResponse(
            access_token=session.access_token if session else "",
            user={
                "id": str(user.id),
                "email": user.email,
                "is_admin": False
            },
            message="Conta criada com sucesso"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar conta"
        )


@router.post("/logout")
async def logout():
    """Logout (invalida JWT no cliente)"""
    try:
        logger.info("✅ Logout bem-sucedido")
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao fazer logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(token: str):
    """
    Obter informações do utilizador autenticado
    Token deve ser passado em header ou query param
    """
    try:
        user_data = get_current_user_from_token(token)

        return UserResponse(
            user=UserInfo(
                id=str(user_data.get("id")),
                email=user_data.get("email", ""),
                is_admin=False  # TODO: Buscar de BD
            ),
            message="Utilizador autenticado"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao obter informações"
        )
