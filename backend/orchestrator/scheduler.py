import asyncio
from typing import Optional

from backend.orchestrator.interfaces import ISchedulerTask
from backend.utils.logger import logger


class MarketScheduler:
    """
    Async-safe deterministic orchestrator.
    Controls the execution loop of all registered tasks.
    """

    def __init__(self, interval_seconds: int, tasks: list[ISchedulerTask]) -> None:
        self.interval_seconds = interval_seconds
        self.tasks = tasks
        self._is_running = False
        self._main_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Starts the orchestration loop."""
        if self._is_running:
            logger.warning("Scheduler is already running.")
            return

        self._is_running = True
        logger.info(
            f"Starting orchestration scheduler (Interval: {self.interval_seconds}s)"
        )

        # We start the loop in a background task
        loop = asyncio.get_running_loop()
        self._main_task = loop.create_task(self._run_loop())

    async def stop(self) -> None:
        """Gracefully stops the orchestration loop."""
        if not self._is_running:
            return

        logger.info("Stopping orchestration scheduler...")
        self._is_running = False

        if self._main_task and not self._main_task.done():
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass

        logger.info("Orchestration scheduler stopped gracefully.")

    @property
    def is_running(self) -> bool:
        """Returns True if the scheduler is actively running."""
        return self._is_running

    async def _run_loop(self) -> None:
        """Core execution loop with deterministic failure isolation."""
        while self._is_running:
            for task in self.tasks:
                if not self._is_running:
                    break
                    
                try:
                    await task.execute()
                except Exception as e:
                    # Deterministic failure isolation: 
                    # one task failure must not crash the entire orchestrator
                    logger.exception(f"Task '{task.name}' failed during execution: {e}")
            
            if self._is_running:
                await asyncio.sleep(self.interval_seconds)
