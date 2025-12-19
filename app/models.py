import reflex as rx
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class AlertRule(SQLModel, table=True):
    """Database model for defining alert rules."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    parameters: str = Field(default="{}", description="JSON string of rule parameters")
    importance: str = Field(default="medium")
    period_seconds: int = Field(default=60)
    action_config: str = Field(default="{}", description="Configuration for actions")
    comment: Optional[str] = None
    is_active: bool = Field(default=True)
    events: list["AlertEvent"] = Relationship(back_populates="rule")


class AlertEvent(SQLModel, table=True):
    """Database model for recorded alert events."""

    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: int = Field(foreign_key="alertrule.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str
    importance: str
    is_acknowledged: bool = Field(default=False)
    acknowledged_timestamp: Optional[datetime] = None
    action_taken: Optional[str] = None
    comment: Optional[str] = None
    rule: AlertRule = Relationship(back_populates="events")