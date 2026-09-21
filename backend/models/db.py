"""
Modelos SQLAlchemy para a BD Supabase
Simplificado para single-user (sem user_id)
Phase 4: Grid Trading Automation
"""
from sqlalchemy import (
    create_engine, Column, String, Boolean, DateTime, DECIMAL, ForeignKey,
    JSON, UniqueConstraint, Integer, Float, CHAR
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


class AppParameters(Base):
    """Tabela de parâmetros gerais da aplicação - Configuração do scheduler e automação"""
    __tablename__ = "app_parameters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Scheduler configuration
    scheduler_interval_seconds = Column(Integer, default=15)

    # Grid trading configuration
    grid_trading_enabled = Column(Boolean, default=True)

    # Logging configuration
    log_level = Column(String, default='OFF')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """Tabela de utilizadores"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ISIN(Base):
    """Tabela de ISINs - Instrumentos com dados sincronizados da API T212"""
    __tablename__ = "isins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin = Column(String, nullable=False, unique=True)
    ticker = Column(String)
    name = Column(String)
    currency = Column(String, default="EUR")
    automation_enabled = Column(Boolean, default=False)
    strategy_id = Column(String)  # Referência a estratégia

    # Campos sincronizados da API T212 (GET /equity/positions)
    api_created_at = Column(DateTime)  # created_at da API (separado do local)
    initial_trade = Column(Boolean, default=False)
    trades_balance = Column(Integer, default=0)
    average_price_paid = Column(Float)
    current_price = Column(Float)
    quantity = Column(Float, default=0)
    quantity_available_for_trading = Column(Float, default=0)
    quantity_in_pies = Column(Float, default=0)

    # T212 API Precision (adaptive per ISIN)
    quantity_precision = Column(Integer, default=3)  # Decimal places T212 accepts for this ISIN

    # Wallet Impact (walletImpact da API)
    wi_currency = Column(String)
    wi_current_value = Column(Float)
    wi_fx_impact = Column(Float)
    wi_total_cost = Column(Float)
    wi_unrealized_profit_loss = Column(Float)

    # Timestamps locais
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Config(Base):
    """Tabela de configuração (credenciais T212 encriptadas)"""
    __tablename__ = "config"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    t212_api_key_encrypted = Column(String)
    t212_api_secret_encrypted = Column(String)
    t212_environment = Column(String, default="demo")  # 'demo' ou 'live'
    strategy_params = Column(JSON)  # Parâmetros da estratégia
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Strategy(Base):
    """Tabela de estratégias - Com suporte a Phase 4 Grid Trading"""
    __tablename__ = "strategies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_name = Column(String, nullable=False, unique=True)
    strategy_desc = Column(String)
    strategy_status = Column(String, nullable=False, default="E")  # 'E'=Enabled, 'D'=Disabled

    # Phase 4: Capital inicial da estratégia
    initial_investment = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyParameters(Base):
    """Tabela de parâmetros de estratégia"""
    __tablename__ = "strategy_parameters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    pos = Column(String, nullable=False)  # Posição/versão dos parâmetros
    param1 = Column(DECIMAL)
    param2 = Column(DECIMAL)
    param3 = Column(DECIMAL)
    param4 = Column(DECIMAL)
    param5 = Column(DECIMAL)
    param6 = Column(DECIMAL)
    param7 = Column(DECIMAL)
    param8 = Column(DECIMAL)
    param9 = Column(DECIMAL)
    param10 = Column(DECIMAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Trade(Base):
    """Tabela de trades executados"""
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin_id = Column(String, ForeignKey("isins.id", ondelete="CASCADE"))
    strategy_id = Column(String, ForeignKey("strategies.id"))
    tipo = Column(String)  # 'BUY' ou 'SELL'
    quantidade = Column(DECIMAL)
    preco = Column(DECIMAL)
    comissao = Column(DECIMAL, default=0)
    status = Column(String)  # 'PENDING', 'EXECUTED', 'FAILED'
    t212_order_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    detalhes_json = Column(JSON)


class Log(Base):
    """Tabela de logs do sistema"""
    __tablename__ = "logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nivel = Column(String)  # 'INFO', 'WARNING', 'ERROR'
    mensagem = Column(String)
    detalhes_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """Tabela de ordens T212 - Phase 4 Grid Trading

    Rastreia todas as ordens colocadas via Trading 212 API.
    Campos sincronizados da API, com rastreamento local de automação.
    """
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin_id = Column(String, ForeignKey("isins.id", ondelete="CASCADE"), nullable=False)

    # Campos da Order API T212
    t212_order_id = Column(Integer, nullable=False)  # ID único na T212 API
    ticker = Column(String, nullable=False)
    instrument_isin = Column(String)
    instrument_name = Column(String)
    instrument_currency = Column(String)

    # Tipo e quantidade
    side = Column(String, nullable=False)  # 'BUY' ou 'SELL'
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0)

    # Tipo de ordem e status
    type = Column(String, nullable=False)  # MARKET, LIMIT, STOP, STOP_LIMIT
    status = Column(String, nullable=False)  # NEW, CONFIRMED, FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED, UNCONFIRMED

    # Preços (opcionais)
    limit_price = Column(Float)
    stop_price = Column(Float)

    # Parâmetros adicionais
    time_in_force = Column(String)  # DAY ou GOOD_TILL_CANCEL
    initiated_from = Column(String)

    # Timestamp da API T212
    created_at = Column(DateTime, nullable=False)

    # Automação Local (Phase 4)
    automation_status = Column(CHAR(1), default='W')  # W=Watch, E=Executed, C=Canceled

    # Relacionamento BUY ↔ SELL (sempre 1 de cada)
    related_order_id = Column(String, ForeignKey("orders.id", ondelete="SET NULL"))

    # Rastreamento local
    synced_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IsINStrategyHistory(Base):
    """Tabela de histórico de automação"""
    __tablename__ = "isin_strategy_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin_id = Column(String, ForeignKey("isins.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(String)
    automated = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
