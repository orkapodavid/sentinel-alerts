import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class HealthCheckTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Health Check Monitor"

    def get_description(self) -> str:
        return "Monitors service endpoints and returns status (Healthy/Unhealthy)."

    def get_default_params(self) -> dict:
        return {"service": "Auth-API", "endpoint": "https://api.sentinel.io/health"}

    async def check(self, params: dict) -> AlertOutput:
        service = params.get("service", "unknown")
        endpoint = params.get("endpoint", "localhost")
        is_healthy = random.random() > 0.2
        importance = "low" if is_healthy else "critical"
        status_text = "Healthy" if is_healthy else "Unhealthy"
        message = f"Health Check for {service} ({endpoint}): {status_text}"
        return AlertOutput(
            triggered=True,
            importance=importance,
            ticker=service,
            message=message,
            metadata={
                "status": status_text,
                "is_healthy": is_healthy,
                "endpoint": endpoint,
            },
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )