import reflex as rx
from datetime import datetime
from typing import Optional


class AlertRule(rx.Base):
    """Data model for defining alert rules."""

    id: Optional[int] = None
    name: str
    parameters: str = "{}"
    importance: str = "medium"
    period_seconds: int = 60
    action_config: str = "{}"
    comment: Optional[str] = None
    is_active: bool = True


class AlertEvent(rx.Base):
    """Data model for recorded alert events."""

    id: Optional[int] = None
    rule_id: int
    timestamp: datetime
    message: str
    importance: str
    is_acknowledged: bool = False
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None