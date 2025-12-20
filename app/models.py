import reflex as rx
from datetime import datetime
from typing import Optional


class AlertRule(rx.Base):
    """Data model for defining alert rules."""

    id: int
    name: str
    parameters: str = "{}"
    importance: str = "medium"
    period_seconds: int = 60
    display_duration_minutes: int = 1440
    action_config: str = "{}"
    comment: Optional[str] = None
    is_active: bool = True


class AlertEvent(rx.Base):
    """Data model for recorded alert events."""

    id: int
    rule_id: int
    timestamp: Optional[datetime] = None
    message: str
    importance: str
    is_acknowledged: bool = False
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None