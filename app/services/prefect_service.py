import random
import asyncio
from app.models import PREFECT_STATES


class PrefectSyncService:
    """Service to interact with Prefect API (Mocked for now)."""

    @staticmethod
    async def get_batch_flow_run_states(flow_run_ids: list[str]) -> dict[str, str]:
        """Fetch states for multiple flow runs."""
        await asyncio.sleep(0.8)
        results = {}
        for fid in flow_run_ids:
            r = random.random()
            if r < 0.05:
                state = "FAILED"
            elif r < 0.1:
                state = "CRASHED"
            elif r < 0.5:
                state = "COMPLETED"
            elif r < 0.8:
                state = "RUNNING"
            elif r < 0.9:
                state = "SCHEDULED"
            else:
                state = "PENDING"
            results[fid] = state
        return results