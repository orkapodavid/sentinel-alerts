import reflex as rx
import reflex_enterprise as rxe
from app.components.sidebar import sidebar
from app.components.live_blotter import live_blotter
from app.components.rule_settings import rules_layout
from app.components.historical_blotter import historical_blotter
from app.components.settings import settings_page
from app.components.logs import logs_page
from app.states.alert_state import AlertState
from app.states.ui_state import UIState


def layout(content: rx.Component) -> rx.Component:
    """Main layout with fixed top navigation."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            content,
            class_name="pt-20 min-h-screen bg-gray-50 px-2 md:px-4 py-4 md:py-6 w-full max-w-[1920px] mx-auto",
        ),
        class_name="min-h-screen font-['Inter'] bg-gray-50",
    )


def dashboard_stat_card(
    title: str, value: str, icon: str, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
                rx.el.h3(value, class_name="text-2xl font-bold text-gray-900 mt-1"),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(icon, class_name=f"w-6 h-6 {color_class}"),
                class_name="p-3 bg-white rounded-xl border border-gray-100 shadow-sm",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
    )


def index() -> rx.Component:
    """Dashboard / Overview Page."""
    return layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Dashboard Overview", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("refresh-ccw", class_name="w-4 h-4 mr-2"),
                        "Sync Prefect",
                        on_click=AlertState.sync_prefect_status,
                        class_name="flex items-center px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-sm shadow-sm",
                    ),
                    rx.el.button(
                        rx.icon("refresh-cw", class_name="w-4 h-4 mr-2"),
                        "Generate Mock Alerts",
                        on_click=AlertState.generate_mock_alerts,
                        class_name="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium text-sm shadow-sm hover:shadow",
                    ),
                    class_name="flex gap-3",
                ),
                class_name="flex justify-between items-center mb-8",
            ),
            rx.el.div(
                dashboard_stat_card(
                    "Total Active Rules",
                    AlertState.active_rules_count.to_string(),
                    "shield-check",
                    "text-green-600",
                ),
                dashboard_stat_card(
                    "Total Events",
                    AlertState.total_events.to_string(),
                    "bell",
                    "text-blue-600",
                ),
                dashboard_stat_card(
                    "Unacknowledged",
                    AlertState.unacknowledged_events.to_string(),
                    "trending_down",
                    "text-red-600",
                ),
                dashboard_stat_card(
                    "Prefect Flows",
                    f"{AlertState.prefect_stats['running']} Running",
                    "workflow",
                    "text-indigo-600",
                ),
                dashboard_stat_card(
                    "Server Status",
                    rx.cond(
                        AlertState.prefect_api_url == "",
                        "Disabled",
                        rx.cond(
                            AlertState.prefect_connection_status, "Online", "Offline"
                        ),
                    ),
                    "server",
                    rx.cond(
                        AlertState.prefect_api_url == "",
                        "text-gray-400",
                        rx.cond(
                            AlertState.prefect_connection_status,
                            "text-green-600",
                            "text-red-600",
                        ),
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Prefect Status", class_name="text-sm font-medium text-gray-500"
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                AlertState.prefect_stats["completed"],
                                class_name="text-lg font-bold text-gray-900",
                            ),
                            rx.el.span(
                                "Completed", class_name="text-xs text-green-600 ml-1"
                            ),
                            class_name="flex items-baseline",
                        ),
                        rx.el.div(class_name="w-px h-8 bg-gray-200 mx-4"),
                        rx.el.div(
                            rx.el.span(
                                AlertState.prefect_stats["failed"],
                                class_name="text-lg font-bold text-gray-900",
                            ),
                            rx.el.span(
                                "Failed", class_name="text-xs text-red-600 ml-1"
                            ),
                            class_name="flex items-baseline",
                        ),
                        rx.el.div(class_name="w-px h-8 bg-gray-200 mx-4"),
                        rx.el.div(
                            rx.el.span(
                                AlertState.prefect_stats["running"],
                                class_name="text-lg font-bold text-gray-900",
                            ),
                            rx.el.span(
                                "Running", class_name="text-xs text-blue-600 ml-1"
                            ),
                            class_name="flex items-baseline",
                        ),
                        class_name="flex items-center mt-2",
                    ),
                    class_name="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm",
                ),
                class_name="grid grid-cols-1 mb-8",
            ),
            live_blotter(),
        )
    )


def rules_page() -> rx.Component:
    """Rules View Page (Read-Only)."""
    return layout(
        rx.el.div(
            rx.el.h1("Alert Rules", class_name="text-2xl font-bold text-gray-900 mb-6"),
            rx.el.p(
                "View existing alert rules and their Prefect integration status. Rules are managed externally in Prefect.",
                class_name="text-gray-500 mb-6",
            ),
            rules_layout(),
        )
    )


def events_page() -> rx.Component:
    """Historical Events Page."""
    return layout(
        rx.el.div(
            rx.el.h1(
                "Alert Events", class_name="text-2xl font-bold text-gray-900 mb-6"
            ),
            historical_blotter(),
        )
    )


style_content = """
.row-critical {
    background-color: #FEF2F2 !important;
}

.row-critical .ag-cell:first-child {
    border-left: 4px solid #DC2626 !important;
}

.row-warning {
    background-color: #FFFBEB !important;
}

.critical-cell {
    background-color: #FEF2F2 !important;
}

.warning-cell {
    background-color: #FFFBEB !important;
}

.healthy-cell {
    background-color: #F0FDF4 !important;
    color: #166534 !important;
}

.prefect-link {
    cursor: pointer;
    color: #4F46E5;
    text-decoration: underline;
}

.critical-cell-border {
    border-left: 4px solid #DC2626 !important;
}

@keyframes pulse-red {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.critical-pulse {
    animation: pulse-red 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    color: #DC2626;
    font-weight: bold;
}
"""
app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.style(style_content),
    ],
)
app.add_page(index, route="/", on_load=AlertState.on_load)
app.add_page(rules_page, route="/rules", on_load=AlertState.on_load)
app.add_page(events_page, route="/events", on_load=AlertState.on_load)
app.add_page(
    lambda: layout(settings_page()), route="/settings", on_load=AlertState.on_load
)
app.add_page(lambda: layout(logs_page()), route="/logs", on_load=AlertState.on_load)