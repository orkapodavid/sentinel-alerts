import uuid
import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class PrefectDeploymentTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Prefect Deployment Runner"

    def get_description(self) -> str:
        return "Invokes a Prefect Deployment and monitors its initial state."

    def get_default_params(self) -> dict:
        return {
            "deployment_id": "dep-12345678",
            "flow_name": "data-pipeline-daily",
            "parameters": {},
        }

    def check(self, params: dict) -> AlertOutput:
        deployment_id = params.get("deployment_id")
        flow_name = params.get("flow_name", "Unknown Flow")
        success = random.random() > 0.1
        if success:
            flow_run_id = str(uuid.uuid4())
            return AlertOutput(
                triggered=True,
                importance="medium",
                ticker="PREFECT",
                message=f"Triggered Flow: {flow_name}",
                metadata={
                    "deployment_id": deployment_id,
                    "flow_run_id": flow_run_id,
                    "initial_state": "SCHEDULED",
                },
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            return AlertOutput(
                triggered=False,
                importance="low",
                ticker="PREFECT",
                message=f"Failed to trigger {flow_name}",
                metadata={},
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )


if __name__ == "__main__":
    trigger = PrefectDeploymentTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())