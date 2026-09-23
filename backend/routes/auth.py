"""
Rotas de autenticação — JWT + Supabase + MFA (Item #12)

Modelo: single-user, uma camada forte (email + password + TOTP obrigatório).
- Sem registo público (bootstrap-only: só funciona se não existir nenhum user)
- Atraso progressivo por IP (nunca bloqueia a conta)
- Dispositivos confiáveis (skip MFA, duração configurável)
- Sessões revogáveis + killswitch
- Token em cookie httpOnly (não em localStorage)
"""
from fastapi import APIRouter, HTTPException, status, Depends, Header, Request, Response
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import base64
import io
import logging
import uuid

import pyotp
import qrcode
from jose import JWTError, jwt
from supabase import create_client, Client

from config.settings import settings
from db.supabase_client import get_supabase_client
from services import login_security_service as security

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

ACCESS_COOKIE_NAME = "access_token"
DEVICE_COOKIE_NAME = "device_id"

_supabase_auth_client: Optional[Client] = None


def get_supabase() -> Client:
    """Cliente Supabase para autenticação (lazy init)"""
    global _supabase_auth_client
    if _supabase_auth_client is None:
        _supabase_auth_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_auth_client


def get_client_ip(request: Request) -> str:
    """Extrai o IP real do cliente, considerando o proxy do Render."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ===== SCHEMAS =====

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    mfa_required: bool
    mfa_setup_required: bool = False
    pre_auth_token: Optional[str] = None
    message: str


class VerifyMfaRequest(BaseModel):
    pre_auth_token: str
    code: str
    trust_device: bool = False


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str
    qr_code_base64: str


class MfaConfirmRequest(BaseModel):
    code: str


class MfaDisableRequest(BaseModel):
    password: str


class UserInfo(BaseModel):
    id: str
    email: str
    is_admin: bool
    totp_enabled: bool


class UserResponse(BaseModel):
    user: UserInfo
    message: str


# ===== JWT HELPERS =====

def create_access_token(user_id: str, email: str, jti: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "jti": jti,
        "stage": "full",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_pre_auth_token(user_id: str, email: str) -> str:
    """Token de curta duração (5 min) para o intervalo entre password OK e código MFA."""
    expire = datetime.utcnow() + timedelta(minutes=5)
    payload = {
        "user_id": user_id,
        "email": email,
        "stage": "mfa_pending",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        logger.warning(f"JWT inválido: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")


def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency: extrai o utilizador do cookie httpOnly (preferencial) ou do
    header Authorization (fallback, útil para Swagger/testes).
    Rejeita tokens de estágio 'mfa_pending' e sessões revogadas.
    """
    token = request.cookies.get(ACCESS_COOKIE_NAME)

    if not token and authorization:
        try:
            scheme, header_token = authorization.split()
            if scheme.lower() == "bearer":
                token = header_token
        except ValueError:
            pass

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    payload = decode_token(token)

    if payload.get("stage") != "full":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação incompleta")

    jti = payload.get("jti")
    if not jti or not security.is_session_active(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão terminada")

    return {"id": payload.get("user_id"), "email": payload.get("email"), "jti": jti}


# ===== USER TABLE HELPERS =====

def _count_users() -> int:
    client = get_supabase_client()
    response = client.table("users").select("id", count="exact").execute()
    return response.count or 0


def _upsert_user(user_id: str, email: str) -> dict:
    """Garante que existe uma row na tabela pública `users` para este utilizador."""
    client = get_supabase_client()
    existing = client.table("users").select("*").eq("id", user_id).execute()
    if existing.data:
        return existing.data[0]

    response = client.table("users").insert({
        "id": user_id,
        "email": email,
        "is_admin": True,  # Single-user: o único user é sempre admin
        "totp_enabled": False,
    }).execute()
    return response.data[0] if response.data else {"id": user_id, "email": email, "totp_enabled": False}


def _get_user(user_id: str) -> Optional[dict]:
    client = get_supabase_client()
    response = client.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def _set_cookies(response: Response, access_token: str, device_token: Optional[str] = None) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_HOURS * 3600,
        path="/",
    )
    if device_token:
        response.set_cookie(
            key=DEVICE_COOKIE_NAME,
            value=device_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.TRUSTED_DEVICE_DAYS * 86400,
            path="/",
        )


def _finish_login(response: Response, request: Request, user_id: str, email: str, trust_device: bool) -> None:
    """Emite o token final (stage=full), cria a sessão, e opcionalmente marca o dispositivo como confiável."""
    jti = str(uuid.uuid4())
    access_token = create_access_token(user_id, email, jti)
    expires_at = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    security.create_session(
        user_id=user_id,
        jti=jti,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )

    device_token = None
    if trust_device:
        device_token = security.generate_device_token()
        security.trust_device(user_id, device_token, get_client_ip(request), request.headers.get("user-agent"))

    _set_cookies(response, access_token, device_token)


# ===== ENDPOINTS =====

@router.post("/register", response_model=dict)
async def register(request: RegisterRequest):
    """
    Cria a conta única desta app (bootstrap-only).
    Bloqueado assim que existir 1 utilizador — não há registo público.
    """
    try:
        existing_users = _count_users()
    except Exception as e:
        logger.error(f"❌ Erro ao consultar tabela `users` (RLS? tabela em falta?): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao aceder à tabela users: {e}",
        )

    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registo desativado — esta aplicação já tem um utilizador configurado",
        )

    if len(request.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password deve ter mínimo 8 caracteres")
    if request.password != request.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords não coincidem")

    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_up({"email": request.email, "password": request.password})
    except Exception as e:
        logger.error(f"❌ Supabase Auth sign_up falhou para {request.email}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erro no Supabase Auth: {e}")

    if not auth_response or not auth_response.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar conta (resposta vazia do Supabase Auth)")

    user_id = str(auth_response.user.id)

    try:
        _upsert_user(user_id, request.email)
    except Exception as e:
        logger.error(f"❌ Conta criada no Auth mas falhou o upsert na tabela `users` ({user_id}): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conta criada no Supabase Auth mas falhou ao gravar na tabela users: {e}",
        )

    logger.info(f"✅ Conta única criada (bootstrap): {request.email}")
    return {"message": "Conta criada com sucesso. Faz login e configura o MFA antes de continuar."}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request, response: Response):
    """
    Passo 1 do login: valida email/password.
    Aplica atraso progressivo por IP. Se MFA estiver ativo e o dispositivo
    não for confiável, devolve um pre_auth_token para o passo 2.
    """
    ip = get_client_ip(req)

    retry_after = security.get_retry_after_seconds(ip)
    if retry_after > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiadas tentativas. Tenta novamente em {retry_after}s",
            headers={"Retry-After": str(retry_after)},
        )

    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })
    except Exception as e:
        # Log the real reason for diagnosis, but keep the HTTP response generic
        # (never reveal "wrong password" vs "email not confirmed" vs "no such user" to a client).
        logger.warning(f"❌ Login falhado: {request.email} (IP: {ip}) — motivo real: {e}")
        auth_response = None

    if not auth_response or not auth_response.user:
        security.record_attempt(ip, request.email, success=False, stage="password")
        security.check_and_alert_threshold(ip, request.email)
        if auth_response is not None:
            # sign_in_with_password didn't raise, but returned no user — log that too
            logger.warning(f"❌ Login falhado: {request.email} (IP: {ip}) — resposta sem user")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou password inválidos")

    user_id = str(auth_response.user.id)
    user_row = _upsert_user(user_id, request.email)
    security.record_attempt(ip, request.email, success=True, stage="password")

    totp_enabled = bool(user_row.get("totp_enabled", False))

    if not totp_enabled:
        # Primeiro login (ou MFA nunca configurado): entra, mas fica marcado para configurar MFA
        _finish_login(response, req, user_id, request.email, trust_device=False)
        logger.info(f"✅ Login sem MFA (setup pendente): {request.email}")
        return LoginResponse(mfa_required=False, mfa_setup_required=True, message="Login efetuado. Configura o MFA.")

    device_token = req.cookies.get(DEVICE_COOKIE_NAME)
    if security.is_device_trusted(user_id, device_token):
        _finish_login(response, req, user_id, request.email, trust_device=False)
        logger.info(f"✅ Login com dispositivo confiável (MFA skip): {request.email}")
        return LoginResponse(mfa_required=False, message="Login efetuado")

    pre_auth_token = create_pre_auth_token(user_id, request.email)
    logger.info(f"🔐 Password OK, aguarda código MFA: {request.email}")
    return LoginResponse(mfa_required=True, pre_auth_token=pre_auth_token, message="Introduz o código do teu autenticador")


@router.post("/login/verify-mfa", response_model=dict)
async def verify_mfa(request: VerifyMfaRequest, req: Request, response: Response):
    """Passo 2 do login: valida o código TOTP e completa a sessão."""
    ip = get_client_ip(req)

    payload = decode_token(request.pre_auth_token)
    if payload.get("stage") != "mfa_pending":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido para este passo")

    user_id = payload.get("user_id")
    email = payload.get("email")

    user_row = _get_user(user_id)
    if not user_row or not user_row.get("totp_secret"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA não configurado para este utilizador")

    totp = pyotp.TOTP(user_row["totp_secret"])
    if not totp.verify(request.code, valid_window=1):
        security.record_attempt(ip, email, success=False, stage="mfa")
        security.check_and_alert_threshold(ip, email)
        logger.warning(f"❌ Código MFA inválido: {email} (IP: {ip})")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

    security.record_attempt(ip, email, success=True, stage="mfa")
    _finish_login(response, req, user_id, email, trust_device=request.trust_device)

    logger.info(f"✅ Login completo com MFA: {email}")
    return {"message": "Login efetuado com sucesso"}


@router.post("/mfa/setup", response_model=MfaSetupResponse)
async def mfa_setup(current_user: dict = Depends(get_current_user)):
    """Gera um novo segredo TOTP (ainda não ativado até /mfa/confirm)."""
    secret = pyotp.random_base32()
    email = current_user["email"]

    client = get_supabase_client()
    client.table("users").update({"totp_secret": secret, "totp_enabled": False}).eq("id", current_user["id"]).execute()

    totp = pyotp.TOTP(secret)
    otpauth_uri = totp.provisioning_uri(name=email, issuer_name="Trading212 Bot")

    qr = qrcode.make(otpauth_uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode()

    logger.info(f"🔐 MFA setup iniciado: {email}")
    return MfaSetupResponse(secret=secret, otpauth_uri=otpauth_uri, qr_code_base64=qr_base64)


@router.post("/mfa/confirm", response_model=dict)
async def mfa_confirm(request: MfaConfirmRequest, current_user: dict = Depends(get_current_user)):
    """Confirma o código gerado a partir do QR code e ativa o MFA definitivamente."""
    user_row = _get_user(current_user["id"])
    if not user_row or not user_row.get("totp_secret"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum setup de MFA em curso")

    totp = pyotp.TOTP(user_row["totp_secret"])
    if not totp.verify(request.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código inválido")

    client = get_supabase_client()
    client.table("users").update({"totp_enabled": True}).eq("id", current_user["id"]).execute()

    logger.info(f"✅ MFA ativado: {current_user['email']}")
    return {"message": "MFA ativado com sucesso"}


@router.post("/mfa/disable", response_model=dict)
async def mfa_disable(request: MfaDisableRequest, req: Request, current_user: dict = Depends(get_current_user)):
    """Desativa o MFA — exige a password novamente (re-auth) por segurança."""
    supabase = get_supabase()
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": current_user["email"],
            "password": request.password,
        })
    except Exception:
        auth_response = None

    if not auth_response or not auth_response.user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorreta")

    client = get_supabase_client()
    client.table("users").update({"totp_enabled": False, "totp_secret": None}).eq("id", current_user["id"]).execute()

    logger.warning(f"⚠️ MFA desativado: {current_user['email']}")
    return {"message": "MFA desativado"}


@router.post("/refresh", response_model=dict)
async def refresh_token(response: Response, req: Request, current_user: dict = Depends(get_current_user)):
    """Renova o access_token (mesma sessão) sem repetir password, enquanto a sessão não for revogada."""
    security.revoke_session(current_user["jti"])  # substitui a sessão antiga por uma nova
    _finish_login(response, req, current_user["id"], current_user["email"], trust_device=False)
    return {"message": "Sessão renovada"}


@router.post("/logout", response_model=dict)
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    """Termina a sessão atual."""
    security.revoke_session(current_user["jti"])
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    logger.info(f"👋 Logout: {current_user['email']}")
    return {"message": "Logout realizado com sucesso"}


@router.post("/logout-all", response_model=dict)
async def logout_all(response: Response, current_user: dict = Depends(get_current_user)):
    """Killswitch: termina TODAS as sessões ativas (todos os dispositivos)."""
    count = security.revoke_all_sessions(current_user["id"])
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(DEVICE_COOKIE_NAME, path="/")
    logger.warning(f"🔴 Killswitch acionado por: {current_user['email']} ({count} sessões terminadas)")
    return {"message": f"{count} sessão(ões) terminada(s)"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Informações do utilizador autenticado."""
    user_row = _get_user(current_user["id"]) or {}
    return UserResponse(
        user=UserInfo(
            id=current_user["id"],
            email=current_user["email"],
            is_admin=bool(user_row.get("is_admin", False)),
            totp_enabled=bool(user_row.get("totp_enabled", False)),
        ),
        message="OK",
    )
