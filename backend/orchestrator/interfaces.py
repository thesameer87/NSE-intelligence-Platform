from typing import Protocol


class ISchedulerTask(Protocol):
    """
    Protocol defining the required interface for any task
    registered with the orchestrator.
    """

    @property
    def name(self) -> str:
        """The name of the task for logging and tracking."""
        ...

    async def execute(self) -> None:
        """The asynchronous business logic of the task."""
        ...
