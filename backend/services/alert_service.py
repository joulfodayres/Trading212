"""
Alertas configuráveis (Item #15).

Cada tipo de alerta pode ser ligado/desligado via app_parameters.alert_settings
(coluna JSON), editável na UI (Config → Alerts). Reutiliza o email_service do
Item #12 (fail-safe: sem SMTP configurado, cai em log).
"""
import logging
from db.supabase_client import get_supabase_client
from services.email_service import send_alert

logger = logging.getLogger(__name__)

DEFAULT_ALERT_SETTINGS = {
    "login_threshold": True,      # N tentativas de login falhadas (Item #12)
    "security_events": True,      # MFA desativado, killswitch acionado
    "limit_reached": True,        # Limite de trading atingido, automação parada
    "order_rejected": True,       # T212 rejeitou uma ordem
    "invalid_credentials": True,  # Erro sugere credenciais T212 inválidas/expiradas
    "cycle_errors": True,         # Vários ciclos seguidos com erro
    "deploy_disabled": True,      # Automação desligada automaticamente após deploy
}


def is_alert_enabled(key: str) -> bool:
    """
    Verifica se um tipo de alerta está ativo em app_parameters.alert_settings.
    Fail-open (assume ativo) em caso de erro — preferimos um email a mais a
    perder um alerta real por uma falha de leitura da BD.
    """
    try:
        client = get_supabase_client()
        result = client.table("app_parameters").select("alert_settings").execute()
        if not result.data:
            return DEFAULT_ALERT_SETTINGS.get(key, True)
        settings_json = result.data[0].get("alert_settings") or {}
        return bool(settings_json.get(key, DEFAULT_ALERT_SETTINGS.get(key, True)))
    except Exception as e:
        logger.warning(f"Erro ao ler alert_settings ({key}): {e}")
        return True


def send_alert_if_enabled(key: str, subject: str, body: str) -> None:
    """Envia o alerta apenas se o interruptor `key` estiver ativo."""
    if is_alert_enabled(key):
        send_alert(subject=subject, body=body)
    else:
        logger.info(f"🔕 Alerta '{key}' desativado nas definições, não enviado: {subject}")
