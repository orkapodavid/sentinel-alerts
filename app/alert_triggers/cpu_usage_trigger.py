import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class CpuUsageTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "CPU Usage Monitor"

    def get_description(self) -> str:
        return "Alerts when CPU usage exceeds critical limits."

    def get_default_params(self) -> dict:
        return {"server": "PROD-DB-01", "threshold": 90}

    async def check(self, params: dict) -> AlertOutput:
        server = params.get("server", "localhost")
        threshold = float(params.get("threshold", 90))
        current_load = random.uniform(10, 100)
        triggered = current_load > threshold
        importance = "critical" if current_load > 95 else "high"
        return AlertOutput(
            triggered=triggered,
            importance=importance,
            ticker=server,
            message=f"High CPU Load on {server}: {current_load:.1f}% (Threshold: {threshold}%)",
            metadata={"load": current_load},
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    trigger = CpuUsageTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())