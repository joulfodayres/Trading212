"""
Modelos SQLAlchemy para a BD Supabase
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
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    isin = Column(String, nullable=False)
    ticker = Column(String)
    name = Column(String)
    currency = Column(String, default="EUR")
    automation_enabled = Column(Boolean, default=False)
    fields_json = Column(JSON)  # Campos dinâmicos da API T212
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "isin", name="unique_user_isin"),
    )


class Config(Base):
    """Tabela de configuração (credenciais T212 encriptadas)"""
    __tablename__ = "config"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    t212_api_key_encrypted = Column(String)
    t212_api_secret_encrypted = Column(String)
    t212_environment = Column(String, default="demo")  # 'demo' ou 'live'
    strategy_params = Column(JSON)  # Parâmetros da estratégia
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Strategy(Base):
    """Tabela de estratégias"""
    __tablename__ = "strategies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default="grid_trading")  # Tipo de estratégia
    params = Column(JSON)  # Parâmetros específicos
    created_at = Column(DateTime, default=datetime.utcnow)


class Trade(Base):
    """Tabela de trades executados"""
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
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
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    nivel = Column(String)  # 'INFO', 'WARNING', 'ERROR'
    mensagem = Column(String)
    detalhes_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
