import reflex as rx
from datetime import datetime
from typing import Optional

PREFECT_STATES = [
    "SCHEDULED",
    "PENDING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "CRASHED",
    "PAUSED",
    "CANCELLING",
]


class AlertRule(rx.Base):
    """Data model for defining alert rules."""

    id: int = 0
    name: str = ""
    parameters: str = "{}"
    importance: str = "medium"
    category: str = "General"
    period_seconds: int = 60
    display_duration_minutes: int = 1440
    action_config: str = "{}"
    comment: Optional[str] = None
    is_active: bool = True
    trigger_script: str = "custom"
    last_output: Optional[str] = None
    prefect_deployment_id: Optional[str] = None
    prefect_flow_name: Optional[str] = None
    schedule_cron: Optional[str] = None


class AlertEvent(rx.Base):
    """Data model for recorded alert events."""

    id: int = 0
    rule_id: int = 0
    timestamp: Optional[datetime] = None
    message: str = ""
    importance: str = "medium"
    category: str = "General"
    is_acknowledged: bool = False
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None
    ticker: Optional[str] = None
    prefect_flow_run_id: Optional[str] = None
    prefect_state: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0


class AlertOutput(rx.Base):
    """Standardized output for alert triggers."""

    triggered: bool
    importance: str
    ticker: str
    message: str
    metadata: dict = {}
    timestamp: str


class LogEntry(rx.Base):
    """Data model for system logs."""

    timestamp: str
    type: str
    message: str
    level: str
    ticker: Optional[str] = None
    importance: Optional[str] = None
    user: str = "Admin User"