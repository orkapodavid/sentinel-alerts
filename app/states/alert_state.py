import reflex as rx
import json
import random
import logging
from datetime import datetime, timedelta
from app.models import AlertRule, AlertEvent


class AlertState(rx.State):
    """State management for Alerts and Rules."""

    rules: list[AlertRule] = []
    events: list[AlertEvent] = []
    total_rules: int = 0
    active_rules_count: int = 0
    total_events: int = 0
    unacknowledged_events: int = 0
    current_time: datetime = datetime.utcnow()
    selected_event_id: int = -1
    acknowledgement_comment: str = ""

    @rx.var
    def displayed_events(self) -> list[AlertEvent]:
        """
        Filter and sort events for the Live Blotter.
        Filter Logic:
           - Serious/High importance: Show until is_acknowledged is True
           - Medium/Low importance: Show only if timestamp is within last 24 hours
        Sorting:
           - Primary: Importance (Serious=4, High=3, Med=2, Low=1)
           - Secondary: Timestamp (Descending)
        """
        filtered = []
        cutoff = self.current_time - timedelta(hours=24)
        importance_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        for event in self.events:
            keep = False
            imp = event.importance.lower()
            ts = event.timestamp if event.timestamp else datetime.min
            if imp in ["critical", "high"]:
                if not event.is_acknowledged:
                    keep = True
            elif ts >= cutoff:
                keep = True
            if keep:
                filtered.append(event)

        @rx.event
        def sort_key(e: AlertEvent):
            imp_score = importance_map.get(e.importance.lower(), 0)
            ts = e.timestamp if e.timestamp else datetime.min
            return (imp_score, ts)

        return sorted(filtered, key=sort_key, reverse=True)

    @rx.event
    def tick(self, _=None):
        """Update current time to refresh relative timestamps."""
        self.current_time = datetime.utcnow()

    @rx.event
    def open_acknowledge_modal(self, event_id: int):
        """Open the acknowledgment modal for a specific event."""
        self.selected_event_id = event_id
        self.acknowledgement_comment = ""

    @rx.event
    def cancel_acknowledgement(self):
        """Close the modal without saving."""
        self.selected_event_id = -1

    @rx.event
    def submit_acknowledgement(self):
        """Mark event as acknowledged and save comment."""
        if self.selected_event_id != -1:
            new_events = []
            for e in self.events:
                if e.id == self.selected_event_id:
                    e.is_acknowledged = True
                    e.acknowledged_timestamp = datetime.utcnow()
                    e.comment = self.acknowledgement_comment
                new_events.append(e)
            self.events = new_events
            self.selected_event_id = -1
            self._update_stats()

    def _update_stats(self):
        """Update summary statistics from the in-memory lists."""
        self.total_rules = len(self.rules)
        self.active_rules_count = sum((1 for r in self.rules if r.is_active))
        self.total_events = len(self.events)
        self.unacknowledged_events = sum(
            (1 for e in self.events if not e.is_acknowledged)
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
        new_events_count = 0
        active_rules = [r for r in self.rules if r.is_active]
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
                        id=len(self.events) + 1,
                        rule_id=rule.id,
                        message=message,
                        importance=rule.importance,
                        timestamp=datetime.utcnow(),
                        is_acknowledged=False,
                    )
                    self.events.append(event)
                    new_events_count += 1
                except json.JSONDecodeError as e:
                    logging.exception(
                        f"Error decoding JSON parameters for rule {rule.id}: {e}"
                    )
                    continue
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