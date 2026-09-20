"""
AutomationEngine - Grid Trading Automation Logic (3 Phases)
Phase 4: Grid Trading Automation
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.db import ISIN, Strategy, StrategyParameters, Order, AppParameters
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

    def __init__(self, db_session: Session, t212_service: T212Service):
        """
        Initialize automation engine

        Args:
            db_session: SQLAlchemy session (Supabase)
            t212_service: T212Service instance for API calls
        """
        self.db_session = db_session
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

        self.logger.info(f"🔄 Ciclo #{self.cycle_count} iniciado")

        try:
            # Check if global automation is enabled
            grid_trading_enabled = self._check_grid_trading_enabled()
            if not grid_trading_enabled:
                self.logger.debug("⏸️ Grid trading está desativado globalmente, ciclo ignorado")
                return

            # PHASE 1: Setup initial BUY/SELL pairs
            self.logger.debug("Fase 1: Setup Inicial")
            await self._phase_1_initial_setup()

            # PHASE 2: Monitor Watch orders
            self.logger.debug("Fase 2: Monitorar Ordens")
            await self._phase_2_monitor_orders()

            # PHASE 3: Handle order fills and rebalance
            self.logger.debug("Fase 3: Processar Fills")
            await self._phase_3_handle_fills()

            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.last_cycle_duration = cycle_duration
            self.logger.info(f"✅ Ciclo #{self.cycle_count} completo ({cycle_duration:.2f}s)")

        except Exception as e:
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            self.last_cycle_duration = cycle_duration
            self.logger.error(
                f"❌ Erro no ciclo #{self.cycle_count} ({cycle_duration:.2f}s): {e}",
                exc_info=True,
            )
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
            isins = (
                self.db_session.query(ISIN)
                .filter(
                    and_(
                        ISIN.initial_trade == True,
                        ISIN.automation_enabled == True,
                    )
                )
                .all()
            )

            if not isins:
                self.logger.debug("Nenhum ISIN com initial_trade=TRUE encontrado")
                return

            self.logger.info(f"Fase 1: {len(isins)} ISINs para setup inicial")

            for isin in isins:
                await self._phase_1_setup_isin(isin)

        except Exception as e:
            self.logger.error(f"❌ Erro na Fase 1: {e}", exc_info=True)

    async def _phase_1_setup_isin(self, isin: ISIN):
        """
        Setup initial orders for a single ISIN.
        """
        try:
            self.logger.info(
                f"Fase 1: Setup {isin.ticker} (current_price={isin.current_price})"
            )

            # Load strategy
            strategy = self.db_session.query(Strategy).filter_by(id=isin.strategy_id).first()
            if not strategy:
                self.logger.warning(f"Strategy não encontrada para {isin.ticker}")
                return

            # Load strategy parameters for current position (trades_balance)
            params = self._get_strategy_parameters(strategy.id, isin.trades_balance)

            if not params:
                self.logger.warning(
                    f"Parâmetros não encontrados para {isin.ticker} pos={isin.trades_balance}"
                )
                return

            # Calculate prices
            buy_price = isin.current_price * (1 + params.param1 / 100)
            sell_price = isin.current_price * (1 + params.param2 / 100)

            # Calculate quantities
            buy_quantity = strategy.initial_investment / buy_price
            sell_quantity = strategy.initial_investment / sell_price

            self.logger.debug(
                f"BUY @ {buy_price:.2f} qty={buy_quantity:.2f}, SELL @ {sell_price:.2f} qty={sell_quantity:.2f}"
            )

            # Place BUY order
            buy_response = await self.t212_service.place_buy_limit_order(
                ticker=isin.ticker, quantity=buy_quantity, limit_price=buy_price
            )
            if not buy_response:
                self.logger.error(f"Falha ao colocar BUY order para {isin.ticker}")
                return

            # Place SELL order
            sell_response = await self.t212_service.place_sell_limit_order(
                ticker=isin.ticker, quantity=sell_quantity, limit_price=sell_price
            )
            if not sell_response:
                self.logger.error(f"Falha ao colocar SELL order para {isin.ticker}")
                # TODO: Cancela BUY order? (Por agora não, Phase 5)
                return

            # Save BUY order to DB
            buy_order_id = buy_response.get("id")
            sell_order_id = sell_response.get("id")

            buy_order = self._create_order_from_response(
                isin_id=isin.id,
                api_response=buy_response,
                automation_status="W",
                related_order_id=None,  # Will update after SELL order created
            )

            sell_order = self._create_order_from_response(
                isin_id=isin.id,
                api_response=sell_response,
                automation_status="W",
                related_order_id=None,  # Will update after SELL order created
            )

            # Link orders together
            buy_order.related_order_id = sell_order.id
            sell_order.related_order_id = buy_order.id

            # Save to DB
            self.db_session.add(buy_order)
            self.db_session.add(sell_order)

            # Mark ISIN as setup done
            isin.initial_trade = False

            self.db_session.commit()

            self.logger.info(
                f"✅ {isin.ticker}: Ordens criadas (BUY id={buy_order_id}, SELL id={sell_order_id})"
            )

        except Exception as e:
            self.logger.error(f"❌ Erro setup {isin.ticker}: {e}", exc_info=True)
            self.db_session.rollback()

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
            watch_orders = self.db_session.query(Order).filter_by(automation_status="W").all()

            if not watch_orders:
                self.logger.debug("Nenhuma ordem 'W' para monitorar")
                return

            self.logger.info(f"Fase 2: Monitorando {len(watch_orders)} ordens")

            for order in watch_orders:
                await self._phase_2_monitor_order(order)

        except Exception as e:
            self.logger.error(f"❌ Erro na Fase 2: {e}", exc_info=True)

    async def _phase_2_monitor_order(self, order: Order):
        """
        Monitor a single order - poll T212 for status.
        """
        try:
            # Poll T212 API
            t212_order = await self.t212_service.get_pending_order(order.t212_order_id)

            if not t212_order:
                self.logger.debug(f"Ordem {order.t212_order_id} não encontrada em T212 (pode estar FILLED)")
                return

            # Update order status from T212 response
            order.status = t212_order.get("status", order.status)
            order.filled_quantity = t212_order.get("filledQuantity", order.filled_quantity)
            order.synced_at = datetime.utcnow()

            # If FILLED, mark as 'E' (Executed)
            if order.status == "FILLED":
                order.automation_status = "E"
                self.logger.info(f"✅ Ordem {order.t212_order_id} FILLED")

            self.db_session.commit()

        except Exception as e:
            self.logger.error(
                f"❌ Erro monitorando ordem {order.t212_order_id}: {e}", exc_info=True
            )
            self.db_session.rollback()

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
            filled_orders = self.db_session.query(Order).filter(
                and_(Order.status == "FILLED", Order.automation_status == "E")
            ).all()

            if not filled_orders:
                self.logger.debug("Nenhuma ordem FILLED para processar")
                return

            self.logger.info(f"Fase 3: Processando {len(filled_orders)} ordens FILLED")

            for order in filled_orders:
                await self._phase_3_handle_filled_order(order)

        except Exception as e:
            self.logger.error(f"❌ Erro na Fase 3: {e}", exc_info=True)

    async def _phase_3_handle_filled_order(self, order: Order):
        """
        Handle a single filled order.
        """
        try:
            # Load ISIN
            isin = self.db_session.query(ISIN).filter_by(id=order.isin_id).first()
            if not isin:
                self.logger.error(f"ISIN não encontrado para ordem {order.id}")
                return

            self.logger.info(f"Fase 3: Processando {isin.ticker} fill (side={order.side})")

            # Get latest position from T212
            position = await self.t212_service.get_position(isin.ticker)
            if position:
                # Update ISIN with position data
                isin.quantity = position.get("quantity", isin.quantity)
                isin.current_price = position.get("currentPrice", isin.current_price)
                isin.average_price_paid = position.get("averagePricePaid", isin.average_price_paid)
                isin.quantity_available_for_trading = position.get(
                    "quantityAvailableForTrading", isin.quantity_available_for_trading
                )

                # Wallet impact
                wi = position.get("walletImpact", {})
                isin.wi_current_value = wi.get("currentValue", isin.wi_current_value)
                isin.wi_total_cost = wi.get("totalCost", isin.wi_total_cost)
                isin.wi_unrealized_profit_loss = wi.get("unrealizedProfitLoss", isin.wi_unrealized_profit_loss)

            # Adjust trades_balance based on order side
            if order.side == "BUY":
                isin.trades_balance -= 1
                self.logger.debug(f"BUY fill: trades_balance {isin.trades_balance + 1} → {isin.trades_balance}")
            elif order.side == "SELL":
                isin.trades_balance += 1
                self.logger.debug(f"SELL fill: trades_balance {isin.trades_balance - 1} → {isin.trades_balance}")

            # Save position update
            self.db_session.commit()

            # Cancel related order
            if order.related_order_id:
                related_order = self.db_session.query(Order).filter_by(id=order.related_order_id).first()
                if related_order and related_order.t212_order_id:
                    cancel_success = await self.t212_service.cancel_order(related_order.t212_order_id)
                    if cancel_success:
                        related_order.automation_status = "C"
                        related_order.status = "CANCELLED"
                        self.db_session.commit()

            # Place new BUY/SELL pair at new grid level
            await self._phase_3_place_new_pair(isin)

        except Exception as e:
            self.logger.error(f"❌ Erro processando filled order: {e}", exc_info=True)
            self.db_session.rollback()

    async def _phase_3_place_new_pair(self, isin: ISIN):
        """
        Place new BUY/SELL pair at new grid level (after fill).
        """
        try:
            # Load strategy
            strategy = self.db_session.query(Strategy).filter_by(id=isin.strategy_id).first()
            if not strategy:
                self.logger.warning(f"Strategy não encontrada para {isin.ticker}")
                return

            # Load new parameters for new trades_balance position
            params = self._get_strategy_parameters(strategy.id, isin.trades_balance)

            if not params:
                self.logger.warning(
                    f"Parâmetros não encontrados para {isin.ticker} pos={isin.trades_balance}"
                )
                return

            # Calculate new prices
            buy_price = isin.current_price * (1 + params.param1 / 100)
            sell_price = isin.current_price * (1 + params.param2 / 100)

            buy_quantity = strategy.initial_investment / buy_price
            sell_quantity = strategy.initial_investment / sell_price

            self.logger.debug(
                f"Novo pair: BUY @ {buy_price:.2f} qty={buy_quantity:.2f}, SELL @ {sell_price:.2f} qty={sell_quantity:.2f}"
            )

            # Place BUY order
            buy_response = await self.t212_service.place_buy_limit_order(
                ticker=isin.ticker, quantity=buy_quantity, limit_price=buy_price
            )
            if not buy_response:
                self.logger.error(f"Falha ao colocar novo BUY order para {isin.ticker}")
                return

            # Place SELL order
            sell_response = await self.t212_service.place_sell_limit_order(
                ticker=isin.ticker, quantity=sell_quantity, limit_price=sell_price
            )
            if not sell_response:
                self.logger.error(f"Falha ao colocar novo SELL order para {isin.ticker}")
                return

            # Create order records
            buy_order = self._create_order_from_response(
                isin_id=isin.id,
                api_response=buy_response,
                automation_status="W",
                related_order_id=None,
            )

            sell_order = self._create_order_from_response(
                isin_id=isin.id,
                api_response=sell_response,
                automation_status="W",
                related_order_id=None,
            )

            # Link orders
            buy_order.related_order_id = sell_order.id
            sell_order.related_order_id = buy_order.id

            self.db_session.add(buy_order)
            self.db_session.add(sell_order)
            self.db_session.commit()

            self.logger.info(
                f"✅ Novo pair para {isin.ticker} @ level {isin.trades_balance} (BUY id={buy_response.get('id')}, SELL id={sell_response.get('id')})"
            )

        except Exception as e:
            self.logger.error(f"❌ Erro criando novo pair: {e}", exc_info=True)
            self.db_session.rollback()

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _check_grid_trading_enabled(self) -> bool:
        """
        Verifica se grid_trading_enabled está ativo em app_parameters.
        """
        try:
            result = self.db_session.query(AppParameters).first()
            if result:
                # Assumes AppParameters model has grid_trading_enabled attribute
                return getattr(result, 'grid_trading_enabled', True)
            return True
        except Exception as e:
            self.logger.warning(f"Erro verificando grid_trading_enabled: {e}, assumindo True")
            return True

    def _get_strategy_parameters(self, strategy_id: str, trades_balance: int) -> Optional[StrategyParameters]:
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
            # Step 1: Tentar exato
            params = (
                self.db_session.query(StrategyParameters)
                .filter_by(strategy_id=strategy_id, pos=str(trades_balance))
                .first()
            )

            if params:
                self.logger.debug(
                    f"Strategy parameters encontrados exato: pos={trades_balance}"
                )
                return params

            # Step 2: Fallback baseado na direção
            all_params = (
                self.db_session.query(StrategyParameters)
                .filter_by(strategy_id=strategy_id)
                .all()
            )

            if not all_params:
                self.logger.warning(
                    f"Nenhuns strategy_parameters encontrados para strategy={strategy_id}"
                )
                return None

            # Converter pos strings para ints
            params_list = []
            for p in all_params:
                try:
                    pos_int = int(p.pos)
                    params_list.append((pos_int, p))
                except (ValueError, TypeError):
                    self.logger.warning(f"Pos inválida: {p.pos}, ignorando")
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
    ) -> Order:
        """
        Create an Order record from T212 API response.
        """
        return Order(
            id=str(__import__("uuid").uuid4()),
            isin_id=isin_id,
            t212_order_id=api_response.get("id"),
            ticker=api_response.get("ticker", ""),
            instrument_isin=api_response.get("instrument", {}).get("isin"),
            instrument_name=api_response.get("instrument", {}).get("name"),
            instrument_currency=api_response.get("instrument", {}).get("currency"),
            side=api_response.get("side", "BUY"),
            quantity=api_response.get("quantity", 0),
            filled_quantity=api_response.get("filledQuantity", 0),
            type=api_response.get("type", "LIMIT"),
            status=api_response.get("status", "NEW"),
            limit_price=api_response.get("limitPrice"),
            stop_price=api_response.get("stopPrice"),
            time_in_force=api_response.get("timeInForce", "GOOD_TILL_CANCEL"),
            initiated_from=api_response.get("initiatedFrom", "API"),
            created_at=api_response.get("createdAt"),
            automation_status=automation_status,
            related_order_id=related_order_id,
            synced_at=datetime.utcnow(),
        )
