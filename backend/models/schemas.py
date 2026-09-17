"""
Schemas Pydantic para validação de requests/responses
Simplificado para single-user (sem user_id)
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para criar utilizador"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de response de utilizador"""
    id: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ISINCreate(BaseModel):
    """Schema para criar ISIN"""
    isin: str
    name: Optional[str] = None
    ticker: Optional[str] = None


class ISINUpdate(BaseModel):
    """Schema para atualizar ISIN"""
    name: Optional[str] = None
    ticker: Optional[str] = None
    automation_enabled: Optional[bool] = None


class ISINResponse(BaseModel):
    """Schema de response de ISIN"""
    id: str
    isin: str
    ticker: Optional[str]
    name: Optional[str]
    currency: str
    automation_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigCreate(BaseModel):
    """Schema para criar/atualizar config"""
    t212_api_key: str
    t212_api_secret: str
    t212_environment: str = "demo"
    strategy_params: Optional[Dict[str, Any]] = None


class ConfigResponse(BaseModel):
    """Schema de response de config"""
    id: str
    t212_environment: str
    strategy_params: Optional[Dict[str, Any]]
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyCreate(BaseModel):
    """Schema para criar estratégia"""
    strategy_name: str
    strategy_desc: Optional[str] = None
    strategy_status: str = "E"


class StrategyResponse(BaseModel):
    """Schema de response de estratégia"""
    id: str
    strategy_name: str
    strategy_desc: Optional[str]
    strategy_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    """Schema de response de trade"""
    id: str
    isin_id: Optional[str]
    strategy_id: Optional[str]
    tipo: str
    quantidade: float
    preco: float
    comissao: float
    status: str
    t212_order_id: Optional[str]
    created_at: datetime
    executed_at: Optional[datetime]
    detalhes_json: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class LogResponse(BaseModel):
    """Schema de response de log"""
    id: str
    nivel: str
    mensagem: str
    detalhes_json: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
