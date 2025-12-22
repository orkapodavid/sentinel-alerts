import uuid
import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput
from app.services.prefect_service import PrefectSyncService


class PrefectDeploymentTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Prefect Deployment Runner"

    def get_description(self) -> str:
        return "Invokes a Prefect Deployment and monitors its initial state."

    def get_default_params(self) -> dict:
        return {"deployment_id": "", "flow_name": "Prefect Flow", "parameters": {}}

    async def check(self, params: dict) -> AlertOutput:
        deployment_id = params.get("deployment_id")
        flow_name = params.get("flow_name", "Unknown Flow")
        run_parameters = params.get("parameters", {})
        if not deployment_id:
            return AlertOutput(
                triggered=False,
                importance="low",
                ticker="PREFECT",
                message="Missing deployment_id parameter",
                metadata={},
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )
        flow_run_id = await PrefectSyncService.trigger_deployment(
            deployment_id, run_parameters
        )
        if flow_run_id:
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
                importance="high",
                ticker="PREFECT",
                message=f"Failed to trigger deployment for {flow_name}",
                metadata={},
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            )


if __name__ == "__main__":
    trigger = PrefectDeploymentTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())