import reflex as rx
import json
import random
import logging
import math
from datetime import datetime, timedelta
from app.models import AlertRule, AlertEvent

PREDEFINED_TEMPLATES = {
    "Custom": "{}",
    "Price Surge > 10%": '{"metric": "price", "condition": "increase", "threshold_percent": 10, "ticker": "AAPL"}',
    "Volume Spike > 200%": '{"metric": "volume", "condition": "increase", "threshold_percent": 200, "ticker": "NVDA"}',
    "News Sentiment Alert": '{"metric": "sentiment", "condition": "negative", "threshold_score": -0.5, "source": "all"}',
    "Unusual Options Activity": '{"metric": "options_vol", "condition": "unusual", "min_contract_size": 500}',
    "Support/Resistance Break": '{"metric": "technical", "indicator": "breakout", "levels": [150, 200]}',
}


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
    rule_form_name: str = ""
    rule_form_importance: str = "medium"
    rule_form_action: str = ""
    rule_form_period_value: int = 60
    rule_form_period_unit: str = "Minutes"
    rule_form_duration_value: int = 24
    rule_form_duration_unit: str = "Hours"
    rule_form_predefined_type: str = "Custom"
    rule_form_parameters: str = (
        '{"ticker": "AAPL", "metric": "price", "threshold": 150}'
    )
    predefined_rule_options: list[str] = list(PREDEFINED_TEMPLATES.keys())

    def _load_data(self):
        """Refresh data from memory."""
        self._update_stats()

    def _update_stats(self):
        """Update summary statistics from the in-memory lists."""
        self.total_rules = len(self.rules)
        self.active_rules_count = sum((1 for r in self.rules if r.is_active))
        self.total_events = len(self.events)
        self.unacknowledged_events = sum(
            (1 for e in self.events if not e.is_acknowledged)
        )

    live_page: int = 1
    live_page_size: int = 10
    live_sort_col: str = "importance"
    live_sort_desc: bool = True

    @rx.var
    def live_total_pages(self) -> int:
        """Total pages for live blotter."""
        count = 0
        rules_map = {r.id: r for r in self.rules}
        for event in self.events:
            imp = event.importance.lower()
            ts = event.timestamp if event.timestamp else datetime.min
            if imp in ["critical", "high"]:
                if not event.is_acknowledged:
                    count += 1
            else:
                rule = rules_map.get(event.rule_id)
                duration_mins = rule.display_duration_minutes if rule else 1440
                cutoff = self.current_time - timedelta(minutes=duration_mins)
                if ts >= cutoff:
                    count += 1
        return math.ceil(count / self.live_page_size) if self.live_page_size > 0 else 1

    @rx.var
    def live_grid_data(self) -> list[dict]:
        """
        Return formatted data for the Live Blotter Table with Pagination.
        Logic:
           - Serious/High importance: Show until is_acknowledged is True
           - Medium/Low importance: Show only if timestamp is within display_duration_minutes
        """
        filtered_data = []
        rules_map = {r.id: r for r in self.rules}
        for event in self.events:
            keep = False
            imp = event.importance.lower()
            ts = event.timestamp if event.timestamp else datetime.min
            if imp in ["critical", "high"]:
                if not event.is_acknowledged:
                    keep = True
            else:
                rule = rules_map.get(event.rule_id)
                duration_mins = rule.display_duration_minutes if rule else 1440
                cutoff = self.current_time - timedelta(minutes=duration_mins)
                if ts >= cutoff:
                    keep = True
            if keep:
                status_text = "Acknowledged" if event.is_acknowledged else "Pending"
                filtered_data.append(
                    {
                        "id": event.id,
                        "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "importance": event.importance.upper(),
                        "message": event.message,
                        "status": status_text,
                        "is_acknowledged": event.is_acknowledged,
                    }
                )
        reverse = self.live_sort_desc
        if self.live_sort_col == "importance":
            importance_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            filtered_data.sort(
                key=lambda x: (importance_map.get(x["importance"], 0), x["timestamp"]),
                reverse=reverse,
            )
        elif self.live_sort_col == "timestamp":
            filtered_data.sort(key=lambda x: x["timestamp"], reverse=reverse)
        elif self.live_sort_col == "message":
            filtered_data.sort(key=lambda x: x["message"], reverse=reverse)
        elif self.live_sort_col == "status":
            filtered_data.sort(key=lambda x: x["status"], reverse=reverse)
        start = (self.live_page - 1) * self.live_page_size
        end = start + self.live_page_size
        return filtered_data[start:end]

    @rx.event
    def next_live_page(self):
        if self.live_page < self.live_total_pages:
            self.live_page += 1

    @rx.event
    def prev_live_page(self):
        if self.live_page > 1:
            self.live_page -= 1

    @rx.event
    def set_live_sort(self, col: str):
        if self.live_sort_col == col:
            self.live_sort_desc = not self.live_sort_desc
        else:
            self.live_sort_col = col
            self.live_sort_desc = True

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
            updated_events = []
            for event in self.events:
                if event.id == self.selected_event_id:
                    event.is_acknowledged = True
                    event.acknowledged_timestamp = datetime.utcnow()
                    event.comment = self.acknowledgement_comment
                updated_events.append(event)
            self.events = updated_events
            self.selected_event_id = -1
            self._load_data()

    def _initialize_db(self):
        """Initialize mock data if empty."""
        if not self.rules:
            rules = [
                AlertRule(
                    id=1,
                    name="High CPU Usage",
                    parameters=json.dumps(
                        {"metric": "cpu", "threshold": 90, "ticker": "SRV-001"}
                    ),
                    importance="high",
                    period_seconds=300,
                    display_duration_minutes=1440,
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
                    display_duration_minutes=720,
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
                    display_duration_minutes=2880,
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
                    display_duration_minutes=60,
                    action_config=json.dumps({"log": "true"}),
                    comment="Performance degradation check",
                    is_active=False,
                ),
            ]
            self.rules = rules
        self._load_data()

    @rx.event
    def generate_mock_alerts(self):
        """Generate random mock alert events based on active rules."""
        new_events_count = 0
        active_rules = [r for r in self.rules if r.is_active]
        events_to_add = []
        current_max_id = 0
        if self.events:
            current_max_id = max([e.id for e in self.events if e.id is not None] or [0])
        for rule in active_rules:
            if random.random() < 0.4:
                try:
                    params = json.loads(rule.parameters)
                    ticker = params.get("ticker", "UNKNOWN")
                    metric = params.get("metric", "unknown_metric")
                    threshold = params.get("threshold", 0)
                    current_value = threshold + random.randint(1, 20)
                    message = f"Alert triggered for {ticker}: {metric} is {current_value} (Threshold: {threshold})"
                    current_max_id += 1
                    event = AlertEvent(
                        id=current_max_id,
                        rule_id=rule.id,
                        message=message,
                        importance=rule.importance,
                        timestamp=datetime.utcnow(),
                        is_acknowledged=False,
                    )
                    events_to_add.append(event)
                    new_events_count += 1
                except json.JSONDecodeError as e:
                    logging.exception(
                        f"Error decoding JSON parameters for rule {rule.id}: {e}"
                    )
                    continue
        if events_to_add:
            self.events = self.events + events_to_add
            self._load_data()
            return rx.toast.info(f"Generated {new_events_count} new mock alerts.")
        else:
            return rx.toast.info("No alerts generated this time.")

    @rx.event
    def set_rule_form_predefined_type(self, value: str):
        """Set the predefined rule type and auto-populate parameters."""
        self.rule_form_predefined_type = value
        self.rule_form_parameters = PREDEFINED_TEMPLATES.get(value, "{}")

    @rx.event
    def add_rule(self):
        """Create a new alert rule from form data."""
        try:
            json.loads(self.rule_form_parameters)
        except json.JSONDecodeError as e:
            logging.exception(f"Invalid JSON in parameters field: {e}")
            return rx.toast.error("Invalid JSON in parameters field.")
        if not self.rule_form_name:
            return rx.toast.error("Rule Name is required.")
        period_mult = 60
        if self.rule_form_period_unit == "Hours":
            period_mult = 3600
        elif self.rule_form_period_unit == "Days":
            period_mult = 86400
        period_seconds = self.rule_form_period_value * period_mult
        duration_mult = 60
        if self.rule_form_duration_unit == "Hours":
            duration_mult = 60
        elif self.rule_form_duration_unit == "Days":
            duration_mult = 1440
        elif self.rule_form_duration_unit == "Minutes":
            duration_mult = 1
        display_duration_minutes = self.rule_form_duration_value * duration_mult
        action_config = (
            json.dumps({"action": self.rule_form_action})
            if self.rule_form_action
            else "{}"
        )
        new_id = 1
        if self.rules:
            new_id = max([r.id for r in self.rules if r.id is not None] or [0]) + 1
        new_rule = AlertRule(
            id=new_id,
            name=self.rule_form_name,
            parameters=self.rule_form_parameters,
            importance=self.rule_form_importance,
            period_seconds=period_seconds,
            display_duration_minutes=display_duration_minutes,
            action_config=action_config,
            comment="Manual Entry",
            is_active=True,
        )
        self.rules = self.rules + [new_rule]
        self._load_data()
        self.rule_form_name = ""
        self.rule_form_action = ""
        self.rule_form_importance = "medium"
        self.rule_form_predefined_type = "Custom"
        return rx.toast.success("New alert rule created successfully.")

    @rx.event
    def delete_rule(self, rule_id: int):
        """Delete a rule by ID."""
        self.rules = [r for r in self.rules if r.id != rule_id]
        self._load_data()
        return rx.toast.success("Rule deleted.")

    @rx.event
    def toggle_rule_active(self, rule_id: int):
        """Toggle the active status of a rule."""
        updated_rules = []
        for rule in self.rules:
            if rule.id == rule_id:
                rule.is_active = not rule.is_active
            updated_rules.append(rule)
        self.rules = updated_rules
        self._load_data()

    history_importance_filter: str = "All"
    history_search_query: str = ""
    history_page: int = 1
    history_page_size: int = 10

    def _get_filtered_events(self) -> list[AlertEvent]:
        """Filter events based on current filters (In-Memory)."""
        events = self.events
        if self.history_importance_filter != "All":
            events = [
                e
                for e in events
                if e.importance.lower() == self.history_importance_filter.lower()
            ]
        if self.history_search_query:
            query = self.history_search_query.lower()
            rules_map = {r.id: r for r in self.rules}
            filtered_events = []
            for e in events:
                rule = rules_map.get(e.rule_id)
                rule_name = rule.name.lower() if rule else ""
                rule_params = rule.parameters.lower() if rule else ""
                message = e.message.lower()
                if query in message or query in rule_name or query in rule_params:
                    filtered_events.append(e)
            events = filtered_events
        return events

    @rx.var
    def filtered_history_count(self) -> int:
        """Total count of filtered items."""
        return len(self._get_filtered_events())

    @rx.var
    def history_total_pages(self) -> int:
        """Total pages based on page size."""
        return (
            math.ceil(self.filtered_history_count / self.history_page_size)
            if self.history_page_size > 0
            else 1
        )

    @rx.var
    def history_start_index(self) -> int:
        """Display start index (1-based)."""
        if self.filtered_history_count == 0:
            return 0
        return (self.history_page - 1) * self.history_page_size + 1

    @rx.var
    def history_end_index(self) -> int:
        """Display end index."""
        end = self.history_page * self.history_page_size
        return min(end, self.filtered_history_count)

    @rx.var
    def paginated_history(self) -> list[dict]:
        """Pagination Logic (In-Memory)."""
        filtered_events = self._get_filtered_events()
        filtered_events.sort(key=lambda x: x.timestamp or datetime.min, reverse=True)
        start = (self.history_page - 1) * self.history_page_size
        end = start + self.history_page_size
        page_items = filtered_events[start:end]
        final_results = []
        rules_map = {r.id: r for r in self.rules}
        for event in page_items:
            rule = rules_map.get(event.rule_id)
            ticker = "-"
            if rule:
                try:
                    params = json.loads(rule.parameters)
                    ticker = params.get("ticker", "-")
                except Exception as e:
                    logging.exception(f"Error parsing rule parameters: {e}")
            final_results.append(
                {
                    "id": event.id,
                    "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    if event.timestamp
                    else "",
                    "message": event.message,
                    "importance": event.importance,
                    "is_acknowledged": event.is_acknowledged,
                    "acknowledged_timestamp": event.acknowledged_timestamp.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if event.acknowledged_timestamp
                    else None,
                    "ack_comment": event.comment or "",
                    "ticker": ticker,
                }
            )
        return final_results

    @rx.event
    def next_history_page(self):
        """Go to next page."""
        if self.history_page < self.history_total_pages:
            self.history_page += 1

    @rx.event
    def prev_history_page(self):
        """Go to previous page."""
        if self.history_page > 1:
            self.history_page -= 1

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        async with self:
            self._initialize_db()