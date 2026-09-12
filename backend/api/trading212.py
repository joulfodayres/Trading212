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

    def get_positions(self) -> List[Dict[str, Any]]:
        """GET /equity/positions — Retorna posições abertas"""
        url = f"{self.base_url}/equity/positions"
        response = self.session.get(url)
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
            logger.error(f"Erro ao colocar ordem: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def cancel_order(self, order_id: str) -> bool:
        """DELETE /equity/orders/{id} — Cancela uma ordem"""
        url = f"{self.base_url}/equity/orders/{order_id}"
        response = self.session.delete(url)
        self._handle_rate_limit(response)

        if response.status_code in [200, 204]:
            return True
        else:
            logger.error(f"Erro ao cancelar ordem: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")

    def get_order_history(self, limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        """GET /equity/history/orders — Histórico de trades"""
        url = f"{self.base_url}/equity/history/orders"
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(url, params=params)
        self._handle_rate_limit(response)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter histórico: {response.status_code} - {response.text}")
            raise Exception(f"Erro T212 API: {response.status_code}")
