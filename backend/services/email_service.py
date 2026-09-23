"""
Serviço de envio de alertas por email (Item #12)

Sem SMTP configurado, o alerta cai em log WARNING (fail-safe) —
nunca bloqueia o fluxo de login por falta de config de email.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from config.settings import settings

logger = logging.getLogger(__name__)


def send_alert(subject: str, body: str) -> bool:
    """
    Envia um email de alerta de segurança.

    Se SMTP_HOST ou ALERT_EMAIL_TO não estiverem configurados,
    regista o alerta em log e retorna False (não é um erro fatal).

    Args:
        subject: Assunto do email
        body: Corpo do email (texto simples)

    Returns:
        True se enviado com sucesso, False caso contrário
    """
    if not settings.ALERT_EMAIL_TO or not settings.SMTP_HOST:
        logger.warning(
            f"⚠️ ALERTA DE SEGURANÇA (SMTP não configurado, apenas log): "
            f"{subject} — {body}"
        )
        return False

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER or "trading212-bot@localhost"
        msg["To"] = settings.ALERT_EMAIL_TO

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ Alerta de segurança enviado por email: {subject}")
        return True

    except Exception as e:
        logger.error(f"❌ Falha ao enviar alerta por email: {e}")
        return False
