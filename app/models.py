import reflex as rx
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class AlertRule(SQLModel, table=True):
    """Data model for defining alert rules."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parameters: str = "{}"
    importance: str = "medium"
    period_seconds: int = 60
    display_duration_minutes: int = 1440
    action_config: str = "{}"
    comment: Optional[str] = None
    is_active: bool = True


class AlertEvent(SQLModel, table=True):
    """Data model for recorded alert events."""

    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str
    importance: str
    is_acknowledged: bool = False
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None