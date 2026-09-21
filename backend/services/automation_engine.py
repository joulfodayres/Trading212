"""
AutomationEngine - Grid Trading Automation Logic (3 Phases)
Phase 4: Grid Trading Automation
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from db.supabase_client import get_db
from services.t212_service import T212Service

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Core automation engine for grid trading strategy.

    Three phases per cycle:
    1. Initial Setup - Create first BUY/SELL order pairs
    2. Monitor Orders - Poll T212 for order status changes
    3. Handle Fills - Rebalance when orders execute
    """

    def __init__(self, db, t212_service: T212Service):
        """
        Initialize automation engine

        Args:
            db: Supabase DB instance
            t212_service: T212Service instance for API calls
        """
        self.db = db
        self.t212_service = t212_service
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Metrics
        self.cycle_count = 0
        self.last_cycle_start: Optional[datetime] = None
        self.last_cycle_duration: Optional[float] = None

    async def run_cycle(self):
        """
        Main cycle function - called every 15 seconds by scheduler.
        Executes 3 phases of automation.

        Checks grid_trading_enabled flag before running.
        """
        self.cycle_count += 1
        cycle_start = datetime.utcnow()
        self.last_cycle_start = cycle_start

        self.logger.info(f"🔄 AutomationEngine | Ciclo #{self.cycle_count} iniciado às {cycle_start.isoformat()}")

        try:
            # Check if global automation is enabled
            self.logger.debug(f"AutomationEngine | ⏳ Verificando se automação está ativada...")
            self._log_db_action("⏳ Verificando status global de automação...")
            grid_trading_enabled = self._check_grid_trading_enabled()
            if not grid_trading_enabled:
                self.logger.info(f"AutomationEngine | ⏸️ Ciclo #{self.cycle_count} IGNORADO: Grid trading está desativado globalmente")
                self._log_db_action("⏸️ Grid trading desativado, ciclo ignorado")
                return

            self.logger.info(f"AutomationEngine | ✅ Automação ativada, iniciando ciclo de 3 fases")
            self._log_db_action("✅ Automação ativada, iniciando ciclo de 3 fases")

            # PHASE 1: Setup initial BUY/SELL pairs
            self.logger.info(f"AutomationEngine | 📋 FASE 1: Iniciando Setup Inicial...")
            await self._phase_1_initial_setup()
            self.logger.info(f"AutomationEngine | ✅ FASE 1: Setup Inicial completo")

            # PHASE 2: Monitor Watch orders
            self.logger.info(f"AutomationEngine | 📋 FASE 2: Iniciando Monitoramento de Ordens...")
            await self._phase_2_monitor_orders()
            self.logger.info(f"AutomationEngine | ✅ FASE 2: Monitoramento de Ordens completo")

            # PHASE 3: Handle order fills and rebalance
            self.logger.info(f"AutomationEngine | 📋 FASE 3: Iniciando Processamento de Fills...")
            await self._phase_3_handle_fills()
            self.logger.info(f"AutomationEngine | ✅ FASE 3: Processamento de Fills completo")

            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.last_cycle_duration = cycle_duration
            self.logger.info(f"✅ AutomationEngine | Ciclo #{self.cycle_count} completo com sucesso em {cycle_duration:.2f}s")
            self._log_db_action(f"✅ Ciclo #{self.cycle_count} completo com sucesso", {"duration_seconds": cycle_duration})

        except Exception as e:
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.last_cycle_duration = cycle_duration
            self.logger.error(
                f"❌ AutomationEngine | ERRO no ciclo #{self.cycle_count} após {cycle_duration:.2f}s: {str(e)}",
                exc_info=True,
            )
            self._log_db_action(f"❌ Erro fatal no ciclo: {str(e)}", {"cycle": self.cycle_count, "error": str(e)})
            # Continue - don't crash, next cycle will retry

    # =========================================================================
    # PHASE 1: INITIAL SETUP
    # =========================================================================

    async def _phase_1_initial_setup(self):
        """
        Phase 1: Create initial BUY/SELL order pairs for ISINs with initial_trade=TRUE.

        For each ISIN:
        1. Load strategy and strategy_parameters (by trades_balance position)
        2. Calculate BUY price: current_price * (1 + param1/100)
        3. Calculate SELL price: current_price * (1 + param2/100)
        4. Place BUY limit order (positive quantity)
        5. Place SELL limit order (negative quantity)
        6. Save both orders with related_order_id linking them
        7. Set initial_trade=FALSE
        """
        try:
            # Query ISINs ready for automation setup
            self._log_db_action("📖 Carregando ISINs com initial_trade=TRUE...")
            db = get_db()
            result = db.client.table("isins").select("*").eq("initial_trade", True).eq("automation_enabled", True).execute()
            isins = result.data or []

            if not isins:
                self.logger.debug("Nenhum ISIN com initial_trade=TRUE encontrado")
                self._log_db_action("ℹ️ Nenhum ISIN com initial_trade=TRUE encontrado")
                return

            self.logger.info(f"Fase 1: {len(isins)} ISINs para setup inicial")
            self._log_db_action(f"✅ Carregados {len(isins)} ISINs para setup inicial", {"count": len(isins)})

            for idx, isin_data in enumerate(isins, 1):
                self.logger.info(f"AutomationEngine | FASE 1 | 🔄 Processando ISIN {idx}/{len(isins)}: {isin_data.get('ticker', 'N/A')}")
                await self._phase_1_setup_isin(isin_data)

        except Exception as e:
            self.logger.error(f"AutomationEngine | FASE 1 | ❌ Erro: {str(e)}", exc_info=True)
            self._log_db_action(f"❌ Erro na Fase 1: {str(e)}", {"error": str(e)})

    async def _phase_1_setup_isin(self, isin_data: Dict):
        """
        Setup initial orders for a single ISIN.
        Loads quantity_precision from ISIN and uses it for rounding.
        If T212 API returns precision error, updates precision and retries.
        """
        try:
            db = get_db()
            ticker = isin_data.get("ticker")
            current_price = isin_data.get("current_price")
            isin_id = isin_data.get("id")
            quantity_precision = isin_data.get("quantity_precision", 3)  # Load precision from ISIN

            self.logger.info(f"AutomationEngine | FASE 1 | 📝 Setup para {ticker} @ €{current_price} (ISIN ID: {isin_id}, precision: {quantity_precision})")

            # Load strategy
            strategy_id = isin_data.get("strategy_id")
            self.logger.debug(f"AutomationEngine | FASE 1 | 📖 Carregando estratégia ID: {strategy_id}")
            strategy_result = db.client.table("strategies").select("*").eq("id", strategy_id).execute()
            strategy = strategy_result.data[0] if strategy_result.data else None
            if not strategy:
                self.logger.warning(f"AutomationEngine | FASE 1 | ⚠️ Strategy não encontrada para {ticker} (strategy_id={strategy_id})")
                return

            strategy_name = strategy.get("strategy_name", "UNKNOWN")
            self.logger.info(f"AutomationEngine | FASE 1 | ✅ Estratégia carregada: {strategy_name}")

            # Load strategy parameters for current position (trades_balance)
            trades_balance = isin_data.get("trades_balance", 0)
            self.logger.debug(f"AutomationEngine | FASE 1 | 📖 Carregando parâmetros para trades_balance={trades_balance}")
            params = self._get_strategy_parameters(strategy_id, trades_balance)

            if not params:
                self.logger.warning(
                    f"Parâmetros não encontrados para {ticker} pos={trades_balance}"
                )
                return

            # [NEW] Calculate investment with adjustment based on param2/param3
            initial_investment = strategy.get("initial_investment", 0)
            param2 = params.get("param2", 0)
            param3 = params.get("param3", 0)
            buy_investment = initial_investment * (1 + param2 / 100)
            sell_investment = initial_investment * (1 + param3 / 100)

            # Calculate prices
            param1 = params.get("param1", 0)
            buy_price = current_price * (1 + param1 / 100)
            sell_price = current_price * (1 + param2 / 100)

            # [NEW] Calculate quantities using investment (not just initial_investment)
            buy_quantity = buy_investment / buy_price if buy_price > 0 else 0
            sell_quantity = sell_investment / sell_price if sell_price > 0 else 0

            self.logger.debug(
                f"BUY @ {buy_price:.2f} qty={buy_quantity:.2f}, SELL @ {sell_price:.2f} qty={sell_quantity:.2f}"
            )

            # Round quantities to ISIN's precision
            buy_quantity_rounded = round(buy_quantity, quantity_precision)
            sell_quantity_rounded = round(sell_quantity, quantity_precision)
            # Prices are NOT rounded - sent as-is with full precision

            self.logger.debug(
                f"After rounding (precision={quantity_precision}): BUY qty={buy_quantity_rounded}, SELL qty={sell_quantity_rounded}"
            )

            # Place BUY order
            buy_response = await self._place_order_with_precision_retry(
                order_type="BUY",
                ticker=ticker,
                quantity=buy_quantity_rounded,
                limit_price=buy_price,
                isin_id=isin_id,
                initial_precision=quantity_precision
            )
            if not buy_response:
                self.logger.error(f"Falha ao colocar BUY order para {ticker}")
                return

            # Place SELL order
            sell_response = await self._place_order_with_precision_retry(
                order_type="SELL",
                ticker=ticker,
                quantity=sell_quantity_rounded,
                limit_price=sell_price,
                isin_id=isin_id,
                initial_precision=quantity_precision
            )
            if not sell_response:
                self.logger.error(f"Falha ao colocar SELL order para {ticker}")
                # TODO: Cancela BUY order? (Por agora não, Phase 5)
                return

            # Save BUY order to DB
            buy_order_id = buy_response.get("id")
            sell_order_id = sell_response.get("id")

            buy_order_data = self._create_order_from_response(
                isin_id=isin_data.get("id"),
                api_response=buy_response,
                automation_status="W",
                related_order_id=None,
            )

            sell_order_data = self._create_order_from_response(
                isin_id=isin_data.get("id"),
                api_response=sell_response,
                automation_status="W",
                related_order_id=None,
            )

            # Link orders together
            buy_order_data["related_order_id"] = sell_order_data["id"]
            sell_order_data["related_order_id"] = buy_order_data["id"]

            # Save to DB
            db.client.table("orders").insert([buy_order_data, sell_order_data]).execute()

            # Mark ISIN as setup done
            db.client.table("isins").update({"initial_trade": False}).eq("id", isin_data.get("id")).execute()

            self.logger.info(
                f"✅ {ticker}: Ordens criadas (BUY id={buy_order_id}, SELL id={sell_order_id})"
            )

        except Exception as e:
            self.logger.error(f"❌ Erro setup {isin_data.get('ticker', 'unknown')}: {e}", exc_info=True)

    # =========================================================================
    # PHASE 2: MONITOR ORDERS
    # =========================================================================

    async def _phase_2_monitor_orders(self):
        """
        Phase 2: Poll T212 for status of all 'W' (Watch) orders.
        Update local DB with latest status from T212.
        """
        try:
            # Query orders with automation_status='W'
            self.logger.info(f"AutomationEngine | FASE 2 | 📖 Carregando ordens em status WATCH...")
            self._log_db_action("📖 Carregando ordens em status WATCH da base de dados...")
            db = get_db()
            result = db.client.table("orders").select("*").eq("automation_status", "W").execute()
            watch_orders = result.data or []

            if not watch_orders:
                self.logger.info(f"AutomationEngine | FASE 2 | ℹ️ Nenhuma ordem em status WATCH para monitorar")
                self._log_db_action("ℹ️ Nenhuma ordem em status WATCH encontrada")
                return

            self.logger.info(f"AutomationEngine | FASE 2 | ✅ {len(watch_orders)} ordem(ns) carregada(s)")
            self._log_db_action(f"✅ Carregadas {len(watch_orders)} ordens em status WATCH", {"count": len(watch_orders)})

            for idx, order in enumerate(watch_orders, 1):
                ticker = order.get("ticker", "N/A")
                order_id = order.get("t212_order_id")
                self.logger.debug(f"AutomationEngine | FASE 2 | 🔄 Monitorando ordem {idx}/{len(watch_orders)}: {ticker} (Order ID: {order_id})")
                await self._phase_2_monitor_order(order)

        except Exception as e:
            self.logger.error(f"AutomationEngine | FASE 2 | ❌ Erro: {str(e)}", exc_info=True)
            self._log_db_action(f"❌ Erro na Fase 2: {str(e)}", {"error": str(e)})

    async def _phase_2_monitor_order(self, order_data: Dict):
        """
        Monitor a single order - poll T212 for status.
        """
        try:
            db = get_db()
            order_id = order_data.get("t212_order_id")
            ticker = order_data.get("ticker", "N/A")

            self.logger.debug(f"AutomationEngine | FASE 2 | 🔍 Consultando T212 API para ordem {order_id}...")

            # Poll T212 API
            t212_order = await self.t212_service.get_pending_order(order_id)

            if not t212_order:
                self.logger.info(f"AutomationEngine | FASE 2 | ℹ️ Ordem {order_id} ({ticker}) não encontrada em T212 - pode estar FILLED")
                return

            # Update order status from T212 response
            current_status = t212_order.get("status", "UNKNOWN")
            filled_qty = t212_order.get("filledQuantity", 0)
            self.logger.debug(f"AutomationEngine | FASE 2 | 📊 Status T212: {current_status}, Filled: {filled_qty}")

            update_data = {
                "status": current_status,
                "filled_quantity": filled_qty,
                "synced_at": datetime.utcnow().isoformat()
            }

            # If FILLED, mark as 'E' (Executed)
            if current_status == "FILLED":
                update_data["automation_status"] = "E"
                self.logger.info(f"AutomationEngine | FASE 2 | ✅ Ordem {order_id} ({ticker}) PREENCHIDA - marcando como EXECUTADA")
                self._log_db_action(f"✅ Ordem FILLED: {ticker} (Order ID: {order_id})", {"order_id": order_id, "ticker": ticker})

            db.client.table("orders").update(update_data).eq("id", order_data.get("id")).execute()

        except Exception as e:
            self.logger.error(
                f"❌ Erro monitorando ordem {order_data.get('t212_order_id')}: {e}", exc_info=True
            )

    # =========================================================================
    # PHASE 3: HANDLE FILLS
    # =========================================================================

    async def _phase_3_handle_fills(self):
        """
        Phase 3: Process filled orders and rebalance grid.

        For each FILLED order:
        1. Update ISIN with position data
        2. Adjust trades_balance (±1)
        3. Cancel related order
        4. Load new strategy parameters
        5. Place new BUY/SELL pair
        """
        try:
            # Query FILLED orders (status='FILLED', automation_status='E')
            self.logger.info(f"AutomationEngine | FASE 3 | 📖 Carregando ordens FILLED para rebalanceamento...")
            self._log_db_action("📖 Carregando ordens FILLED para rebalanceamento...")
            db = get_db()
            result = db.client.table("orders").select("*").eq("status", "FILLED").eq("automation_status", "E").execute()
            filled_orders = result.data or []

            if not filled_orders:
                self.logger.info(f"AutomationEngine | FASE 3 | ℹ️ Nenhuma ordem FILLED para processar")
                self._log_db_action("ℹ️ Nenhuma ordem FILLED encontrada para rebalanceamento")
                return

            self.logger.info(f"AutomationEngine | FASE 3 | ✅ {len(filled_orders)} ordem(ns) FILLED carregada(s)")
            self._log_db_action(f"✅ Carregadas {len(filled_orders)} ordens FILLED", {"count": len(filled_orders)})

            for idx, order in enumerate(filled_orders, 1):
                ticker = order.get("ticker", "N/A")
                side = order.get("side", "N/A")
                self.logger.debug(f"AutomationEngine | FASE 3 | 🔄 Processando ordem {idx}/{len(filled_orders)}: {ticker} ({side})")
                await self._phase_3_handle_filled_order(order)

        except Exception as e:
            self.logger.error(f"AutomationEngine | FASE 3 | ❌ Erro: {str(e)}", exc_info=True)
            self._log_db_action(f"❌ Erro na Fase 3: {str(e)}", {"error": str(e)})

    async def _phase_3_handle_filled_order(self, order_data: Dict):
        """
        Handle a single filled order.
        """
        try:
            db = get_db()
            order_id = order_data.get("t212_order_id")
            side = order_data.get("side", "N/A")
            ticker = order_data.get("ticker", "N/A")

            self.logger.info(f"AutomationEngine | FASE 3 | 📝 Processando fill: {ticker} ({side}) - Order ID: {order_id}")

            # Load ISIN
            self.logger.debug(f"AutomationEngine | FASE 3 | 📖 Carregando dados ISIN...")
            isin_result = db.client.table("isins").select("*").eq("id", order_data.get("isin_id")).execute()
            isin = isin_result.data[0] if isin_result.data else None
            if not isin:
                self.logger.error(f"AutomationEngine | FASE 3 | ❌ ISIN não encontrado para ordem {order_id}")
                return

            ticker = isin.get("ticker")
            self.logger.info(f"AutomationEngine | FASE 3 | ✅ ISIN carregado: {ticker} - Atualizando posição...")

            # Get latest position from T212
            position = await self.t212_service.get_position(ticker)
            if position:
                # Update ISIN with position data
                update_isin = {
                    "quantity": position.get("quantity", isin.get("quantity")),
                    "current_price": position.get("currentPrice", isin.get("current_price")),
                    "average_price_paid": position.get("averagePricePaid", isin.get("average_price_paid")),
                    "quantity_available_for_trading": position.get("quantityAvailableForTrading", isin.get("quantity_available_for_trading")),
                }

                # Wallet impact
                wi = position.get("walletImpact", {})
                update_isin["wi_current_value"] = wi.get("currentValue", isin.get("wi_current_value"))
                update_isin["wi_total_cost"] = wi.get("totalCost", isin.get("wi_total_cost"))
                update_isin["wi_unrealized_profit_loss"] = wi.get("unrealizedProfitLoss", isin.get("wi_unrealized_profit_loss"))

                # Adjust trades_balance based on order side
                trades_balance = isin.get("trades_balance", 0)
                if order_data.get("side") == "BUY":
                    update_isin["trades_balance"] = trades_balance - 1
                    self.logger.debug(f"BUY fill: trades_balance {trades_balance} → {trades_balance - 1}")
                elif order_data.get("side") == "SELL":
                    update_isin["trades_balance"] = trades_balance + 1
                    self.logger.debug(f"SELL fill: trades_balance {trades_balance} → {trades_balance + 1}")

                # Save position update
                db.client.table("isins").update(update_isin).eq("id", isin.get("id")).execute()

            # Cancel related order
            if order_data.get("related_order_id"):
                related_result = db.client.table("orders").select("*").eq("id", order_data.get("related_order_id")).execute()
                related_order = related_result.data[0] if related_result.data else None
                if related_order and related_order.get("t212_order_id"):
                    cancel_success = await self.t212_service.cancel_order(related_order.get("t212_order_id"))
                    if cancel_success:
                        db.client.table("orders").update({
                            "automation_status": "C",
                            "status": "CANCELLED"
                        }).eq("id", related_order.get("id")).execute()

            # Place new BUY/SELL pair at new grid level
            await self._phase_3_place_new_pair(isin)

        except Exception as e:
            self.logger.error(f"❌ Erro processando filled order: {e}", exc_info=True)

    async def _phase_3_place_new_pair(self, isin_data: Dict):
        """
        Place new BUY/SELL pair at new grid level (after fill).
        Loads quantity_precision from ISIN and uses it for rounding.
        If T212 API returns precision error, updates precision and retries.
        """
        try:
            db = get_db()
            quantity_precision = isin_data.get("quantity_precision", 3)  # Load precision from ISIN

            # Load strategy
            strategy_id = isin_data.get("strategy_id")
            strategy_result = db.client.table("strategies").select("*").eq("id", strategy_id).execute()
            strategy = strategy_result.data[0] if strategy_result.data else None
            if not strategy:
                self.logger.warning(f"Strategy não encontrada para {isin_data.get('ticker')}")
                return

            # Load new parameters for new trades_balance position
            trades_balance = isin_data.get("trades_balance", 0)
            params = self._get_strategy_parameters(strategy_id, trades_balance)

            if not params:
                self.logger.warning(
                    f"Parâmetros não encontrados para {isin_data.get('ticker')} pos={trades_balance}"
                )
                return

            # [NEW] Recalculate investment with new position
            initial_investment = strategy.get("initial_investment", 0)
            param2 = params.get("param2", 0)
            param3 = params.get("param3", 0)
            new_buy_investment = initial_investment * (1 + param2 / 100)
            new_sell_investment = initial_investment * (1 + param3 / 100)

            # Calculate new prices with new position
            current_price = isin_data.get("current_price")
            param1 = params.get("param1", 0)
            new_buy_price = current_price * (1 + param1 / 100)
            new_sell_price = current_price * (1 + param2 / 100)

            # [NEW] Calculate quantities with new investment
            new_buy_quantity = new_buy_investment / new_buy_price if new_buy_price > 0 else 0
            new_sell_quantity = new_sell_investment / new_sell_price if new_sell_price > 0 else 0

            # Round quantities to ISIN's precision
            new_buy_quantity_rounded = round(new_buy_quantity, quantity_precision)
            new_sell_quantity_rounded = round(new_sell_quantity, quantity_precision)
            # Prices are NOT rounded - sent as-is with full precision

            self.logger.debug(
                f"Novo pair: BUY @ {new_buy_price:.2f} qty={new_buy_quantity_rounded:.2f}, SELL @ {new_sell_price:.2f} qty={new_sell_quantity_rounded:.2f}"
            )

            # Place BUY order
            buy_response = await self._place_order_with_precision_retry(
                order_type="BUY",
                ticker=isin_data.get("ticker"),
                quantity=new_buy_quantity_rounded,
                limit_price=new_buy_price,
                isin_id=isin_data.get("id"),
                initial_precision=quantity_precision
            )
            if not buy_response:
                self.logger.error(f"Falha ao colocar novo BUY order para {isin_data.get('ticker')}")
                return

            # Place SELL order
            sell_response = await self._place_order_with_precision_retry(
                order_type="SELL",
                ticker=isin_data.get("ticker"),
                quantity=new_sell_quantity_rounded,
                limit_price=new_sell_price,
                isin_id=isin_data.get("id"),
                initial_precision=quantity_precision
            )
            if not sell_response:
                self.logger.error(f"Falha ao colocar novo SELL order para {isin_data.get('ticker')}")
                return

            # Create order records
            buy_order = self._create_order_from_response(
                isin_id=isin_data.get("id"),
                api_response=buy_response,
                automation_status="W",
                related_order_id=None,
            )

            sell_order = self._create_order_from_response(
                isin_id=isin_data.get("id"),
                api_response=sell_response,
                automation_status="W",
                related_order_id=None,
            )

            # Link orders
            buy_order["related_order_id"] = sell_order.get("id")
            sell_order["related_order_id"] = buy_order.get("id")

            db.client.table("orders").insert([buy_order, sell_order]).execute()

            self.logger.info(
                f"✅ Novo pair para {isin_data.get('ticker')} @ level {trades_balance} (BUY id={buy_response.get('id')}, SELL id={sell_response.get('id')})"
            )

        except Exception as e:
            self.logger.error(f"❌ Erro criando novo pair: {e}", exc_info=True)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _check_grid_trading_enabled(self) -> bool:
        """
        Verifica se grid_trading_enabled está ativo em app_parameters.
        """
        try:
            db = get_db()
            result = db.client.table("app_parameters").select("grid_trading_enabled").execute()
            if result.data:
                return result.data[0].get("grid_trading_enabled", True)
            return True
        except Exception as e:
            self.logger.warning(f"Erro verificando grid_trading_enabled: {e}, assumindo True")
            return True

    def _get_strategy_parameters(self, strategy_id: str, trades_balance: int) -> Optional[Dict]:
        """
        Buscar strategy_parameters com fallback inteligente.

        Lógica:
        1. Tenta buscar exata: pos = trades_balance
        2. Se não encontrar:
           - Se trades_balance positivo: busca máximo pos <= trades_balance
           - Se trades_balance negativo: busca mínimo pos >= trades_balance

        Significado: A última 'pos' colocada (extremo) é usada mesmo que trades_balance ultrapasse.
        """
        try:
            db = get_db()
            # Step 1: Tentar exato
            result = db.client.table("strategy_parameters").select("*").eq("strategy_id", strategy_id).eq("pos", str(trades_balance)).execute()

            if result.data:
                self.logger.debug(f"Strategy parameters encontrados exato: pos={trades_balance}")
                return result.data[0]

            # Step 2: Fallback baseado na direção
            all_result = db.client.table("strategy_parameters").select("*").eq("strategy_id", strategy_id).execute()
            all_params = all_result.data or []

            if not all_params:
                self.logger.warning(f"Nenhuns strategy_parameters encontrados para strategy={strategy_id}")
                return None

            # Converter pos strings para ints
            params_list = []
            for p in all_params:
                try:
                    pos_int = int(p.get("pos", 0))
                    params_list.append((pos_int, p))
                except (ValueError, TypeError):
                    self.logger.warning(f"Pos inválida: {p.get('pos')}, ignorando")
                    continue

            if not params_list:
                return None

            # Selecionar baseado em trades_balance
            if trades_balance > 0:
                # Positivo: buscar máximo pos <= trades_balance
                valid = [p for p in params_list if p[0] <= trades_balance]
                if valid:
                    valid.sort(key=lambda x: x[0], reverse=True)
                    selected = valid[0][1]
                    self.logger.debug(
                        f"Strategy parameters fallback (positivo): pos={trades_balance} → pos={valid[0][0]}"
                    )
                    return selected
                else:
                    # Nenhum <= trades_balance, usar o máximo negativo/zero disponível
                    params_list.sort(key=lambda x: x[0], reverse=True)
                    selected = params_list[0][1]
                    self.logger.debug(
                        f"Strategy parameters fallback (positivo, nenhum válido): pos={trades_balance} → pos={params_list[0][0]}"
                    )
                    return selected

            elif trades_balance < 0:
                # Negativo: buscar mínimo pos >= trades_balance
                valid = [p for p in params_list if p[0] >= trades_balance]
                if valid:
                    valid.sort(key=lambda x: x[0])
                    selected = valid[0][1]
                    self.logger.debug(
                        f"Strategy parameters fallback (negativo): pos={trades_balance} → pos={valid[0][0]}"
                    )
                    return selected
                else:
                    # Nenhum >= trades_balance, usar o mínimo positivo/zero disponível
                    params_list.sort(key=lambda x: x[0])
                    selected = params_list[0][1]
                    self.logger.debug(
                        f"Strategy parameters fallback (negativo, nenhum válido): pos={trades_balance} → pos={params_list[0][0]}"
                    )
                    return selected

            else:  # trades_balance == 0
                # Zero: buscar exato pos=0 (OBRIGATÓRIO)
                for pos_int, param in params_list:
                    if pos_int == 0:
                        self.logger.debug("Strategy parameters encontrados: pos=0")
                        return param

                # pos=0 não existe - ERRO
                self.logger.error(
                    f"CRÍTICO: Strategy parameters pos=0 não encontrado para strategy={strategy_id}. "
                    f"pos=0 é obrigatório. ISINs não devem ter trades_balance=0 sem parâmetros."
                )
                return None

        except Exception as e:
            self.logger.error(f"Erro buscando strategy_parameters: {e}", exc_info=True)
            return None

    def _create_order_from_response(
        self,
        isin_id: str,
        api_response: Dict[str, Any],
        automation_status: str,
        related_order_id: Optional[str] = None,
    ) -> Dict:
        """
        Create an Order record from T212 API response.
        """
        return {
            "id": str(uuid.uuid4()),
            "isin_id": isin_id,
            "t212_order_id": api_response.get("id"),
            "ticker": api_response.get("ticker", ""),
            "instrument_isin": api_response.get("instrument", {}).get("isin"),
            "instrument_name": api_response.get("instrument", {}).get("name"),
            "instrument_currency": api_response.get("instrument", {}).get("currency"),
            "side": api_response.get("side", "BUY"),
            "quantity": api_response.get("quantity", 0),
            "filled_quantity": api_response.get("filledQuantity", 0),
            "type": api_response.get("type", "LIMIT"),
            "status": api_response.get("status", "NEW"),
            "limit_price": api_response.get("limitPrice"),
            "stop_price": api_response.get("stopPrice"),
            "time_in_force": api_response.get("timeInForce", "GOOD_TILL_CANCEL"),
            "initiated_from": api_response.get("initiatedFrom", "API"),
            "created_at": api_response.get("createdAt"),
            "automation_status": automation_status,
            "related_order_id": related_order_id,
            "synced_at": datetime.utcnow().isoformat(),
        }

    # =========================================================================
    # LOGGING HELPERS (Task 3: Database logging conditional on log_level)
    # =========================================================================
    # HELPER: PLACE ORDER WITH PRECISION RETRY
    # =========================================================================

    async def _place_order_with_precision_retry(
        self,
        order_type: str,
        ticker: str,
        quantity: float,
        limit_price: float,
        isin_id: str,
        initial_precision: int
    ):
        """
        Place a limit order with automatic precision detection and retry.

        If T212 API returns "invalid quantity precision X" error:
        1. Extract X from error message
        2. Update ISIN's quantity_precision to X
        3. Round quantity to X decimals
        4. Retry the order

        Args:
            order_type: "BUY" or "SELL"
            ticker: Ticker symbol
            quantity: Quantity to order (already rounded to initial_precision)
            limit_price: Limit price (already rounded to 3 decimals)
            isin_id: ISIN ID for updating quantity_precision
            initial_precision: Current precision setting for this ISIN

        Returns:
            API response if successful, None on failure
        """
        try:
            db = get_db()

            # First attempt with current precision
            self.logger.debug(
                f"AutomationEngine | Order attempt 1: {order_type} {ticker} qty={quantity} @ {limit_price} (precision={initial_precision})"
            )

            if order_type == "BUY":
                response = await self.t212_service.place_buy_limit_order(
                    ticker=ticker, quantity=quantity, limit_price=limit_price
                )
            elif order_type == "SELL":
                response = await self.t212_service.place_sell_limit_order(
                    ticker=ticker, quantity=quantity, limit_price=limit_price
                )
            else:
                self.logger.error(f"Invalid order_type: {order_type}")
                return None

            # If successful, return response
            if response:
                self.logger.info(
                    f"AutomationEngine | {order_type} order successful on first attempt: {ticker} qty={quantity}"
                )
                return response

            # If failed, we'll handle error below
            return None

        except Exception as e:
            error_str = str(e)

            # Check if it's a quantity precision error
            if "invalid quantity precision" in error_str.lower():
                self.logger.warning(
                    f"AutomationEngine | Quantity precision error for {ticker}: {error_str}"
                )

                # Try to extract precision value from error message
                # Format: "invalid quantity precision 2" or similar
                try:
                    parts = error_str.split("invalid quantity precision")
                    if len(parts) > 1:
                        precision_str = parts[1].strip().split()[0]
                        new_precision = int(precision_str)

                        self.logger.info(
                            f"AutomationEngine | Detected required precision: {new_precision} (was {initial_precision})"
                        )

                        # Update ISIN's quantity_precision
                        db.client.table("isins").update({
                            "quantity_precision": new_precision
                        }).eq("id", isin_id).execute()

                        self.logger.info(
                            f"AutomationEngine | Updated ISIN {isin_id} precision to {new_precision}"
                        )

                        # Round quantity to new precision
                        quantity_retried = round(quantity, new_precision)

                        # Retry the order
                        self.logger.info(
                            f"AutomationEngine | Retrying {order_type} order with new precision {new_precision}: qty={quantity_retried}"
                        )

                        if order_type == "BUY":
                            response = await self.t212_service.place_buy_limit_order(
                                ticker=ticker, quantity=quantity_retried, limit_price=limit_price
                            )
                        elif order_type == "SELL":
                            response = await self.t212_service.place_sell_limit_order(
                                ticker=ticker, quantity=quantity_retried, limit_price=limit_price
                            )
                        else:
                            return None

                        if response:
                            self.logger.info(
                                f"AutomationEngine | {order_type} order successful on retry: {ticker} qty={quantity_retried}"
                            )
                            return response
                        else:
                            self.logger.error(
                                f"AutomationEngine | {order_type} order failed on retry: {ticker}"
                            )
                            return None

                except (ValueError, IndexError) as parse_error:
                    self.logger.error(
                        f"AutomationEngine | Could not parse precision from error: {error_str} - {parse_error}"
                    )
                    return None

            else:
                # Not a precision error, log and return None
                self.logger.error(
                    f"AutomationEngine | {order_type} order failed: {ticker} - {error_str}"
                )
                return None

    # =========================================================================
        """
        Read current log_level from app_parameters.
        Defaults to 'OFF' if not found or on error.
        """
        try:
            db = get_db()
            result = db.client.table("app_parameters").select("log_level").execute()
            if result.data:
                log_level = result.data[0].get("log_level", "OFF")
                return log_level
            return "OFF"
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao ler log_level: {e}")
            return "OFF"

    def _log_db_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        Log a database or API action to the database (if log_level == 'MEDIUM').

        Args:
            action: Action description (e.g., "📖 Reading ISINs from database...")
            details: Optional dictionary with additional context

        This method silently fails if:
        - log_level != 'MEDIUM'
        - Database operation fails
        - Logging is disabled
        """
        try:
            # Check log level - only log if MEDIUM
            log_level = self._get_log_level()
            if log_level != 'MEDIUM':
                return

            # Insert into logs table
            db = get_db()
            db.client.table("logs").insert({
                "nivel": "INFO",
                "mensagem": action,
                "detalhes_json": details,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

        except Exception as e:
            # Silently fail - don't let logging break automation
            self.logger.debug(f"⚠️ Erro ao criar log de ação: {e}")

