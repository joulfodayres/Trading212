"""
Limites de trading (Item #15): valor máximo por ordem de compra/venda, e
gasto máximo diário. Consultado pelo AutomationEngine antes de colocar cada
ordem, e pelos endpoints de configuração/dashboard para mostrar consumo.

Regras acordadas no brainstorming:
- max_buy_order_value / max_sell_order_value: bloqueiam a ordem específica
  ANTES de a colocar na T212 (preventivo).
- max_daily_spend: soma de compras executadas HOJE (Europe/Lisbon) menos
  vendas executadas com lucro (valor total da venda). Verificado antes de
  cada ordem nova — pode ser ultrapassado por ordens que executem em lote
  entre verificações (risco aceite explicitamente, não corrigir).
- Atingir qualquer limite para a automação POR COMPLETO (grid_trading_enabled
  = False) — não só a ordem em causa. Ordens pendentes na T212 não são
  canceladas. Retoma é sempre manual (mesmo no dia seguinte).
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo

from db.supabase_client import get_supabase_client
from services.alert_service import send_alert_if_enabled

logger = logging.getLogger(__name__)

LISBON_TZ = ZoneInfo("Europe/Lisbon")


def get_trading_limits() -> Dict[str, Any]:
    """Lê os limites configurados + o motivo de paragem atual (se houver)."""
    try:
        client = get_supabase_client()
        result = client.table("app_parameters").select(
            "max_buy_order_value, max_sell_order_value, max_daily_spend, automation_disabled_reason"
        ).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.warning(f"Erro ao ler limites de trading: {e}")
        return {}


def get_daily_spend() -> float:
    """
    Gasto diário = compras executadas - vendas executadas com lucro (valor
    total da venda), desde as 00:00 de Europe/Lisbon.

    Fail-open (devolve 0.0) em caso de erro de leitura — uma falha transitória
    de BD nunca deve, por si só, travar a automação através deste cálculo.
    """
    try:
        client = get_supabase_client()
        now_lisbon = datetime.now(LISBON_TZ)
        start_of_day_lisbon = now_lisbon.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day_utc = start_of_day_lisbon.astimezone(ZoneInfo("UTC")).isoformat()

        result = client.table("orders").select(
            "side, fill_net_value, fill_realised_pnl"
        ).eq("status", "FILLED").gte("filled_at", start_of_day_utc).execute()

        spend = 0.0
        for row in result.data or []:
            net_value = row.get("fill_net_value")
            if net_value is None:
                continue
            if row.get("side") == "BUY":
                spend += abs(net_value)
            elif row.get("side") == "SELL" and (row.get("fill_realised_pnl") or 0) > 0:
                spend += abs(net_value)
        return spend
    except Exception as e:
        logger.warning(f"Erro ao calcular gasto diário: {e}")
        return 0.0


def check_order_against_limits(order_type: str, order_value: float) -> Optional[str]:
    """
    Verifica uma ordem prestes a ser colocada contra os limites configurados.
    Devolve o motivo de bloqueio (string) se violar algum, ou None se estiver OK.
    """
    limits = get_trading_limits()

    max_value_key = "max_buy_order_value" if order_type == "BUY" else "max_sell_order_value"
    max_value = limits.get(max_value_key)
    if max_value is not None and order_value > max_value:
        label = "compra" if order_type == "BUY" else "venda"
        return (
            f"Valor da ordem de {label} (€{order_value:.2f}) excede o máximo "
            f"configurado (€{max_value:.2f})"
        )

    max_daily = limits.get("max_daily_spend")
    if max_daily is not None:
        spend = get_daily_spend()
        if spend >= max_daily:
            return f"Gasto diário (€{spend:.2f}) atingiu o máximo configurado (€{max_daily:.2f})"

    return None


def stop_automation(reason: str) -> None:
    """
    Desliga a automação globalmente e envia alerta.
    Idempotente: se já estiver parada, não repete o alerta (evita spam se
    várias ordens do mesmo ciclo violarem o limite).
    """
    try:
        client = get_supabase_client()
        result = client.table("app_parameters").select("id, grid_trading_enabled").execute()
        if not result.data:
            return
        row = result.data[0]
        if not row.get("grid_trading_enabled", True):
            return  # já estava parada

        client.table("app_parameters").update({
            "grid_trading_enabled": False,
            "automation_disabled_reason": reason,
            "updated_at": "now()",
        }).eq("id", row["id"]).execute()

        logger.warning(f"🔴 Automação PARADA: {reason}")
        send_alert_if_enabled(
            "limit_reached",
            subject="🔴 Trading 212 Bot — Automação parada (limite atingido)",
            body=(
                f"A automação foi parada automaticamente.\n\n"
                f"Motivo: {reason}\n\n"
                f"As ordens pendentes na T212 NÃO são canceladas. Revê os limites "
                f"em Config → Trading Limits e reativa manualmente quando quiseres."
            ),
        )
    except Exception as e:
        logger.error(f"Erro ao parar automação por limite: {e}")
