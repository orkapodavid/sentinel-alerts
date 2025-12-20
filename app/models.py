import reflex as rx
from datetime import datetime
from typing import Optional


class AlertRule(rx.Base):
    """Data model for defining alert rules."""

    id: int = 0
    name: str = ""
    parameters: str = "{}"
    importance: str = "medium"
    period_seconds: int = 60
    display_duration_minutes: int = 1440
    action_config: str = "{}"
    comment: Optional[str] = None
    is_active: bool = True
    trigger_script: str = "custom"
    last_output: Optional[str] = None


class AlertEvent(rx.Base):
    """Data model for recorded alert events."""

    id: int = 0
    rule_id: int = 0
    timestamp: Optional[datetime] = None
    message: str = ""
    importance: str = "medium"
    is_acknowledged: bool = False
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None


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