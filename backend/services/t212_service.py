"""
T212Service - Wrapper around Trading 212 API for automation engine
Phase 4: Grid Trading Automation
"""

import logging
from typing import Optional, Dict, Any
from api.trading212 import Trading212Client

logger = logging.getLogger(__name__)


class T212Service:
    """
    Provides high-level methods for T212 API interactions.
    Wraps Trading212Client with error handling and logging.
    """

    def __init__(self, t212_client: Trading212Client):
        """
        Initialize T212Service

        Args:
            t212_client: Trading212Client instance (from api/trading212.py)
        """
        self.client = t212_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def place_buy_limit_order(
        self, ticker: str, quantity: float, limit_price: float
    ) -> Optional[Dict[str, Any]]:
        """
        Place a BUY limit order on T212.

        Args:
            ticker: Ticker symbol (ex: AAPL_US_EQ)
            quantity: Positive quantity (ex: 6.72)
            limit_price: Limit price (ex: 148.99)

        Returns:
            Order response from T212 API or None on error
        """
        try:
            self.logger.debug(
                f"Placing BUY limit order: {ticker} qty={quantity} @ {limit_price}"
            )

            response = self.client.place_limit_order(
                ticker=ticker, quantity=quantity, limitPrice=limit_price
            )

            self.logger.info(
                f"✅ BUY order placed: {ticker} id={response.get('id')}"
            )
            return response

        except Exception as e:
            self.logger.error(
                f"❌ Error placing BUY order: {ticker} - {e}", exc_info=True
            )
            return None

    async def place_sell_limit_order(
        self, ticker: str, quantity: float, limit_price: float
    ) -> Optional[Dict[str, Any]]:
        """
        Place a SELL limit order on T212.

        Args:
            ticker: Ticker symbol
            quantity: Negative quantity (ex: -6.72 to sell 6.72)
            limit_price: Limit price

        Returns:
            Order response from T212 API or None on error
        """
        try:
            self.logger.debug(
                f"Placing SELL limit order: {ticker} qty={quantity} @ {limit_price}"
            )

            # Ensure quantity is negative for SELL
            sell_quantity = -abs(quantity) if quantity > 0 else quantity

            response = self.client.place_limit_order(
                ticker=ticker, quantity=sell_quantity, limitPrice=limit_price
            )

            self.logger.info(
                f"✅ SELL order placed: {ticker} id={response.get('id')}"
            )
            return response

        except Exception as e:
            self.logger.error(
                f"❌ Error placing SELL order: {ticker} - {e}", exc_info=True
            )
            return None

    async def get_pending_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get status of a pending order from T212.

        Args:
            order_id: T212 order ID (integer)

        Returns:
            Order details from T212 or None if not found/error
        """
        try:
            response = self.client.get_order_by_id(order_id)
            return response

        except Exception as e:
            self.logger.debug(f"Order {order_id} not found or error: {e}")
            return None

    async def cancel_order(self, order_id: int) -> bool:
        """
        Cancel a pending order on T212.

        Args:
            order_id: T212 order ID

        Returns:
            True if successful, False on error
        """
        try:
            self.client.cancel_order(order_id)
            self.logger.info(f"✅ Order {order_id} cancelled")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error cancelling order {order_id}: {e}")
            return False

    async def get_position(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get current position details from T212.

        Args:
            ticker: Ticker symbol

        Returns:
            Position details or None on error
        """
        try:
            response = self.client.get_positions(ticker=ticker)

            if response and len(response) > 0:
                return response[0]  # Return first match
            else:
                self.logger.debug(f"No position found for {ticker}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Error fetching position {ticker}: {e}")
            return None

    async def get_account_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get account summary from T212.

        Returns:
            Account details or None on error
        """
        try:
            response = self.client.get_account_summary()
            return response

        except Exception as e:
            self.logger.error(f"❌ Error fetching account summary: {e}")
            return None
