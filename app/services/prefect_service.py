import logging
import uuid
import asyncio
import os

try:
    from prefect.client.orchestration import get_client
    from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId
except ImportError as e:
    logging.exception(f"Optional dependency 'prefect' not found: {e}")
    get_client = None
from app.models import PREFECT_STATES


class PrefectSyncService:
    """Service to interact with Prefect API."""

    DEFAULT_API_URL = "http://localhost:4200/api"

    @staticmethod
    def _get_api_url() -> str:
        return os.environ.get("PREFECT_API_URL", PrefectSyncService.DEFAULT_API_URL)

    @staticmethod
    async def get_batch_flow_run_states(flow_run_ids: list[str]) -> dict[str, str]:
        """Fetch states for multiple flow runs."""
        if not get_client:
            logging.warning(
                "Prefect client not available (prefect package not installed or import failed)."
            )
            return {}
        valid_uuids = []
        for fid in flow_run_ids:
            try:
                valid_uuids.append(uuid.UUID(fid))
            except ValueError as e:
                logging.exception(f"Skipping invalid UUID '{fid}': {e}")
                continue
        if not valid_uuids:
            return {}
        try:
            async with get_client(api_url=PrefectSyncService._get_api_url()) as client:
                runs = await client.read_flow_runs(
                    flow_run_filter=FlowRunFilter(id=FlowRunFilterId(any_=valid_uuids))
                )
                return {str(run.id): run.state.name for run in runs}
        except Exception as e:
            logging.exception(f"Error fetching Prefect flow runs: {e}")
            return {}

    @staticmethod
    async def get_deployments() -> list[dict]:
        """Fetch all available deployments."""
        if not get_client:
            return []
        try:
            async with get_client(api_url=PrefectSyncService._get_api_url()) as client:
                deployments = await client.read_deployments()
                return [
                    {"id": str(d.id), "name": d.name, "flow_id": str(d.flow_id)}
                    for d in deployments
                ]
        except Exception as e:
            logging.exception(f"Error fetching Prefect deployments: {e}")
            return []

    @staticmethod
    async def trigger_deployment(
        deployment_id: str, parameters: dict = None
    ) -> str | None:
        """Trigger a deployment by ID."""
        if not get_client:
            logging.warning("Prefect client not available, cannot trigger deployment.")
            return None
        try:
            async with get_client(api_url=PrefectSyncService._get_api_url()) as client:
                dep_uuid = uuid.UUID(deployment_id)
                deployment = await client.read_deployment(dep_uuid)
                flow_run = await client.create_flow_run_from_deployment(
                    deployment.id, parameters=parameters or {}
                )
                return str(flow_run.id)
        except Exception as e:
            logging.exception(f"Error triggering deployment {deployment_id}: {e}")
            return None

    @staticmethod
    async def check_connection(api_url: str = None) -> dict:
        """Check if Prefect API is accessible."""
        if not get_client:
            return {"success": False, "error": "Prefect package not installed"}
        target_url = (
            api_url
            if api_url
            else os.environ.get("PREFECT_API_URL", PrefectSyncService.DEFAULT_API_URL)
        )
        try:
            async with get_client(api_url=target_url) as client:
                await client.hello()
                return {"success": True, "message": "Connected to Prefect"}
        except Exception as e:
            logging.exception(f"Error checking Prefect connection: {e}")
            msg = str(e)
            if "Connection refused" in msg or "ConnectError" in msg:
                return {
                    "success": False,
                    "error": f"Connection refused at {target_url}. Is the server running?",
                }
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_ui_url(flow_run_id: str, base_url: str = "http://localhost:4200") -> str:
        """Get the UI URL for a flow run."""
        return f"{base_url}/flow-runs/flow-run/{flow_run_id}"