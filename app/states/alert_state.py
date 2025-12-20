import reflex as rx
import json
import random
import logging
import math
from datetime import datetime, timedelta
from app.models import AlertRule, AlertEvent, LogEntry

DEFAULT_TEMPLATES = {
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
    next_rule_id: int = 1
    next_event_id: int = 1

    @rx.var
    def total_rules(self) -> int:
        return len(self.rules)

    @rx.var
    def active_rules_count(self) -> int:
        return len([r for r in self.rules if r.is_active])

    @rx.var
    def total_events(self) -> int:
        return len(self.events)

    @rx.var
    def unacknowledged_events(self) -> int:
        return len([e for e in self.events if not e.is_acknowledged])

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
    predefined_templates: dict[str, str] = DEFAULT_TEMPLATES.copy()
    new_template_name: str = ""
    new_template_json: str = ""

    @rx.var
    def predefined_rule_options(self) -> list[str]:
        return list(self.predefined_templates.keys())

    @rx.var
    def template_list(self) -> list[dict]:
        return [
            {"name": k, "json": v}
            for k, v in self.predefined_templates.items()
            if k != "Custom"
        ]

    @rx.event
    def set_new_template_name(self, value: str):
        self.new_template_name = value

    @rx.event
    def set_new_template_json(self, value: str):
        self.new_template_json = value

    @rx.event
    def add_template(self):
        if not self.new_template_name or not self.new_template_json:
            return rx.toast.error("Name and JSON are required.")
        try:
            json.loads(self.new_template_json)
        except json.JSONDecodeError as e:
            logging.exception(f"Invalid JSON format in template: {e}")
            return rx.toast.error("Invalid JSON format.")
        self.predefined_templates[self.new_template_name] = self.new_template_json
        self.predefined_templates = self.predefined_templates.copy()
        self.log_system_event(
            "Template Added", f"Added template: {self.new_template_name}", "info"
        )
        self.new_template_name = ""
        self.new_template_json = ""
        return rx.toast.success("Template added.")

    @rx.event
    def remove_template(self, name: str):
        if name in self.predefined_templates:
            del self.predefined_templates[name]
            self.predefined_templates = self.predefined_templates.copy()
            self.log_system_event(
                "Template Removed", f"Removed template: {name}", "warning"
            )
            return rx.toast.success("Template removed.")

    system_logs: list[LogEntry] = []

    @rx.event
    def log_system_event(self, event_type: str, message: str, level: str = "info"):
        new_log = LogEntry(
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            type=event_type,
            message=message,
            level=level,
        )
        self.system_logs.insert(0, new_log)
        if len(self.system_logs) > 100:
            self.system_logs = self.system_logs[:100]

    def _get_rule_by_id(self, rule_id: int) -> AlertRule | None:
        for r in self.rules:
            if r.id == rule_id:
                return r
        return None

    def _get_event_by_id(self, event_id: int) -> AlertEvent | None:
        for e in self.events:
            if e.id == event_id:
                return e
        return None

    live_sort_column: str = "timestamp"
    live_sort_reverse: bool = True
    live_page: int = 1
    live_page_size: int = 10

    @rx.event
    def sort_live_by(self, col: str):
        if self.live_sort_column == col:
            self.live_sort_reverse = not self.live_sort_reverse
        else:
            self.live_sort_column = col
            if col == "timestamp":
                self.live_sort_reverse = True
            else:
                self.live_sort_reverse = False
        self.live_page = 1

    @rx.event
    def next_live_page(self):
        if self.live_page < self.live_total_pages:
            self.live_page += 1

    @rx.event
    def prev_live_page(self):
        if self.live_page > 1:
            self.live_page -= 1

    @rx.var
    def all_live_events(self) -> list[dict]:
        """
        Return all relevant events for the Live Blotter.
        Filters relevant events in memory.
        """
        data = []
        critical_high = [
            e
            for e in self.events
            if e.importance in ["critical", "high"] and (not e.is_acknowledged)
        ]
        cutoff_24h = self.current_time - timedelta(days=1)
        recent_events = [
            e
            for e in self.events
            if e.importance in ["medium", "low"]
            and (e.timestamp and e.timestamp >= cutoff_24h)
        ]
        merged = {e.id: e for e in critical_high + recent_events}
        all_candidates = list(merged.values())
        all_candidates.sort(
            key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True
        )
        for event in all_candidates:
            keep = False
            if event.importance in ["critical", "high"]:
                keep = True
            else:
                rule = self._get_rule_by_id(event.rule_id)
                duration_mins = rule.display_duration_minutes if rule else 1440
                cutoff = self.current_time - timedelta(minutes=duration_mins)
                if event.timestamp and event.timestamp >= cutoff:
                    keep = True
            if keep:
                status_text = "Acknowledged" if event.is_acknowledged else "Pending"
                data.append(
                    {
                        "id": event.id,
                        "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if event.timestamp
                        else "",
                        "importance": event.importance.upper(),
                        "message": event.message,
                        "status": status_text,
                        "is_acknowledged": event.is_acknowledged,
                    }
                )
        return data

    @rx.var
    def live_events_count(self) -> int:
        return len(self.all_live_events)

    @rx.var
    def live_total_pages(self) -> int:
        return (
            math.ceil(self.live_events_count / self.live_page_size)
            if self.live_page_size > 0
            else 1
        )

    @rx.var
    def paginated_live_events(self) -> list[dict]:
        items = self.all_live_events[:]
        col = self.live_sort_column
        reverse = self.live_sort_reverse

        @rx.event
        def sort_key(item):
            val = item.get(col, "")
            if col == "importance":
                order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
                return order.get(str(val).upper(), -1)
            return val

        items.sort(key=sort_key, reverse=reverse)
        start = (self.live_page - 1) * self.live_page_size
        end = start + self.live_page_size
        return items[start:end]

    @rx.var
    def live_start_index(self) -> int:
        if self.live_events_count == 0:
            return 0
        return (self.live_page - 1) * self.live_page_size + 1

    @rx.var
    def live_end_index(self) -> int:
        end = self.live_page * self.live_page_size
        return min(end, self.live_events_count)

    @rx.event
    def tick(self, _=None):
        """Update current time."""
        self.current_time = datetime.utcnow()

    @rx.event
    def open_acknowledge_modal(self, event_id: int):
        self.selected_event_id = event_id
        self.acknowledgement_comment = ""

    @rx.event
    def cancel_acknowledgement(self):
        self.selected_event_id = -1

    @rx.event
    def submit_acknowledgement(self):
        if self.selected_event_id != -1:
            event = self._get_event_by_id(self.selected_event_id)
            if event:
                event.is_acknowledged = True
                event.acknowledged_timestamp = datetime.utcnow()
                event.comment = self.acknowledgement_comment
                self.events = list(self.events)
                self.log_system_event(
                    "Event Acknowledged", f"Acknowledged event {event.id}", "success"
                )
            self.selected_event_id = -1
            self._refresh_history()

    def _initialize_db(self):
        """Initialize mock data if empty."""
        if not self.rules:
            rules_data = [
                dict(
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
                dict(
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
                dict(
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
                dict(
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
            for r_data in rules_data:
                r = AlertRule(id=self.next_rule_id, **r_data)
                self.next_rule_id += 1
                self.rules.append(r)
            self._refresh_history()

    @rx.event
    def generate_mock_alerts(self):
        """Generate random mock alert events."""
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
                        id=self.next_event_id,
                        rule_id=rule.id,
                        message=message,
                        importance=rule.importance,
                        timestamp=datetime.utcnow(),
                        is_acknowledged=False,
                    )
                    self.next_event_id += 1
                    self.events.append(event)
                    new_events_count += 1
                except Exception as e:
                    logging.exception(f"Error generating mock event: {e}")
                    continue
        if new_events_count > 0:
            self.events = list(self.events)
            self._refresh_history()
            self.log_system_event(
                "Mock Data", f"Generated {new_events_count} mock alerts", "info"
            )
            return rx.toast.info(f"Generated {new_events_count} new mock alerts.")
        else:
            return rx.toast.info("No alerts generated this time.")

    @rx.event
    def set_rule_form_predefined_type(self, value: str):
        self.rule_form_predefined_type = value
        self.rule_form_parameters = self.predefined_templates.get(value, "{}")

    @rx.event
    def add_rule(self):
        try:
            json.loads(self.rule_form_parameters)
        except json.JSONDecodeError as e:
            logging.exception(f"Error decoding JSON parameters: {e}")
            return rx.toast.error("Invalid JSON parameters.")
        if not self.rule_form_name:
            return rx.toast.error("Rule Name is required.")
        period_mult = {"Minutes": 60, "Hours": 3600, "Days": 86400}.get(
            self.rule_form_period_unit, 60
        )
        period_seconds = self.rule_form_period_value * period_mult
        duration_mult = {"Minutes": 1, "Hours": 60, "Days": 1440}.get(
            self.rule_form_duration_unit, 60
        )
        display_duration_minutes = self.rule_form_duration_value * duration_mult
        action_config = (
            json.dumps({"action": self.rule_form_action})
            if self.rule_form_action
            else "{}"
        )
        new_rule = AlertRule(
            id=self.next_rule_id,
            name=self.rule_form_name,
            parameters=self.rule_form_parameters,
            importance=self.rule_form_importance,
            period_seconds=period_seconds,
            display_duration_minutes=display_duration_minutes,
            action_config=action_config,
            comment="Manual Entry",
            is_active=True,
        )
        self.next_rule_id += 1
        self.rules.append(new_rule)
        self.rules = list(self.rules)
        self.log_system_event(
            "Rule Created", f"Created rule: {new_rule.name}", "success"
        )
        self.rule_form_name = ""
        self.rule_form_action = ""
        return rx.toast.success("Rule created.")

    @rx.event
    def delete_rule(self, rule_id: int):
        rule = self._get_rule_by_id(rule_id)
        if rule:
            self.rules.remove(rule)
            self.rules = list(self.rules)
            self.log_system_event(
                "Rule Deleted", f"Deleted rule: {rule.name}", "warning"
            )
        return rx.toast.success("Rule deleted.")

    @rx.event
    def toggle_rule_active(self, rule_id: int):
        rule = self._get_rule_by_id(rule_id)
        if rule:
            rule.is_active = not rule.is_active
            status = "activated" if rule.is_active else "deactivated"
            self.log_system_event("Rule Updated", f"Rule {rule.name} {status}", "info")
            self.rules = list(self.rules)

    history_importance_filter: str = "All"
    history_search_query: str = ""
    history_page: int = 1
    history_page_size: int = 10
    paginated_history: list[dict] = []
    filtered_history_count: int = 0

    def _refresh_history(self):
        """Perform memory search and pagination."""
        filtered = self.events
        if self.history_importance_filter != "All":
            filtered = [
                e
                for e in filtered
                if e.importance == self.history_importance_filter.lower()
            ]
        if self.history_search_query:
            q = self.history_search_query.lower()
            filtered = [e for e in filtered if q in e.message.lower()]
        self.filtered_history_count = len(filtered)
        filtered.sort(
            key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True
        )
        start = (self.history_page - 1) * self.history_page_size
        end = start + self.history_page_size
        page_items = filtered[start:end]
        final_results = []
        for event in page_items:
            rule = self._get_rule_by_id(event.rule_id)
            ticker = "-"
            if rule:
                try:
                    params = json.loads(rule.parameters)
                    ticker = params.get("ticker", "-")
                except Exception as e:
                    logging.exception(
                        f"Error parsing parameters for rule {rule.id}: {e}"
                    )
                    pass
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
        self.paginated_history = final_results

    @rx.var
    def history_total_pages(self) -> int:
        return (
            math.ceil(self.filtered_history_count / self.history_page_size)
            if self.history_page_size > 0
            else 1
        )

    @rx.var
    def history_start_index(self) -> int:
        if self.filtered_history_count == 0:
            return 0
        return (self.history_page - 1) * self.history_page_size + 1

    @rx.var
    def history_end_index(self) -> int:
        end = self.history_page * self.history_page_size
        return min(end, self.filtered_history_count)

    @rx.event
    def next_history_page(self):
        if self.history_page < self.history_total_pages:
            self.history_page += 1
            self._refresh_history()

    @rx.event
    def prev_history_page(self):
        if self.history_page > 1:
            self.history_page -= 1
            self._refresh_history()

    @rx.event
    def set_history_search_query(self, value: str):
        self.history_search_query = value
        self.history_page = 1
        self._refresh_history()

    @rx.event
    def set_history_importance_filter(self, value: str):
        self.history_importance_filter = value
        self.history_page = 1
        self._refresh_history()

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        async with self:
            self._initialize_db()
            self._refresh_history()