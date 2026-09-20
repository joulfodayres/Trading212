"""
SchedulerService - Manages APScheduler lifecycle for automation engine
Phase 4: Grid Trading Automation
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Manages APScheduler for running automation_engine.run_cycle() every X seconds.
    Scheduler runs in a background thread.
    """

    def __init__(self, db_session: Session, automation_engine):
        """
        Initialize scheduler service

        Args:
            db_session: SQLAlchemy session (Supabase)
            automation_engine: AutomationEngine instance
        """
        self.scheduler = BackgroundScheduler(daemon=False)
        self.db_session = db_session
        self.automation_engine = automation_engine
        self.is_running = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def start(self):
        """
        Start the scheduler during app startup.
        Reads interval from app_parameters table.
        """
        if self.is_running:
            self.logger.warning("Scheduler já está a correr!")
            return

        try:
            # Get scheduler interval from database
            interval = await self._get_scheduler_interval()

            # Wrapper for async run_cycle (APScheduler runs sync jobs only)
            def run_cycle_wrapper():
                """Wrapper to run async function in sync context"""
                import asyncio
                try:
                    asyncio.run(self.automation_engine.run_cycle())
                except Exception as e:
                    self.logger.error(f"❌ Erro ao executar ciclo: {e}", exc_info=True)

            # Register the job
            self.scheduler.add_job(
                func=run_cycle_wrapper,
                trigger=IntervalTrigger(seconds=interval),
                id="automation_cycle",
                name="Automation Engine Cycle",
                max_instances=1,  # CRITICAL: Prevent overlapping cycles
                replace_existing=True,
                coalesce=True,  # If missed trigger, run once
            )

            # Start the scheduler (background thread)
            self.scheduler.start()
            self.is_running = True

            self.logger.info(
                f"✅ Scheduler iniciado com sucesso. Intervalo: {interval}s"
            )

            # [NEW] Run first cycle immediately on startup
            self.logger.info("🚀 Executando primeira ciclo imediatamente no arranque")
            try:
                run_cycle_wrapper()
            except Exception as e:
                self.logger.error(f"❌ Erro ao executar primeira ciclo: {e}", exc_info=True)
                # Don't fail startup if first cycle fails, just log error

        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar scheduler: {e}", exc_info=True)
            raise

    def stop(self):
        """Stop the scheduler during app shutdown."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            self.logger.info("✅ Scheduler parado com sucesso")

    async def _get_scheduler_interval(self) -> int:
        """
        Read scheduler interval from app_parameters table (Supabase).
        Falls back to 15 seconds if error.
        """
        try:
            from db.supabase_client import get_db

            db = get_db()
            result = db.client.table("app_parameters").select("scheduler_interval_seconds").execute()

            if result.data and len(result.data) > 0:
                interval = result.data[0].get("scheduler_interval_seconds", 15)
                if interval >= 5:
                    self.logger.info(f"[DEBUG] Loaded scheduler interval from BD: {interval}s")
                    return interval
                else:
                    self.logger.warning(
                        f"Intervalo inválido na BD ({interval}), usando 15s default"
                    )
                    return 15
            else:
                self.logger.warning(
                    "app_parameters não encontrada na BD, usando 15s default"
                )
                return 15

        except Exception as e:
            self.logger.warning(
                f"Erro ao ler app_parameters, usando 15s default: {e}"
            )
            return 15

    async def update_interval(self, new_interval: int) -> None:
        """
        Update scheduler interval at runtime.
        Reschedules the automation_cycle job immediately.

        Args:
            new_interval: New interval in seconds (minimum 5)

        Raises:
            ValueError: If interval < 5
        """
        if new_interval < 5:
            raise ValueError("Intervalo mínimo é 5 segundos")

        try:
            from db.supabase_client import get_db

            db = get_db()

            # Get the singleton row first
            result = db.client.table("app_parameters").select("id").execute()
            if not result.data:
                self.logger.error("app_parameters não encontrada na BD")
                raise ValueError("app_parameters não encontrada")

            param_id = result.data[0]["id"]

            # Update database via Supabase
            update_result = db.client.table("app_parameters").update({
                "scheduler_interval_seconds": new_interval
            }).eq("id", param_id).execute()

            if not update_result.data:
                self.logger.error("Falha ao atualizar app_parameters")
                raise ValueError("Falha ao atualizar app_parameters")

            self.logger.info(
                f"[DEBUG] Updated app_parameters in Supabase: {new_interval}s"
            )

            # Reschedule job if scheduler is running
            if self.scheduler.running:
                self.scheduler.reschedule_job(
                    "automation_cycle",
                    trigger=IntervalTrigger(seconds=new_interval),
                )
                self.logger.info(
                    f"✅ Intervalo do scheduler atualizado: {new_interval}s"
                )

        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar intervalo: {e}", exc_info=True)
            raise

    def get_status(self) -> dict:
        """Get current scheduler status."""
        return {
            "running": self.is_running,
            "cycle_count": (
                self.automation_engine.cycle_count
                if self.automation_engine
                else 0
            ),
            "last_cycle_start": (
                self.automation_engine.last_cycle_start
                if self.automation_engine
                else None
            ),
            "last_cycle_duration_seconds": (
                self.automation_engine.last_cycle_duration
                if self.automation_engine
                else None
            ),
        }
