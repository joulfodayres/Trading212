"""
Modelos SQLAlchemy para a BD Supabase
Simplificado para single-user (sem user_id)
"""
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, DECIMAL, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """Tabela de utilizadores"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ISIN(Base):
    """Tabela de ISINs"""
    __tablename__ = "isins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin = Column(String, nullable=False, unique=True)
    ticker = Column(String)
    name = Column(String)
    currency = Column(String, default="EUR")
    automation_enabled = Column(Boolean, default=False)
    strategy_id = Column(String)  # Referência a estratégia
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
    """Tabela de estratégias"""
    __tablename__ = "strategies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_name = Column(String, nullable=False, unique=True)
    strategy_desc = Column(String)
    strategy_status = Column(String, nullable=False, default="E")  # 'E'=Enabled, 'D'=Disabled
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


class IsINStrategyHistory(Base):
    """Tabela de histórico de automação"""
    __tablename__ = "isin_strategy_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isin_id = Column(String, ForeignKey("isins.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(String)
    automated = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
