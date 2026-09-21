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
        self, ticker: str, quantity: float, limit_price: float, time_validity: str = "GOOD_TILL_CANCEL"
    ) -> Optional[Dict[str, Any]]:
        """
        Place a BUY limit order on T212.

        Args:
            ticker: Ticker symbol (ex: AAPL_US_EQ)
            quantity: Positive quantity (already rounded by AutomationEngine to ISIN's quantity_precision)
            limit_price: Limit price (sent as-is, no rounding)
            time_validity: "DAY" ou "GOOD_TILL_CANCEL" (default: GOOD_TILL_CANCEL)

        Returns:
            Order response from T212 API or None on error

        NOTE: Both quantity and limit_price are passed as-is from AutomationEngine.
        No rounding happens here - values are pre-formatted by the caller.
        """
        try:
            # Both quantity and limit_price are already properly formatted by AutomationEngine
            # Pass them as-is without any modifications

            self.logger.info(
                f"AutomationEngine | 🔄 Placing BUY limit order: {ticker} qty={quantity} @ {limit_price} ({time_validity})"
            )

            response = self.client.place_limit_order(
                ticker=ticker, quantity=quantity, limit_price=limit_price, time_validity=time_validity
            )

            if response:
                order_id = response.get('id')
                self.logger.info(
                    f"AutomationEngine | ✅ BUY order placed: {ticker} qty={quantity} @ {limit_price} (Order ID={order_id}, validity={time_validity})"
                )
            return response

        except Exception as e:
            self.logger.error(
                f"AutomationEngine | ❌ Error placing BUY order: {ticker} - {str(e)}"
            )
            # Re-raise the exception so AutomationEngine's precision retry logic can handle it
            raise

    async def place_sell_limit_order(
        self, ticker: str, quantity: float, limit_price: float, time_validity: str = "GOOD_TILL_CANCEL"
    ) -> Optional[Dict[str, Any]]:
        """
        Place a SELL limit order on T212.

        Args:
            ticker: Ticker symbol
            quantity: Positive quantity to sell (already rounded by AutomationEngine to ISIN's quantity_precision)
            limit_price: Limit price (sent as-is, no rounding)
            time_validity: "DAY" ou "GOOD_TILL_CANCEL" (default: GOOD_TILL_CANCEL)

        Returns:
            Order response from T212 API or None on error

        NOTE: Both quantity and limit_price are passed as-is from AutomationEngine.
        No rounding happens here - values are pre-formatted by the caller.
        """
        try:
            # Both quantity and limit_price are already properly formatted by AutomationEngine
            # Ensure quantity is negative for SELL
            sell_quantity = -abs(quantity) if quantity > 0 else quantity

            self.logger.info(
                f"AutomationEngine | 🔄 Placing SELL limit order: {ticker} qty={sell_quantity} @ {limit_price} ({time_validity})"
            )

            response = self.client.place_limit_order(
                ticker=ticker, quantity=sell_quantity, limit_price=limit_price, time_validity=time_validity
            )

            if response:
                order_id = response.get('id')
                self.logger.info(
                    f"AutomationEngine | ✅ SELL order placed: {ticker} qty={sell_quantity} @ {limit_price} (Order ID={order_id}, validity={time_validity})"
                )
            return response

        except Exception as e:
            self.logger.error(
                f"AutomationEngine | ❌ Error placing SELL order: {ticker} - {str(e)}"
            )
            # Re-raise the exception so AutomationEngine's precision retry logic can handle it
            raise

    async def get_pending_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get status of a pending order from T212.

        Args:
            order_id: T212 order ID (integer)

        Returns:
            Order details from T212 or None if not found/error
        """
        try:
            self.logger.debug(f"AutomationEngine | 📖 Fetching order {order_id} from T212...")

            # Get all pending orders and find the one matching order_id
            orders = self.client.get_pending_orders()
            for order in orders:
                if order.get('id') == order_id:
                    self.logger.debug(f"AutomationEngine | ✅ Order {order_id} found - Status: {order.get('status')}")
                    return order

            self.logger.debug(f"AutomationEngine | ℹ️ Order {order_id} not found in pending orders")
            return None

        except Exception as e:
            self.logger.debug(f"AutomationEngine | ⚠️ Error fetching order {order_id}: {e}")
            return None

    async def get_historical_order(self, order_id: int, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Search for an order in T212 historical orders (executed/closed orders).

        Used when an order is no longer in pending orders - it may have been
        filled/executed. Calls GET /equity/history/orders?cursor=0&ticker=<ticker>
        and searches items[].order for the matching order_id.

        Args:
            order_id: T212 order ID (integer)
            ticker: Ticker symbol to filter history by (e.g., NQSEd_EQ)

        Returns:
            The matching order dict (items[].order) from history, or None if not found/error
        """
        try:
            self.logger.debug(
                f"AutomationEngine | 📖 Searching historical orders for order {order_id} (ticker={ticker})..."
            )

            # GET /equity/history/orders?cursor=0&ticker=<ticker>
            history = self.client.get_order_history(cursor="0", ticker=ticker)
            items = history.get("items", []) if history else []

            for item in items:
                order = item.get("order", {})
                if order.get("id") == order_id:
                    self.logger.info(
                        f"AutomationEngine | ✅ Order {order_id} found in history - Status: {order.get('status')}"
                    )
                    return order

            self.logger.debug(
                f"AutomationEngine | ℹ️ Order {order_id} not found in historical orders for {ticker}"
            )
            return None

        except Exception as e:
            self.logger.warning(
                f"AutomationEngine | ⚠️ Error searching historical order {order_id} ({ticker}): {e}"
            )
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
            self.logger.info(f"AutomationEngine | 🔄 Cancelling order {order_id}...")
            self.client.cancel_order(str(order_id))
            self.logger.info(f"AutomationEngine | ✅ Order {order_id} cancelled successfully")
            return True

        except Exception as e:
            self.logger.error(f"AutomationEngine | ❌ Error cancelling order {order_id}: {str(e)}")
            return False

    async def get_position(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get current position details from T212.

        Args:
            ticker: Ticker symbol

        Returns:
            Position details or None on error

        NOTE: The T212 Position schema exposes the ticker inside
        `position.instrument.ticker` (NOT at the top level). We also pass
        the `ticker` query param so the API filters server-side.
        """
        try:
            self.logger.info(f"AutomationEngine | 📖 Fetching position for {ticker} (GET /equity/positions?ticker={ticker})...")
            response = self.client.get_positions(ticker=ticker)

            self.logger.debug(f"AutomationEngine | 📊 Positions API returned {len(response) if response else 0} position(s) for {ticker}")

            if response and len(response) > 0:
                # Search for matching ticker. The ticker is nested under instrument.ticker,
                # but also check top-level as a fallback for API variations.
                for position in response:
                    pos_ticker = (position.get("instrument") or {}).get("ticker") or position.get("ticker")
                    if pos_ticker == ticker:
                        self.logger.info(f"AutomationEngine | ✅ Position found for {ticker} (currentPrice={position.get('currentPrice')})")
                        return position

                # If server-side filtered by ticker and returned exactly one, use it
                if len(response) == 1:
                    only = response[0]
                    self.logger.info(f"AutomationEngine | ✅ Position (single result) for {ticker} (currentPrice={only.get('currentPrice')})")
                    return only

                self.logger.warning(
                    f"AutomationEngine | ⚠️ {len(response)} position(s) returned but none matched ticker '{ticker}'. "
                    f"Tickers seen: {[ (p.get('instrument') or {}).get('ticker') or p.get('ticker') for p in response ]}"
                )

            self.logger.info(f"AutomationEngine | ℹ️ No position found for {ticker}")
            return None

        except Exception as e:
            self.logger.error(f"AutomationEngine | ❌ Error fetching position {ticker}: {str(e)}", exc_info=True)
            return None

    async def get_account_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get account summary from T212.

        Returns:
            Account details or None on error
        """
        try:
            self.logger.debug(f"AutomationEngine | 📖 Fetching account summary...")
            response = self.client.get_account_summary()
            self.logger.debug(f"AutomationEngine | ✅ Account summary retrieved")
            return response

        except Exception as e:
            self.logger.error(f"AutomationEngine | ❌ Error fetching account summary: {str(e)}")
            return None
