import reflex as rx
import json
import random
import asyncio
import logging
from datetime import datetime
from sqlmodel import select
from app.models import AlertRule, AlertEvent


class AlertState(rx.State):
    """State management for Alerts and Rules."""

    rules: list[AlertRule] = []
    events: list[AlertEvent] = []
    total_rules: int = 0
    active_rules_count: int = 0
    total_events: int = 0
    unacknowledged_events: int = 0

    @rx.event
    async def initialize_db(self):
        """Initialize database with seed data if empty."""
        with rx.session() as session:
            result = session.exec(select(AlertRule))
            existing_rules = result.all()
            if not existing_rules:
                seed_rules = [
                    AlertRule(
                        name="High CPU Usage",
                        parameters=json.dumps(
                            {"metric": "cpu", "threshold": 90, "ticker": "SRV-001"}
                        ),
                        importance="high",
                        period_seconds=300,
                        action_config=json.dumps({"email": "admin@example.com"}),
                        comment="Critical server monitoring",
                        is_active=True,
                    ),
                    AlertRule(
                        name="Memory Leak Warning",
                        parameters=json.dumps(
                            {"metric": "memory", "threshold": 85, "ticker": "SRV-DB-02"}
                        ),
                        importance="medium",
                        period_seconds=600,
                        action_config=json.dumps({"slack": "#dev-ops"}),
                        comment="Monitor for potential leaks",
                        is_active=True,
                    ),
                    AlertRule(
                        name="Low Disk Space",
                        parameters=json.dumps(
                            {"metric": "disk", "threshold": 10, "ticker": "SRV-STORAGE"}
                        ),
                        importance="critical",
                        period_seconds=3600,
                        action_config=json.dumps({"pagerduty": "urgent"}),
                        comment="Storage capacity warning",
                        is_active=True,
                    ),
                    AlertRule(
                        name="API Latency Spike",
                        parameters=json.dumps(
                            {
                                "metric": "latency",
                                "threshold": 500,
                                "ticker": "API-GATEWAY",
                            }
                        ),
                        importance="low",
                        period_seconds=60,
                        action_config=json.dumps({"log": "true"}),
                        comment="Performance degradation check",
                        is_active=False,
                    ),
                ]
                session.add_all(seed_rules)
                session.commit()
        await self.load_data()

    @rx.event
    async def load_data(self):
        """Load rules and events from the database."""
        with rx.session() as session:
            self.rules = session.exec(select(AlertRule)).all()
            self.events = session.exec(
                select(AlertEvent).order_by(AlertEvent.timestamp.desc())
            ).all()
            self.total_rules = len(self.rules)
            self.active_rules_count = len([r for r in self.rules if r.is_active])
            self.total_events = len(self.events)
            self.unacknowledged_events = len(
                [e for e in self.events if not e.is_acknowledged]
            )

    @rx.event
    async def generate_mock_alerts(self):
        """Generate random mock alert events based on active rules."""
        with rx.session() as session:
            active_rules = session.exec(
                select(AlertRule).where(AlertRule.is_active == True)
            ).all()
            new_events = []
            for rule in active_rules:
                if random.random() < 0.4:
                    try:
                        params = json.loads(rule.parameters)
                        ticker = params.get("ticker", "UNKNOWN")
                        metric = params.get("metric", "unknown_metric")
                        threshold = params.get("threshold", 0)
                        current_value = threshold + random.randint(1, 20)
                        message = f"Alert triggered for {ticker}: {metric} is {current_value} (Threshold: {threshold})"
                        event = AlertEvent(
                            rule_id=rule.id,
                            message=message,
                            importance=rule.importance,
                            timestamp=datetime.utcnow(),
                            is_acknowledged=False,
                        )
                        new_events.append(event)
                    except json.JSONDecodeError as e:
                        logging.exception(
                            f"Error decoding JSON parameters for rule {rule.id}: {e}"
                        )
                        continue
            if new_events:
                session.add_all(new_events)
                session.commit()
        await self.load_data()
        if new_events:
            return rx.toast.info(f"Generated {len(new_events)} new mock alerts.")
        else:
            return rx.toast.info("No alerts generated this time.")

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        async with self:
            await self.initialize_db()