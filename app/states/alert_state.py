import reflex as rx
import json
import random
import logging
import math
import asyncio
import uuid
import os
from datetime import datetime, timedelta
from app.models import AlertRule, AlertEvent, LogEntry, PREFECT_STATES
from app.alert_runner import AlertRunner
from app.services.prefect_service import PrefectSyncService


class AlertState(rx.State):
    """State management for Alerts and Rules."""

    rules: list[AlertRule] = []
    events: list[AlertEvent] = []
    next_rule_id: int = 1
    next_event_id: int = 1
    available_triggers: list[dict] = []

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

    @rx.var
    def prefect_stats(self) -> dict[str, int]:
        """Calculate stats for Prefect flows linked to events."""
        running = len([e for e in self.events if e.prefect_state == "RUNNING"])
        failed = len(
            [e for e in self.events if e.prefect_state in ["FAILED", "CRASHED"]]
        )
        completed = len([e for e in self.events if e.prefect_state == "COMPLETED"])
        return {"running": running, "failed": failed, "completed": completed}

    current_time: datetime = datetime.utcnow()
    selected_event_id: int = -1
    acknowledgement_comment: str = ""
    rule_form_name: str = ""
    rule_form_importance: str = "medium"
    rule_form_category: str = "General"
    rule_form_period_value: int = 60
    rule_form_period_unit: str = "Minutes"
    rule_form_duration_value: int = 24
    rule_form_duration_unit: str = "Hours"
    rule_form_trigger_script: str = "custom"
    rule_form_parameters: str = "{}"
    rule_form_action_targets: list[str] = [""]

    @rx.event
    def add_action_target(self):
        self.rule_form_action_targets.append("")

    @rx.event
    def remove_action_target(self, index: int):
        if 0 <= index < len(self.rule_form_action_targets):
            self.rule_form_action_targets.pop(index)

    @rx.event
    def update_action_target(self, index: int, value: str):
        if 0 <= index < len(self.rule_form_action_targets):
            self.rule_form_action_targets[index] = value

    clone_modal_open: bool = False
    clone_search_query: str = ""
    clone_page: int = 1
    clone_page_size: int = 10

    @rx.event
    def open_clone_modal(self):
        self.clone_modal_open = True
        self.clone_search_query = ""
        self.clone_page = 1

    @rx.event
    def close_clone_modal(self):
        self.clone_modal_open = False

    @rx.event
    def set_clone_search_query(self, value: str):
        self.clone_search_query = value
        self.clone_page = 1

    @rx.var
    def clone_filtered_rules(self) -> list[AlertRule]:
        if not self.clone_search_query:
            return self.rules
        q = self.clone_search_query.lower()
        return [r for r in self.rules if q in r.name.lower()]

    @rx.var
    def clone_total_pages(self) -> int:
        return (
            math.ceil(len(self.clone_filtered_rules) / self.clone_page_size)
            if self.clone_page_size > 0
            else 1
        )

    @rx.var
    def clone_paginated_rules(self) -> list[AlertRule]:
        start = (self.clone_page - 1) * self.clone_page_size
        end = start + self.clone_page_size
        return self.clone_filtered_rules[start:end]

    @rx.event
    def next_clone_page(self):
        if self.clone_page < self.clone_total_pages:
            self.clone_page += 1

    @rx.event
    def prev_clone_page(self):
        if self.clone_page > 1:
            self.clone_page -= 1

    @rx.event
    def select_clone_rule(self, rule_id: int):
        rule = self._get_rule_by_id(rule_id)
        if not rule:
            return
        self.rule_form_name = f"Copy of {rule.name}"
        self.rule_form_importance = rule.importance
        self.rule_form_category = rule.category
        self.rule_form_trigger_script = rule.trigger_script
        self.rule_form_parameters = rule.parameters
        if rule.period_seconds % 86400 == 0:
            self.rule_form_period_value = rule.period_seconds // 86400
            self.rule_form_period_unit = "Days"
        elif rule.period_seconds % 3600 == 0:
            self.rule_form_period_value = rule.period_seconds // 3600
            self.rule_form_period_unit = "Hours"
        else:
            self.rule_form_period_value = rule.period_seconds // 60
            self.rule_form_period_unit = "Minutes"
        if rule.display_duration_minutes % 1440 == 0:
            self.rule_form_duration_value = rule.display_duration_minutes // 1440
            self.rule_form_duration_unit = "Days"
        elif rule.display_duration_minutes % 60 == 0:
            self.rule_form_duration_value = rule.display_duration_minutes // 60
            self.rule_form_duration_unit = "Hours"
        else:
            self.rule_form_duration_value = rule.display_duration_minutes
            self.rule_form_duration_unit = "Minutes"
        try:
            config = json.loads(rule.action_config)
            if "emails" in config and isinstance(config["emails"], list):
                self.rule_form_action_targets = config["emails"]
            elif "action" in config and config["action"]:
                self.rule_form_action_targets = [config["action"]]
            else:
                self.rule_form_action_targets = [""]
        except Exception as e:
            logging.exception(f"Error parsing action config for rule cloning: {e}")
            self.rule_form_action_targets = [""]
        if not self.rule_form_action_targets:
            self.rule_form_action_targets = [""]
        self.clone_modal_open = False
        rx.toast.success("Rule settings cloned.")

    @rx.event
    def fetch_available_triggers(self):
        self.available_triggers = AlertRunner.discover_triggers()

    prefect_deployments: list[dict] = []
    prefect_connection_status: bool = False
    prefect_api_url: str = "http://localhost:4200/api"
    prefect_ui_url: str = "http://localhost:4200"
    prefect_status_message: str = "Not checked"

    @rx.event
    def set_prefect_api_url(self, value: str):
        self.prefect_api_url = value
        os.environ["PREFECT_API_URL"] = value

    @rx.event
    def set_prefect_ui_url(self, value: str):
        self.prefect_ui_url = value

    @rx.event
    async def test_prefect_connection(self):
        """Test connectivity to Prefect API."""
        os.environ["PREFECT_API_URL"] = self.prefect_api_url
        result = await PrefectSyncService.check_connection(self.prefect_api_url)
        self.prefect_connection_status = result["success"]
        if self.prefect_connection_status:
            self.prefect_status_message = "Connected"
            rx.toast.success("Prefect API Connected Successfully")
        else:
            self.prefect_status_message = result.get("error", "Connection Failed")
            rx.toast.error(f"Failed: {self.prefect_status_message}")

    @rx.event
    async def fetch_prefect_deployments(self):
        self.prefect_deployments = await PrefectSyncService.get_deployments()

    @rx.event
    def update_rule_form_prefect_deployment(self, deployment_id: str):
        """Update deployment ID in parameters JSON when dropdown changes."""
        try:
            params = json.loads(self.rule_form_parameters)
            params["deployment_id"] = deployment_id
            for d in self.prefect_deployments:
                if d["id"] == deployment_id:
                    params["flow_name"] = d["name"]
                    break
            self.rule_form_parameters = json.dumps(params, indent=2)
        except json.JSONDecodeError as e:
            logging.exception(f"Error updating rule parameters JSON: {e}")

    system_logs: list[LogEntry] = []

    @rx.event
    def log_system_event(
        self,
        event_type: str,
        message: str,
        level: str = "info",
        ticker: str | None = None,
        importance: str | None = None,
        user: str = "Admin User",
    ):
        new_log = LogEntry(
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            type=event_type,
            message=message,
            level=level,
            ticker=ticker,
            importance=importance,
            user=user,
        )
        self.system_logs.insert(0, new_log)
        if len(self.system_logs) > 1000:
            self.system_logs = self.system_logs[:1000]

    log_active_tab: str = "latest"
    log_search_query: str = ""
    log_level_filter: str = "All"
    log_start_date: str = ""
    log_end_date: str = ""
    log_page: int = 1
    log_page_size: int = 15

    @rx.event
    def set_log_active_tab(self, value: str):
        self.log_active_tab = value

    @rx.event
    def set_log_search_query(self, value: str):
        self.log_search_query = value
        self.log_page = 1

    @rx.event
    def set_log_level_filter(self, value: str):
        self.log_level_filter = value
        self.log_page = 1

    @rx.event
    def set_log_start_date(self, value: str):
        self.log_start_date = value
        self.log_page = 1

    @rx.event
    def set_log_end_date(self, value: str):
        self.log_end_date = value
        self.log_page = 1

    @rx.event
    def reset_log_filters(self):
        self.log_search_query = ""
        self.log_level_filter = "All"
        self.log_start_date = ""
        self.log_end_date = ""
        self.log_page = 1

    @rx.var
    def filtered_logs(self) -> list[LogEntry]:
        logs = self.system_logs
        if self.log_level_filter != "All":
            logs = [l for l in logs if l.level.lower() == self.log_level_filter.lower()]
        if self.log_search_query:
            q = self.log_search_query.lower()
            logs = [
                l
                for l in logs
                if q in l.message.lower()
                or q in l.type.lower()
                or (l.ticker and q in l.ticker.lower())
            ]
        if self.log_start_date:
            try:
                s_date = datetime.strptime(self.log_start_date, "%Y-%m-%d")
                logs = [
                    l
                    for l in logs
                    if datetime.strptime(l.timestamp, "%Y-%m-%d %H:%M:%S") >= s_date
                ]
            except ValueError as e:
                logging.exception(f"Error parsing start date: {e}")
        if self.log_end_date:
            try:
                e_date = datetime.strptime(self.log_end_date, "%Y-%m-%d") + timedelta(
                    days=1
                )
                logs = [
                    l
                    for l in logs
                    if datetime.strptime(l.timestamp, "%Y-%m-%d %H:%M:%S") < e_date
                ]
            except ValueError as e:
                logging.exception(f"Error parsing end date: {e}")
        return logs

    @rx.var
    def total_filtered_logs_count(self) -> int:
        return len(self.filtered_logs)

    @rx.var
    def total_log_pages(self) -> int:
        return (
            math.ceil(self.total_filtered_logs_count / self.log_page_size)
            if self.log_page_size > 0
            else 1
        )

    @rx.var
    def paginated_logs(self) -> list[LogEntry]:
        start = (self.log_page - 1) * self.log_page_size
        end = start + self.log_page_size
        return self.filtered_logs[start:end]

    @rx.event
    def next_log_page(self):
        if self.log_page < self.total_log_pages:
            self.log_page += 1

    @rx.event
    def prev_log_page(self):
        if self.log_page > 1:
            self.log_page -= 1

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

    quick_filter: str = "All"
    prefect_state_filter: str = "All"

    @rx.event
    def set_quick_filter(self, value: str):
        self.quick_filter = value
        self.live_page = 1

    @rx.event
    def set_prefect_state_filter(self, value: str):
        self.prefect_state_filter = value
        self.live_page = 1
        self.history_page = 1

    def _get_logo_url(self, ticker: str) -> str:
        """Generate a logo URL for a given ticker or name."""
        if not ticker or ticker == "-":
            return ""
        domain_map = {
            "AAPL": "apple.com",
            "NVDA": "nvidia.com",
            "MSFT": "microsoft.com",
            "GOOGL": "google.com",
            "AMZN": "amazon.com",
            "TSLA": "tesla.com",
            "META": "meta.com",
            "NFLX": "netflix.com",
        }
        domain = domain_map.get(ticker.upper())
        if domain:
            return f"https://logo.clearbit.com/{domain}"
        return f"https://ui-avatars.com/api/?name={ticker}&background=random&color=fff&size=64&font-size=0.4"

    def _serialize_event_for_grid(
        self, event: AlertEvent, for_history: bool = False
    ) -> dict:
        """Unified serializer for both blotters."""
        status_text = "Acknowledged" if event.is_acknowledged else "Pending"
        if for_history:
            action_label = "View Details"
        else:
            action_label = "" if event.is_acknowledged else "ACKNOWLEDGE"
        ticker = event.ticker if event.ticker else "-"
        importance = event.importance if event.importance else "medium"
        category = event.category if event.category else "General"
        prefect_link_text = "View Flow" if event.prefect_flow_run_id else ""
        prefect_ui_url = ""
        if event.prefect_flow_run_id:
            prefect_ui_url = PrefectSyncService.get_ui_url(
                event.prefect_flow_run_id, base_url=self.prefect_ui_url
            )
        return {
            "id": event.id,
            "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if event.timestamp
            else "",
            "importance": importance.upper(),
            "category": category,
            "message": event.message or "",
            "status": status_text,
            "is_acknowledged": event.is_acknowledged,
            "acknowledged_timestamp": event.acknowledged_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if event.acknowledged_timestamp
            else "",
            "ack_comment": event.comment or "",
            "action_label": action_label,
            "ticker": ticker,
            "logo_url": self._get_logo_url(ticker),
            "prefect_state": event.prefect_state or "",
            "prefect_flow_run_id": event.prefect_flow_run_id or "",
            "prefect_link": prefect_link_text,
            "prefect_ui_url": prefect_ui_url,
        }

    @rx.var
    def all_live_events(self) -> list[dict]:
        """
        Return all relevant events for the Live Blotter.
        Filters relevant events in memory based on importance, recency, and quick filters.
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
            if not keep:
                continue
            if self.quick_filter == "Critical":
                if event.importance not in ["critical", "high"]:
                    continue
            elif self.quick_filter == "Market":
                if event.category != "Market":
                    continue
            elif self.quick_filter == "System":
                if event.category != "System":
                    continue
            if self.prefect_state_filter != "All":
                evt_state = event.prefect_state or "None"
                if self.prefect_state_filter == "None":
                    if evt_state != "None":
                        continue
                elif evt_state != self.prefect_state_filter:
                    continue
            data.append(self._serialize_event_for_grid(event, for_history=False))
        return data

    @rx.event
    def handle_live_grid_cell_clicked(self, cell_event: dict):
        """Handle clicks on the AG Grid cells in Live Blotter."""
        col_id = cell_event.get("colDef", {}).get("field")
        row_data = cell_event.get("data", {})
        if col_id == "action_label":
            if not row_data.get("is_acknowledged"):
                event_id = row_data.get("id")
                if event_id:
                    self.open_acknowledge_modal(event_id)
        elif col_id == "prefect_link":
            url = row_data.get("prefect_ui_url")
            if url:
                return rx.redirect(url, is_external=True)

    @rx.event
    def handle_history_grid_cell_clicked(self, cell_event: dict):
        """Handle clicks on the AG Grid cells in History Blotter."""
        col_id = cell_event.get("colDef", {}).get("field")
        row_data = cell_event.get("data", {})
        if col_id == "action_label":
            msg = row_data.get("message", "Event")
            rx.toast.info(f"Details for: {msg}")
        elif col_id == "prefect_link":
            url = row_data.get("prefect_ui_url")
            if url:
                return rx.redirect(url, is_external=True)

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
                log_msg = f"Acknowledged event {event.id}: {event.message}"
                if self.acknowledgement_comment:
                    log_msg += f" | Comment: {self.acknowledgement_comment}"
                self.log_system_event(
                    "Event Acknowledged",
                    log_msg,
                    "success",
                    ticker=event.ticker,
                    importance=event.importance,
                    user="Admin User",
                )
            self.selected_event_id = -1
            self._refresh_history()

    def _initialize_db(self):
        """Initialize mock data if empty."""
        if not self.rules:
            self.log_system_event(
                "System Init",
                "Initializing default rules and mock data...",
                "info",
                user="System",
            )
            rules_data = [
                dict(
                    name="Production CPU Monitor",
                    trigger_script="cpu_usage_trigger",
                    parameters=json.dumps({"server": "PROD-CORE-01", "threshold": 90}),
                    importance="high",
                    category="System",
                    period_seconds=300,
                    display_duration_minutes=1440,
                    action_config=json.dumps({"emails": ["ops@sentinel.io"]}),
                    comment="Critical server monitoring",
                    is_active=True,
                ),
                dict(
                    name="Apple Stock Surge",
                    trigger_script="price_surge_trigger",
                    parameters=json.dumps({"ticker": "AAPL", "threshold": 180.0}),
                    importance="medium",
                    category="Market",
                    period_seconds=60,
                    display_duration_minutes=60,
                    action_config=json.dumps({"emails": ["trading@sentinel.io"]}),
                    comment="Day trading alert",
                    is_active=True,
                ),
                dict(
                    name="NVDA Volume Spike",
                    trigger_script="volume_spike_trigger",
                    parameters=json.dumps({"ticker": "NVDA", "avg_volume": 5000000}),
                    importance="low",
                    category="Market",
                    period_seconds=300,
                    display_duration_minutes=120,
                    action_config=json.dumps({"emails": []}),
                    comment="Volume tracking",
                    is_active=True,
                ),
                dict(
                    name="Daily Data Pipeline",
                    trigger_script="prefect_deployment_trigger",
                    parameters=json.dumps(
                        {
                            "deployment_id": "dep-analytics-01",
                            "flow_name": "etl-daily-batch",
                        }
                    ),
                    importance="medium",
                    category="System",
                    period_seconds=86400,
                    display_duration_minutes=1440,
                    action_config=json.dumps({"emails": ["data-eng@sentinel.io"]}),
                    comment="Triggers daily ETL",
                    is_active=True,
                ),
            ]
            for r_data in rules_data:
                r = AlertRule(id=self.next_rule_id, **r_data)
                self.next_rule_id += 1
                self.rules.append(r)
            categories = ["Market", "System", "Security", "Liquidity", "News"]
            importances = ["critical", "high", "medium", "low"]
            tickers = [
                "AAPL",
                "NVDA",
                "MSFT",
                "TSLA",
                "GOOGL",
                "SYS-01",
                "API-GW",
                "DB-PROD",
            ]
            messages = [
                "High latency detected",
                "Unusual volume spike",
                "Price threshold breached",
                "Connection timeout",
                "Unauthorized access attempt",
                "Liquidity crunch warning",
            ]
            base_time = datetime.utcnow() - timedelta(days=7)
            for i in range(50):
                rule_idx = random.randint(0, len(self.rules) - 1)
                rule = self.rules[rule_idx]
                event_time = base_time + timedelta(hours=random.randint(1, 160))
                ticker = random.choice(tickers)
                evt = AlertEvent(
                    id=self.next_event_id,
                    rule_id=rule.id,
                    timestamp=event_time,
                    message=f"{random.choice(messages)} on {ticker}",
                    importance=random.choice(importances),
                    category=random.choice(categories),
                    is_acknowledged=random.choice([True, False]),
                    comment="Auto-generated history" if random.random() > 0.5 else None,
                    ticker=ticker,
                )
                if evt.is_acknowledged:
                    evt.acknowledged_timestamp = evt.timestamp + timedelta(
                        minutes=random.randint(5, 120)
                    )
                if random.random() < 0.3:
                    evt.prefect_flow_run_id = str(uuid.uuid4())
                    evt.prefect_state = random.choice(
                        ["SCHEDULED", "PENDING", "RUNNING"]
                    )
                self.events.append(evt)
                self.next_event_id += 1
            self.log_system_event(
                "System Init",
                f"Created {len(self.rules)} rules and {len(self.events)} mock events.",
                "success",
                user="System",
            )
            for rule in self.rules:
                self.log_system_event(
                    "Rule Init",
                    f"Initialized rule: {rule.name} ({rule.category})",
                    "info",
                    user="System",
                )
            self._refresh_history()

    @rx.event
    async def generate_mock_alerts(self):
        """Run trigger scripts for active rules."""
        new_events_count = 0
        active_rules = [r for r in self.rules if r.is_active]
        for rule in active_rules:
            try:
                params = json.loads(rule.parameters)
                if rule.trigger_script and rule.trigger_script != "custom":
                    output = await AlertRunner.run_trigger(rule.trigger_script, params)
                    if output:
                        rule.last_output = output.json()
                        if output.triggered:
                            flow_run_id = output.metadata.get("flow_run_id")
                            prefect_state = output.metadata.get("initial_state")
                            event = AlertEvent(
                                id=self.next_event_id,
                                rule_id=rule.id,
                                message=output.message,
                                importance=output.importance.lower(),
                                timestamp=datetime.utcnow(),
                                is_acknowledged=False,
                                category=rule.category,
                                ticker=output.ticker,
                                prefect_flow_run_id=flow_run_id,
                                prefect_state=prefect_state,
                            )
                            self.next_event_id += 1
                            self.events.append(event)
                            new_events_count += 1
            except Exception as e:
                logging.exception(f"Error running trigger for rule {rule.name}: {e}")
                continue
        if new_events_count > 0:
            self.events = list(self.events)
            self._refresh_history()
            triggered_rules = [
                r.name
                for r in active_rules
                if r.last_output and json.loads(r.last_output).get("triggered")
            ]
            triggered_str = ", ".join(triggered_rules) if triggered_rules else "Unknown"
            self.log_system_event(
                "Trigger Execution",
                f"Generated {new_events_count} alerts. Sources: {triggered_str}",
                "info",
                user="System",
            )
            return rx.toast.info(
                f"Generated {new_events_count} new alerts from triggers."
            )
        else:
            return rx.toast.info("Rules executed but no alerts triggered.")

    @rx.event
    def set_rule_form_trigger_script(self, value: str):
        self.rule_form_trigger_script = value
        for trigger in self.available_triggers:
            if trigger["script"] == value:
                self.rule_form_name = trigger["name"]
                self.rule_form_parameters = json.dumps(
                    trigger["default_params"], indent=2
                )
                break

    @rx.event
    def set_rule_form_category(self, value: str):
        self.rule_form_category = value

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
        valid_targets = [t for t in self.rule_form_action_targets if t.strip()]
        action_config = json.dumps({"emails": valid_targets})
        new_rule = AlertRule(
            id=self.next_rule_id,
            name=self.rule_form_name,
            parameters=self.rule_form_parameters,
            importance=self.rule_form_importance,
            category=self.rule_form_category,
            period_seconds=period_seconds,
            display_duration_minutes=display_duration_minutes,
            action_config=action_config,
            comment="Manual Entry",
            is_active=True,
            trigger_script=self.rule_form_trigger_script,
        )
        self.next_rule_id += 1
        self.rules.append(new_rule)
        self.rules = list(self.rules)
        self.log_system_event(
            "Rule Created",
            f"Created rule '{new_rule.name}' ({new_rule.category}) with params: {new_rule.parameters}",
            "success",
            user="Admin User",
        )
        self.rule_form_name = ""
        self.rule_form_action_targets = [""]
        self.rule_form_category = "General"
        self.rule_form_trigger_script = "custom"
        self.rule_form_parameters = "{}"
        return rx.toast.success("Rule created.")

    @rx.event
    def delete_rule(self, rule_id: int):
        rule = self._get_rule_by_id(rule_id)
        if rule:
            self.rules.remove(rule)
            self.rules = list(self.rules)
            self.log_system_event(
                "Rule Deleted",
                f"Deleted rule: {rule.name}",
                "warning",
                user="Admin User",
            )
        return rx.toast.success("Rule deleted.")

    @rx.event
    def toggle_rule_active(self, rule_id: int):
        rule = self._get_rule_by_id(rule_id)
        if rule:
            rule.is_active = not rule.is_active
            status = "activated" if rule.is_active else "deactivated"
            self.log_system_event(
                "Rule Updated",
                f"Rule '{rule.name}' {status}",
                "info",
                user="Admin User",
            )
            self.rules = list(self.rules)

    rules_search_query: str = ""

    @rx.event
    def set_rules_search_query(self, value: str):
        self.rules_search_query = value

    def _serialize_rule_for_grid(self, rule: AlertRule) -> dict:
        flow_info = f"{rule.prefect_flow_name}" if rule.prefect_flow_name else "-"
        last_sync = (
            rule.last_prefect_sync.strftime("%H:%M:%S")
            if rule.last_prefect_sync
            else "-"
        )
        return {
            "id": rule.id,
            "name": rule.name,
            "category": rule.category,
            "importance": rule.importance.upper(),
            "period": f"{rule.period_seconds}s",
            "status": "ACTIVE" if rule.is_active else "INACTIVE",
            "action": "Delete",
            "prefect_info": flow_info,
            "last_prefect_state": rule.last_prefect_state or "-",
            "last_sync": last_sync,
        }

    @rx.var
    def rules_grid_data(self) -> list[dict]:
        data = self.rules
        if self.rules_search_query:
            q = self.rules_search_query.lower()
            data = [r for r in data if q in r.name.lower() or q in r.category.lower()]
        return [self._serialize_rule_for_grid(r) for r in data]

    @rx.event
    def handle_rules_grid_cell_clicked(self, cell_event: dict):
        col = cell_event.get("colDef", {}).get("field")
        data = cell_event.get("data", {})
        rule_id = data.get("id")
        if not rule_id:
            return
        if col == "status":
            self.toggle_rule_active(rule_id)
        elif col == "action":
            self.delete_rule(rule_id)

    history_importance_filter: str = "All"
    history_search_query: str = ""
    history_start_date: str = ""
    history_end_date: str = ""
    history_page: int = 1
    history_page_size: int = 10
    paginated_history: list[dict] = []
    filtered_history_count: int = 0

    @rx.var
    def history_grid_data(self) -> list[dict]:
        """Data source for the History Ag-Grid (Client-side pagination)."""
        filtered = self.events
        if self.history_importance_filter != "All":
            filtered = [
                e
                for e in filtered
                if e.importance == self.history_importance_filter.lower()
            ]
        if self.prefect_state_filter != "All":
            target = self.prefect_state_filter
            if target == "None":
                filtered = [e for e in filtered if not e.prefect_state]
            else:
                filtered = [e for e in filtered if e.prefect_state == target]
        if self.history_search_query:
            q = self.history_search_query.lower()
            filtered = [e for e in filtered if q in e.message.lower()]
        if self.history_start_date:
            try:
                s_date = datetime.strptime(self.history_start_date, "%Y-%m-%d")
                filtered = [
                    e for e in filtered if e.timestamp and e.timestamp >= s_date
                ]
            except ValueError as e:
                logging.exception(f"Error parsing history start date: {e}")
        if self.history_end_date:
            try:
                e_date = datetime.strptime(
                    self.history_end_date, "%Y-%m-%d"
                ) + timedelta(days=1)
                filtered = [e for e in filtered if e.timestamp and e.timestamp < e_date]
            except ValueError as e:
                logging.exception(f"Error parsing history end date: {e}")
        filtered.sort(
            key=lambda x: x.timestamp if x.timestamp else datetime.min, reverse=True
        )
        return [self._serialize_event_for_grid(e, for_history=True) for e in filtered]

    def _refresh_history(self):
        """Perform memory search and pagination (Legacy/Back-compat for non-grid usage if any)."""
        pass

    @rx.event
    def set_history_search_query(self, value: str):
        self.history_search_query = value

    @rx.event
    def set_history_importance_filter(self, value: str):
        self.history_importance_filter = value

    @rx.event
    def set_history_start_date(self, value: str):
        self.history_start_date = value

    @rx.event
    def set_history_end_date(self, value: str):
        self.history_end_date = value

    @rx.event
    def export_history_csv(self):
        rx.toast.success(f"Exporting {len(self.history_grid_data)} events to CSV...")

    @rx.event(background=True)
    async def sync_prefect_status(self):
        """Sync Prefect flow run states."""
        async with self:
            self.log_system_event(
                "Prefect Sync", "Starting Prefect status sync...", "info"
            )
        ids_to_sync = [
            e.prefect_flow_run_id for e in self.events if e.prefect_flow_run_id
        ]
        if not ids_to_sync:
            async with self:
                rx.toast.info("No Prefect flow runs linked to events.")
                return
        try:
            new_states = await PrefectSyncService.get_batch_flow_run_states(ids_to_sync)
            async with self:
                updates = 0
                for event in self.events:
                    if event.prefect_flow_run_id in new_states:
                        old = event.prefect_state
                        new = new_states[event.prefect_flow_run_id]
                        if old != new:
                            event.prefect_state = new
                            updates += 1
                now = datetime.utcnow()
                for rule in self.rules:
                    rule_events = [
                        e
                        for e in self.events
                        if e.rule_id == rule.id and e.prefect_flow_run_id
                    ]
                    if rule_events:
                        latest = max(
                            rule_events, key=lambda e: e.timestamp or datetime.min
                        )
                        if latest.prefect_state:
                            rule.last_prefect_state = latest.prefect_state
                            rule.last_prefect_sync = now
                self.events = list(self.events)
                self.rules = list(self.rules)
                self.log_system_event(
                    "Prefect Sync",
                    f"Synced {len(ids_to_sync)} flows. {updates} updates.",
                    "success",
                )
                rx.toast.success(f"Prefect status synced: {updates} updates.")
        except Exception as e:
            async with self:
                logging.exception(f"Prefect sync failed: {e}")
                rx.toast.error("Failed to sync with Prefect API.")

    is_grid_ready: bool = False

    @rx.event(background=True)
    async def on_load(self):
        """Called when page loads."""
        os.environ["PREFECT_API_URL"] = self.prefect_api_url
        async with self:
            self.fetch_available_triggers()
            await self.test_prefect_connection()
            await self.fetch_prefect_deployments()
            if not self.system_logs:
                self.log_system_event(
                    "System Ready",
                    "Dashboard application loaded successfully",
                    "success",
                    user="System",
                )
            self._initialize_db()
            self._refresh_history()
            await asyncio.sleep(0.5)
            self.is_grid_ready = True