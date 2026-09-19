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
    """Schema de response de ISIN - Com campos sincronizados da API T212"""
    id: str
    isin: str
    ticker: Optional[str]
    name: Optional[str]
    currency: str
    automation_enabled: bool

    # Campos sincronizados da API T212
    api_created_at: Optional[datetime] = None
    initial_trade: Optional[bool] = None
    trades_balance: Optional[int] = None
    average_price_paid: Optional[float] = None
    current_price: Optional[float] = None
    quantity: Optional[float] = None
    quantity_available_for_trading: Optional[float] = None
    quantity_in_pies: Optional[float] = None

    # Wallet Impact
    wi_currency: Optional[str] = None
    wi_current_value: Optional[float] = None
    wi_fx_impact: Optional[float] = None
    wi_total_cost: Optional[float] = None
    wi_unrealized_profit_loss: Optional[float] = None

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


class StrategyResponse(BaseModel):
    """Schema de response de estratégia - Com suporte a Phase 4"""
    id: str
    strategy_name: str
    strategy_desc: Optional[str]
    strategy_status: str
    initial_investment: Optional[float] = None  # Phase 4: Capital inicial
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyCreate(BaseModel):
    """Schema para criar estratégia - Com Phase 4 fields"""
    strategy_name: str
    strategy_desc: Optional[str] = None
    strategy_status: str = "E"
    initial_investment: Optional[float] = None


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


# =====================================================
# PHASE 4: ORDER SCHEMAS
# =====================================================

class OrderCreate(BaseModel):
    """Schema para criar uma ordem (internal use)"""
    isin_id: str
    t212_order_id: int
    ticker: str
    instrument_isin: Optional[str] = None
    instrument_name: Optional[str] = None
    instrument_currency: Optional[str] = None

    side: str  # BUY ou SELL
    quantity: float
    filled_quantity: Optional[float] = 0

    type: str  # MARKET, LIMIT, STOP, STOP_LIMIT
    status: str  # NEW, CONFIRMED, FILLED, etc

    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

    time_in_force: Optional[str] = None
    initiated_from: Optional[str] = None

    created_at: datetime

    automation_status: Optional[str] = "W"  # W, E, C
    related_order_id: Optional[str] = None


class OrderResponse(BaseModel):
    """Schema de response de ordem T212"""
    id: str
    isin_id: str

    t212_order_id: int
    ticker: str
    instrument_isin: Optional[str]
    instrument_name: Optional[str]
    instrument_currency: Optional[str]

    side: str
    quantity: float
    filled_quantity: float

    type: str
    status: str

    limit_price: Optional[float]
    stop_price: Optional[float]

    time_in_force: Optional[str]
    initiated_from: Optional[str]

    created_at: datetime

    automation_status: str
    related_order_id: Optional[str]

    synced_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """Schema para atualizar status de ordem"""
    status: Optional[str] = None
    filled_quantity: Optional[float] = None
    automation_status: Optional[str] = None
    related_order_id: Optional[str] = None


class OrderListResponse(BaseModel):
    """Schema para listagem de ordens"""
    items: list[OrderResponse]
    total: int
