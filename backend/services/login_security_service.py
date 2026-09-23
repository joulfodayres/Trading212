"""
Serviço central de segurança de login (Item #12)

Responsabilidades:
- Atraso progressivo por IP (nunca bloqueia a conta, só abranda o IP)
- Dispositivos confiáveis (skip MFA após primeiro login)
- Sessões revogáveis (killswitch)
- Logging de tentativas + alerta por email

Single-user app: o foco é abrandar/detetar ataques sem nunca poder
trancar o próprio utilizador fora da aplicação.
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from config.settings import settings
from db.supabase_client import get_supabase_client
from services.email_service import send_alert

logger = logging.getLogger(__name__)

# Janela deslizante para contar falhas recentes (atraso progressivo)
FAILURE_WINDOW_MINUTES = 30


def _now() -> datetime:
    return datetime.utcnow()


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# ===== PROGRESSIVE DELAY (por IP) =====

def record_attempt(ip_address: str, email: Optional[str], success: bool, stage: str = "password") -> None:
    """Regista uma tentativa de login (sucesso ou falha) para um IP."""
    try:
        client = get_supabase_client()
        client.table("login_attempts").insert({
            "ip_address": ip_address,
            "email": email,
            "success": success,
            "stage": stage,
        }).execute()
    except Exception as e:
        # Nunca deixar o logging partir o fluxo de login
        logger.error(f"Erro ao registar tentativa de login: {e}")


def count_recent_failures(ip_address: str) -> int:
    """Conta falhas consecutivas recentes para um IP (janela deslizante)."""
    try:
        client = get_supabase_client()
        window_start = _now() - timedelta(minutes=FAILURE_WINDOW_MINUTES)

        response = (
            client.table("login_attempts")
            .select("success, created_at")
            .eq("ip_address", ip_address)
            .gte("created_at", _iso(window_start))
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )

        rows = response.data or []
        # Contar falhas consecutivas a partir da mais recente, parar no primeiro sucesso
        failures = 0
        for row in rows:
            if row.get("success"):
                break
            failures += 1
        return failures

    except Exception as e:
        logger.error(f"Erro ao contar falhas recentes: {e}")
        return 0  # Fail-open no cálculo do atraso (nunca bloquear por erro interno)


def get_retry_after_seconds(ip_address: str) -> int:
    """
    Calcula o atraso progressivo (em segundos) para um IP, baseado em falhas recentes.

    Exponencial: 0s, 2s, 4s, 8s, 16s, 32s... com teto configurável.
    Retorna 0 se o IP pode tentar imediatamente.
    """
    failures = count_recent_failures(ip_address)
    if failures == 0:
        return 0

    max_seconds = settings.LOGIN_DELAY_MAX_MINUTES * 60
    delay = min(2 ** (failures - 1), max_seconds)
    return delay


def check_and_alert_threshold(ip_address: str, email: Optional[str]) -> None:
    """Envia alerta por email se o número de falhas atingir o threshold configurado."""
    failures = count_recent_failures(ip_address)
    if failures > 0 and failures % settings.LOGIN_ALERT_THRESHOLD == 0:
        send_alert(
            subject=f"⚠️ Trading 212 Bot — {failures} tentativas de login falhadas",
            body=(
                f"Foram detetadas {failures} tentativas de login falhadas consecutivas.\n\n"
                f"IP de origem: {ip_address}\n"
                f"Email visado: {email or '(não fornecido)'}\n"
                f"Janela: últimos {FAILURE_WINDOW_MINUTES} minutos\n\n"
                f"Se não reconheces esta atividade, considera terminar todas as sessões "
                f"ativas (killswitch) e mudar a password."
            ),
        )


# ===== TRUSTED DEVICES =====

def generate_device_token() -> str:
    """Gera um token de dispositivo aleatório e imprevisível."""
    return secrets.token_urlsafe(32)


def is_device_trusted(user_id: str, device_token: Optional[str]) -> bool:
    """Verifica se um device_token está marcado como confiável e ainda válido."""
    if not device_token or settings.TRUSTED_DEVICE_DAYS == 0:
        return False

    try:
        client = get_supabase_client()
        response = (
            client.table("trusted_devices")
            .select("id, expires_at")
            .eq("user_id", user_id)
            .eq("device_token", device_token)
            .execute()
        )

        rows = response.data or []
        if not rows:
            return False

        expires_at = datetime.fromisoformat(rows[0]["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None)
        if expires_at < _now():
            return False

        # Atualizar last_used_at (fire-and-forget, não crítico)
        try:
            client.table("trusted_devices").update({
                "last_used_at": _iso(_now())
            }).eq("id", rows[0]["id"]).execute()
        except Exception:
            pass

        return True

    except Exception as e:
        logger.error(f"Erro ao verificar trusted device: {e}")
        return False  # Fail-closed: em caso de dúvida, pedir MFA


def trust_device(user_id: str, device_token: str, ip_address: str, user_agent: Optional[str]) -> None:
    """Marca um dispositivo como confiável (skip MFA até expirar)."""
    if settings.TRUSTED_DEVICE_DAYS == 0:
        return  # Configuração exige MFA sempre — não guardar nada

    try:
        client = get_supabase_client()
        expires_at = _now() + timedelta(days=settings.TRUSTED_DEVICE_DAYS)

        client.table("trusted_devices").insert({
            "user_id": user_id,
            "device_token": device_token,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "expires_at": _iso(expires_at),
        }).execute()

    except Exception as e:
        logger.error(f"Erro ao marcar trusted device: {e}")


# ===== SESSIONS (revocable + killswitch) =====

def create_session(user_id: str, jti: str, ip_address: str, user_agent: Optional[str], expires_at: datetime) -> None:
    """Regista uma nova sessão ativa (para permitir revogação futura)."""
    try:
        client = get_supabase_client()
        client.table("active_sessions").insert({
            "user_id": user_id,
            "jti": jti,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": _iso(expires_at),
            "revoked": False,
        }).execute()
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {e}")


def is_session_active(jti: str) -> bool:
    """Verifica se uma sessão (pelo jti do JWT) ainda está ativa (não revogada)."""
    try:
        client = get_supabase_client()
        response = (
            client.table("active_sessions")
            .select("revoked")
            .eq("jti", jti)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return False  # Sessão desconhecida — tratar como inválida
        return not rows[0].get("revoked", False)
    except Exception as e:
        logger.error(f"Erro ao verificar sessão ativa: {e}")
        return True  # Fail-open: erro de BD não deve deitar todo o user fora a meio do dia


def revoke_session(jti: str) -> None:
    """Revoga uma sessão específica (logout normal)."""
    try:
        client = get_supabase_client()
        client.table("active_sessions").update({
            "revoked": True,
            "revoked_at": _iso(_now()),
        }).eq("jti", jti).execute()
    except Exception as e:
        logger.error(f"Erro ao revogar sessão: {e}")


def revoke_all_sessions(user_id: str) -> int:
    """Killswitch: revoga TODAS as sessões ativas de um utilizador. Retorna quantas foram revogadas."""
    try:
        client = get_supabase_client()
        response = (
            client.table("active_sessions")
            .update({"revoked": True, "revoked_at": _iso(_now())})
            .eq("user_id", user_id)
            .eq("revoked", False)
            .execute()
        )
        count = len(response.data or [])
        logger.warning(f"🔴 KILLSWITCH: {count} sessões revogadas para user {user_id}")
        return count
    except Exception as e:
        logger.error(f"Erro ao revogar todas as sessões: {e}")
        return 0
