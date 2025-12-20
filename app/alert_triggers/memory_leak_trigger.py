import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class MemoryLeakTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Memory Leak Detector"

    def get_description(self) -> str:
        return "Monitors memory usage trends for potential leaks."

    def get_default_params(self) -> dict:
        return {"service": "api-gateway", "limit_mb": 512}

    def check(self, params: dict) -> AlertOutput:
        service = params.get("service", "unknown")
        limit = float(params.get("limit_mb", 512))
        used = limit * random.uniform(0.6, 1.2)
        triggered = used > limit
        return AlertOutput(
            triggered=triggered,
            importance="medium",
            ticker=service,
            message=f"Potential Memory Leak in {service}: {used:.1f}MB used (Limit: {limit}MB)",
            metadata={"used_mb": used, "limit_mb": limit},
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    trigger = MemoryLeakTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())