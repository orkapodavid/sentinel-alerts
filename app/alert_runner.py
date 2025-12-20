import pkgutil
import importlib
import inspect
import logging
from app import alert_triggers
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class AlertRunner:
    """Utility to discover and run alert triggers."""

    @staticmethod
    def discover_triggers() -> list[dict]:
        """Scan app.alert_triggers for available Trigger classes."""
        triggers = []
        path = alert_triggers.__path__
        prefix = alert_triggers.__name__ + "."
        for _, name, _ in pkgutil.iter_modules(path, prefix):
            try:
                module = importlib.import_module(name)
                for _, item in inspect.getmembers(module):
                    if (
                        inspect.isclass(item)
                        and issubclass(item, BaseTrigger)
                        and (item is not BaseTrigger)
                    ):
                        instance = item()
                        triggers.append(
                            {
                                "name": instance.get_name(),
                                "script": name.split(".")[-1],
                                "description": instance.get_description(),
                                "default_params": instance.get_default_params(),
                            }
                        )
            except Exception as e:
                logging.exception(f"Error loading trigger module {name}: {e}")
        return triggers

    @staticmethod
    def run_trigger(script_name: str, params: dict) -> AlertOutput | None:
        """Execute a specific trigger script."""
        try:
            module_name = f"app.alert_triggers.{script_name}"
            module = importlib.import_module(module_name)
            trigger_class = None
            for _, item in inspect.getmembers(module):
                if (
                    inspect.isclass(item)
                    and issubclass(item, BaseTrigger)
                    and (item is not BaseTrigger)
                ):
                    trigger_class = item
                    break
            if trigger_class:
                instance = trigger_class()
                return instance.check(params)
            else:
                logging.error(f"No BaseTrigger subclass found in {script_name}")
                return None
        except Exception as e:
            logging.exception(f"Error executing trigger {script_name}: {e}")
            return None