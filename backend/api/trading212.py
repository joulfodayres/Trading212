"""
Cliente da Trading 212 API
Wrapper para as chamadas à API T212 com rate limiting e error handling
"""
import requests
import base64
import time
import logging
from typing import Dict, List, Optional, Any
from config.settings import settings

logger = logging.getLogger(__name__)


class Trading212Client:
    """Cliente HTTP para a Trading 212 API"""

    def __init__(self, api_key: str, api_secret: str, environment: str = "demo"):
        """
        Inicializa o cliente T212

        Args:
            api_key: API Key do T212
            api_secret: API Secret do T212
            environment: 'demo' ou 'live'
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.environment = environment

        # Determina o URL base
        if environment == "demo":
            self.base_url = "https://demo.trading212.com/api/v0"
        else:
            self.base_url = "https://live.trading212.com/api/v0"

        # Session reutilizável
        self.session = requests.Session()
        self._setup_auth()

    def _setup_auth(self):
        """Configura autenticação HTTP Basic"""
        credentials = f"{self.api_key}:{self.api_secret}"
        # O requests vai fazer o base64 encoding automaticamente com auth tuple
        self.session.auth = (self.api_key, self.api_secret)

    def _handle_rate_limit(self, response: requests.Response):
        """Verifica rate limit headers e aguarda se necessário"""
        remaining = response.headers.get("x-ratelimit-remaining")
        reset = response.headers.get("x-ratelimit-reset")

        if remaining and int(remaining) < 1 and reset:
            wait_seconds = int(reset) - time.time()
            if wait_seconds > 0:
                logger.warning(f"Rate limit atingido. Aguardando {wait_seconds}s")
                time.sleep(wait_seconds + 1)

    def get_account_summary(self) -> Dict[str, Any]:
        """GET /equity/account/summary — Retorna saldo da conta"""
        url = f"{self.base_url}/equity/account/summary"
        response = self.session.get(url)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter summary: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def get_positions(self, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """GET /equity/positions — Retorna posições abertas

        Args:
            ticker: Filtrar por ticker específico (ex: AAPL_US_EQ). Opcional.
        """
        url = f"{self.base_url}/equity/positions"
        params = {}
        if ticker:
            params["ticker"] = ticker

        logger.info(f"AutomationEngine | 🌐 GET {url} params={params}")
        response = self.session.get(url, params=params)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter posições: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """GET /equity/orders — Retorna ordens pendentes"""
        url = f"{self.base_url}/equity/orders"
        response = self.session.get(url)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter ordens: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def get_instruments(self, limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        GET /equity/metadata/instruments — Lista de instrumentos disponíveis

        Args:
            limit: Número de resultados (max 50)
            cursor: Para paginação
        """
        url = f"{self.base_url}/equity/metadata/instruments"
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(url, params=params)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter instrumentos: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def place_market_order(self, ticker: str, quantity: float) -> Dict[str, Any]:
        """
        POST /equity/orders/market — Coloca ordem de mercado

        Args:
            ticker: Símbolo do instrumento
            quantity: Quantidade (positiva = buy, negativa = sell)
        """
        url = f"{self.base_url}/equity/orders/market"
        payload = {
            "ticker": ticker,
            "quantity": quantity,
            "assetType": "EQUITY"
        }

        response = self.session.post(url, json=payload)
        self._handle_rate_limit(response)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Erro ao colocar ordem de mercado: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def place_limit_order(self, ticker: str, quantity: float, limit_price: float, time_validity: str = "GOOD_TILL_CANCEL") -> Dict[str, Any]:
        """
        POST /equity/orders/limit — Coloca ordem limitada

        Args:
            ticker: Símbolo do instrumento
            quantity: Quantidade (positiva = buy, negativa = sell) - already rounded by AutomationEngine
            limit_price: Preço limite para a ordem - already rounded by T212Service
            time_validity: "DAY" ou "GOOD_TILL_CANCEL" (default: GOOD_TILL_CANCEL)

        NOTE: Do NOT re-round quantity here. It's already been rounded to ISIN's quantity_precision
        by AutomationEngine and passed through T212Service. Re-rounding would break the
        precision adaptation logic in AutomationEngine._place_order_with_precision_retry()
        """
        url = f"{self.base_url}/equity/orders/limit"

        # Validar time_validity
        if time_validity not in ["DAY", "GOOD_TILL_CANCEL"]:
            raise ValueError(f"time_validity deve ser 'DAY' ou 'GOOD_TILL_CANCEL', recebido: {time_validity}")

        # Use quantity and limit_price as-is - they're already properly rounded by caller
        payload = {
            "ticker": ticker,
            "quantity": quantity,
            "limitPrice": limit_price,
            "timeValidity": time_validity
        }

        response = self.session.post(url, json=payload)
        self._handle_rate_limit(response)

        if response.status_code in [200, 201]:
            logger.info(f"AutomationEngine | ✅ Limit order placed: {ticker} qty={quantity} @ {limit_price} (validity={time_validity})")
            return response.json()
        else:
            # Extract error detail from T212 API response for better error messages
            try:
                error_data = response.json()
                error_detail = error_data.get("detail", f"HTTP {response.status_code}")
            except:
                error_detail = response.text or f"HTTP {response.status_code}"

            logger.error(f"Erro ao colocar ordem limitada: {response.status_code} - {error_detail}")
            # Raise exception with the actual error message from T212 API
            # This allows AutomationEngine to detect "invalid quantity precision X" errors
            raise Exception(error_detail)

    def cancel_order(self, order_id: str) -> bool:
        """DELETE /equity/orders/{id} — Cancela uma ordem

        Returns True if cancellation request accepted (200) OR if the order
        was not found (404) - a 404 means the order is no longer active
        (already filled/cancelled), so there is nothing to cancel.
        Raises Exception on other errors.
        """
        url = f"{self.base_url}/equity/orders/{order_id}"
        logger.info(f"AutomationEngine | 🌐 DELETE {url}")
        response = self.session.delete(url)
        self._handle_rate_limit(response)

        if response.status_code in [200, 204]:
            return True
        elif response.status_code == 404:
            # Order not found - already filled or cancelled. Not a real error.
            logger.warning(f"AutomationEngine | ⚠️ Order {order_id} not found (404) - already filled/cancelled, nothing to cancel")
            return True
        else:
            error_text = response.text or f"HTTP {response.status_code}"
            logger.error(f"Erro ao cancelar ordem {order_id}: {response.status_code} - {error_text}")
            raise Exception(f"Erro T212 API ao cancelar ordem: {response.status_code} - {error_text}")

    def get_order_history(self, limit: int = 50, cursor: Optional[str] = None, ticker: Optional[str] = None) -> Dict[str, Any]:
        """GET /equity/history/orders — Histórico de trades

        Args:
            limit: Número de resultados (max 50)
            cursor: Para paginação
            ticker: Filtrar por ticker específico (ex: AAPL_US_EQ)
        """
        url = f"{self.base_url}/equity/history/orders"
        params = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if ticker:
            params["ticker"] = ticker

        response = self.session.get(url, params=params)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter histórico: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")
