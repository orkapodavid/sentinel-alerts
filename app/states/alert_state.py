import reflex as rx
import json
import random
import logging
from sqlmodel import select, func
from datetime import datetime
from app.models import AlertRule, AlertEvent


class AlertState(rx.State):
    """State management for Alerts and Rules."""

    total_rules: int = 0
    active_rules_count: int = 0
    total_events: int = 0
    unacknowledged_events: int = 0

    def _update_stats(self):
        """Update summary statistics from the database."""
        with rx.session() as session:
            self.total_rules = session.exec(
                select(func.count()).select_from(AlertRule)
            ).one()
            self.active_rules_count = session.exec(
                select(func.count())
                .select_from(AlertRule)
                .where(AlertRule.is_active == True)
            ).one()
            self.total_events = session.exec(
                select(func.count()).select_from(AlertEvent)
            ).one()
            self.unacknowledged_events = session.exec(
                select(func.count())
                .select_from(AlertEvent)
                .where(AlertEvent.is_acknowledged == False)
            ).one()

    def _initialize_db(self):
        """Initialize mock data if empty."""
        with rx.session() as session:
            count = session.exec(select(func.count()).select_from(AlertRule)).one()
            if count == 0:
                initial_rules = [
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
                for rule in initial_rules:
                    session.add(rule)
                session.commit()
        self._update_stats()

    @rx.event
    def generate_mock_alerts(self):
        """Generate random mock alert events based on active rules."""
        new_events_count = 0
        with rx.session() as session:
            active_rules = session.exec(
                select(AlertRule).where(AlertRule.is_active == True)
            ).all()
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
                        session.add(event)
                        new_events_count += 1
                    except json.JSONDecodeError as e:
                        logging.exception(
                            f"Error decoding JSON parameters for rule {rule.id}: {e}"
                        )
                        continue
            session.commit()
        self._update_stats()
        if new_events_count > 0:
            return rx.toast.info(f"Generated {new_events_count} new mock alerts.")
        else:
            return rx.toast.info("No alerts generated this time.")

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        async with self:
            self._initialize_db()