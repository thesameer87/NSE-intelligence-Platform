import asyncio

import pytest

from backend.orchestrator.interfaces import ISchedulerTask
from backend.orchestrator.scheduler import MarketScheduler


class MockTask(ISchedulerTask):
    """A mock task that tracks execution count."""

    def __init__(self, name: str, fail_on_run: int = -1):
        self._name = name
        self.execution_count = 0
        self.fail_on_run = fail_on_run

    @property
    def name(self) -> str:
        return self._name

    async def execute(self) -> None:
        self.execution_count += 1
        if self.execution_count == self.fail_on_run:
            raise ValueError(f"Simulated failure for {self.name}")


@pytest.mark.asyncio
async def test_scheduler_lifecycle() -> None:
    """Test start, stop, and interval timing of the scheduler."""
    mock_task = MockTask(name="TestTask")

    # Use a very short interval for tests
    scheduler = MarketScheduler(interval_seconds=1, tasks=[mock_task])

    assert not scheduler.is_running

    await scheduler.start()
    assert scheduler.is_running

    # Wait for the scheduler to loop at least twice
    await asyncio.sleep(1.5)

    await scheduler.stop()
    assert not scheduler.is_running

    # Check that execution happened at least twice (initial + 1 interval)
    assert mock_task.execution_count >= 2


@pytest.mark.asyncio
async def test_scheduler_failure_isolation() -> None:
    """Test that one failing task does not crash the scheduler."""
    # Task 1 will fail on its first run
    failing_task = MockTask(name="FailingTask", fail_on_run=1)
    
    # Task 2 will never fail
    stable_task = MockTask(name="StableTask")

    scheduler = MarketScheduler(interval_seconds=1, tasks=[failing_task, stable_task])
    await scheduler.start()

    # Wait for the scheduler to loop twice
    await asyncio.sleep(1.5)

    await scheduler.stop()

    # The failing task should have run twice (it failed once, but loop continued)
    assert failing_task.execution_count >= 2

    # The stable task should also have run twice, unaffected by the failure
    assert stable_task.execution_count >= 2



