import reflex as rx
import json
import random
import logging
from datetime import datetime
from app.models import AlertRule, AlertEvent


class AlertState(rx.State):
    """State management for Alerts and Rules."""

    rules: list[AlertRule] = []
    events: list[AlertEvent] = []
    total_rules: int = 0
    active_rules_count: int = 0
    total_events: int = 0
    unacknowledged_events: int = 0

    def _update_stats(self):
        """Update summary statistics."""
        self.total_rules = len(self.rules)
        self.active_rules_count = len([r for r in self.rules if r.is_active])
        self.total_events = len(self.events)
        self.unacknowledged_events = len(
            [e for e in self.events if not e.is_acknowledged]
        )

    def _initialize_db(self):
        """Initialize mock data if empty."""
        if not self.rules:
            self.rules = [
                AlertRule(
                    id=1,
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
                    id=2,
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
                    id=3,
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
                    id=4,
                    name="API Latency Spike",
                    parameters=json.dumps(
                        {"metric": "latency", "threshold": 500, "ticker": "API-GATEWAY"}
                    ),
                    importance="low",
                    period_seconds=60,
                    action_config=json.dumps({"log": "true"}),
                    comment="Performance degradation check",
                    is_active=False,
                ),
            ]
        self._update_stats()

    @rx.event
    def generate_mock_alerts(self):
        """Generate random mock alert events based on active rules."""
        active_rules = [r for r in self.rules if r.is_active]
        new_events = []
        next_id = 1
        if self.events:
            next_id = max((e.id or 0 for e in self.events)) + 1
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
                        id=next_id,
                        rule_id=rule.id,
                        message=message,
                        importance=rule.importance,
                        timestamp=datetime.utcnow(),
                        is_acknowledged=False,
                    )
                    new_events.append(event)
                    next_id += 1
                except json.JSONDecodeError as e:
                    logging.exception(
                        f"Error decoding JSON parameters for rule {rule.id}: {e}"
                    )
                    continue
        if new_events:
            self.events = new_events + self.events
            self._update_stats()
            yield rx.toast.info(f"Generated {len(new_events)} new mock alerts.")
        else:
            yield rx.toast.info("No alerts generated this time.")

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        async with self:
            self._initialize_db()