import abc
from app.models import AlertOutput


class BaseTrigger(abc.ABC):
    """Abstract base class for all alert triggers."""

    @abc.abstractmethod
    async def check(self, params: dict) -> AlertOutput:
        """Run the check logic and return an AlertOutput."""
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the display name of the trigger."""
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        """Return a short description of what the trigger does."""
        pass

    @abc.abstractmethod
    def get_default_params(self) -> dict:
        """Return default parameters for UI population."""
        pass