"""
Cliente Supabase para operações de BD
Wrapper para integração com Supabase PostgreSQL
Simplificado para single-user (sem user_id)
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)


# ===== SQLAlchemy-like wrapper para compatibilidade com AutomationEngine =====

class QueryBuilder:
    """Simula SQLAlchemy QueryBuilder"""

    def __init__(self, client: Client, table_name: str, model_class=None):
        self.client = client
        self.table_name = table_name
        self.model_class = model_class
        self._filters = []

    def filter_by(self, **kwargs):
        """Simula filter_by"""
        self._filters = kwargs
        return self

    def filter(self, *args):
        """Simula filter (por enquanto apenas suporta filter_by)"""
        return self

    def first(self):
        """Retorna primeiro resultado"""
        result = self.client.table(self.table_name).select("*").execute()
        for key, value in self._filters.items():
            if result.data:
                result.data = [r for r in result.data if r.get(key) == value]
        if result.data:
            return result.data[0]
        return None

    def all(self):
        """Retorna todos os resultados"""
        result = self.client.table(self.table_name).select("*").execute()
        filtered = result.data or []
        for key, value in self._filters.items():
            filtered = [r for r in filtered if r.get(key) == value]
        return filtered


class SQLAlchemyCompatibleSession:
    """Wrapper que oferece interface SQLAlchemy mas usa Supabase por baixo"""

    def __init__(self, client: Client):
        self.client = client
        self._objects_to_add = []
        self._objects_to_update = {}

    def query(self, model_class):
        """Simula session.query()"""
        table_name = self._get_table_name(model_class)
        return QueryBuilder(self.client, table_name, model_class)

    def add(self, obj):
        """Simula session.add()"""
        self._objects_to_add.append(obj)

    def commit(self):
        """Comita as mudanças (inserts)"""
        for obj in self._objects_to_add:
            self._insert_object(obj)
        self._objects_to_add = []

    def rollback(self):
        """Cancela a transação"""
        self._objects_to_add = []
        self._objects_to_update = {}

    def close(self):
        """Fecha a sessão"""
        pass

    def _get_table_name(self, model_class):
        """Obtém o nome da tabela a partir da classe modelo"""
        # Mapping simples
        mapping = {
            "ISIN": "isins",
            "Strategy": "strategies",
            "StrategyParameters": "strategy_parameters",
            "Order": "orders",
        }
        class_name = model_class.__name__ if hasattr(model_class, '__name__') else str(model_class)
        return mapping.get(class_name, class_name.lower() + "s")

    def _insert_object(self, obj):
        """Insere um objeto na BD"""
        table_name = self._get_table_name(obj.__class__)
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        try:
            self.client.table(table_name).insert(data).execute()
            logger.debug(f"Inserted object in {table_name}: {data.get('id', 'no-id')}")
        except Exception as e:
            logger.error(f"Error inserting object: {e}")
            raise


class SupabaseDB:
    """Cliente Supabase singleton"""

    _instance: Optional["SupabaseDB"] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa cliente Supabase"""
        if self._client is None:
            try:
                self._client = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info(" Cliente Supabase inicializado")
            except Exception as e:
                logger.error(f" Erro ao inicializar Supabase: {str(e)}")
                raise

    @property
    def client(self) -> Client:
        """Retorna instância do cliente Supabase"""
        if self._client is None:
            self.__init__()
        return self._client

    # ===== OPERAÇÕES GENÉRICAS =====

    def query(self, table: str) -> Any:
        """Retorna query builder para uma tabela"""
        return self.client.table(table)

    # ===== ISINS =====

    def create_isin(self, isin: str, ticker: str, name: str, currency: str = "EUR", fields_json: Optional[Dict] = None) -> Dict:
        """Criar novo ISIN"""
        try:
            data = {
                "isin": isin,
                "ticker": ticker,
                "name": name,
                "currency": currency,
                "automation_enabled": False,
                "fields_json": fields_json or {}
            }

            response = self.client.table("isins").insert(data).execute()
            if response.data:
                logger.info(f" ISIN criado: {isin}")
                return response.data[0]
            else:
                raise Exception(f"Falha ao criar ISIN: {response}")

        except Exception as e:
            logger.error(f" Erro ao criar ISIN: {str(e)}")
            raise

    def get_isin(self, isin_id: str) -> Optional[Dict]:
        """Obter ISIN específico"""
        try:
            response = self.client.table("isins").select("*").eq("id", isin_id).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f" Erro ao obter ISIN: {str(e)}")
            raise

    def get_isin_by_isin_code(self, isin: str) -> Optional[Dict]:
        """Obter ISIN por código ISIN"""
        try:
            response = self.client.table("isins").select("*").eq("isin", isin).execute()

            if response.data:
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f" Erro ao obter ISIN por código: {str(e)}")
            raise

    def list_isins(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Listar todos os ISINs"""
        try:
            response = (
                self.client.table("isins")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )

            return response.data or []

        except Exception as e:
            logger.error(f" Erro ao listar ISINs: {str(e)}")
            raise

    def update_isin(self, isin_id: str, updates: Dict) -> Optional[Dict]:
        """Atualizar ISIN"""
        try:
            # Always refresh updated_at on any update
            updates = {**updates, "updated_at": datetime.utcnow().isoformat()}
            response = (
                self.client.table("isins")
                .update(updates)
                .eq("id", isin_id)
                .execute()
            )

            if response.data:
                logger.info(f" ISIN atualizado: {isin_id}")
                return response.data[0]
            else:
                raise Exception(f"ISIN não encontrado: {isin_id}")

        except Exception as e:
            logger.error(f" Erro ao atualizar ISIN: {str(e)}")
            raise

    def delete_isin(self, isin_id: str) -> bool:
        """Deletar ISIN (com cascade delete de trades)"""
        try:
            # Primeiro, deletar todos os trades associados
            self.client.table("trades").delete().eq("isin_id", isin_id).execute()

            # Depois, deletar o ISIN
            response = (
                self.client.table("isins")
                .delete()
                .eq("id", isin_id)
                .execute()
            )

            logger.info(f" ISIN deletado: {isin_id}")
            return True

        except Exception as e:
            logger.error(f" Erro ao deletar ISIN: {str(e)}")
            raise

    def toggle_automation(self, isin_id: str) -> Optional[Dict]:
        """Toggle automation_enabled para um ISIN"""
        try:
            # Primeiro, obter o ISIN atual
            isin = self.get_isin(isin_id)
            if not isin:
                raise Exception(f"ISIN não encontrado: {isin_id}")

            # Inverter o valor
            new_value = not isin.get("automation_enabled", False)

            # Atualizar
            response = (
                self.client.table("isins")
                .update({
                    "automation_enabled": new_value,
                    "updated_at": datetime.utcnow().isoformat()
                })
                .eq("id", isin_id)
                .execute()
            )

            if response.data:
                logger.info(f" Automação toggled: {isin_id} = {new_value}")
                return response.data[0]
            else:
                raise Exception(f"Falha ao toggle automação: {isin_id}")

        except Exception as e:
            logger.error(f" Erro ao toggle automation: {str(e)}")
            raise

    # ===== TRADES =====

    def list_isin_trades(self, isin_id: str, limit: int = 50) -> List[Dict]:
        """Listar trades para um ISIN"""
        try:
            response = (
                self.client.table("trades")
                .select("*")
                .eq("isin_id", isin_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return response.data or []

        except Exception as e:
            logger.error(f" Erro ao listar trades: {str(e)}")
            raise

    def get_isin_pnl(self, isin_id: str) -> Dict:
        """Calcular P&L total para um ISIN baseado em trades"""
        try:
            trades = self.list_isin_trades(isin_id, limit=1000)

            total_bought = 0
            total_bought_value = 0
            total_sold = 0
            total_sold_value = 0

            for trade in trades:
                if trade["status"] != "EXECUTED":
                    continue

                qty = float(trade.get("quantidade", 0))
                price = float(trade.get("preco", 0))
                commission = float(trade.get("comissao", 0))

                if trade["tipo"] == "BUY":
                    total_bought += qty
                    total_bought_value += qty * price + commission
                else:  # SELL
                    total_sold += qty
                    total_sold_value += qty * price - commission

            # P&L realizados
            pnl = total_sold_value - total_bought_value if total_sold > 0 else 0
            pnl_percent = (pnl / total_bought_value * 100) if total_bought_value > 0 else 0

            return {
                "total_bought": total_bought,
                "total_bought_value": total_bought_value,
                "total_sold": total_sold,
                "total_sold_value": total_sold_value,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
                "quantity_holding": total_bought - total_sold
            }

        except Exception as e:
            logger.error(f" Erro ao calcular P&L: {str(e)}")
            return {
                "total_bought": 0,
                "total_bought_value": 0,
                "total_sold": 0,
                "total_sold_value": 0,
                "pnl": 0,
                "pnl_percent": 0,
                "quantity_holding": 0
            }


# Singleton global
_db_instance: Optional[SupabaseDB] = None
_supabase_client: Optional[Client] = None


def get_db() -> SupabaseDB:
    """Factory function para obter instância global da BD"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance


def get_supabase_client() -> Client:
    """Retorna cliente Supabase puro"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
    return _supabase_client


def SessionLocal() -> SQLAlchemyCompatibleSession:
    """Factory para criar nova sessão tipo SQLAlchemy"""
    client = get_supabase_client()
    return SQLAlchemyCompatibleSession(client)
