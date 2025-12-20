import reflex as rx
from app.components.sidebar import sidebar
from app.components.live_blotter import live_blotter
from app.components.rule_settings import rules_layout
from app.components.historical_blotter import historical_blotter
from app.components.settings import settings_page
from app.components.logs import logs_page
from app.states.alert_state import AlertState
from app.states.ui_state import UIState


def layout(content: rx.Component) -> rx.Component:
    """Main layout with responsive sidebar and content area."""
    return rx.el.div(
        rx.cond(
            UIState.sidebar_open,
            rx.el.div(
                class_name="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 md:hidden transition-opacity",
                on_click=UIState.close_sidebar,
            ),
        ),
        sidebar(),
        rx.el.div(
            rx.el.header(
                rx.el.div(
                    rx.el.button(
                        rx.icon("menu", class_name="h-6 w-6 text-gray-600"),
                        on_click=UIState.toggle_sidebar,
                        class_name="p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500",
                    ),
                    rx.el.span(
                        "Sentinel", class_name="ml-3 text-lg font-bold text-gray-900"
                    ),
                    class_name="flex items-center",
                ),
                class_name="md:hidden flex items-center justify-between p-4 bg-white border-b border-gray-200 sticky top-0 z-30",
            ),
            rx.el.main(content, class_name="flex-1 bg-gray-50 p-4 md:p-8 min-h-screen"),
            class_name="flex flex-col flex-1 md:ml-64 min-h-screen transition-all duration-300",
        ),
        class_name="flex min-h-screen font-['Inter'] bg-gray-50",
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
                    "System Status", "Healthy", "activity", "text-indigo-600"
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
            ),
            live_blotter(),
        )
    )


def rules_page() -> rx.Component:
    """Rules Management Page."""
    return layout(
        rx.el.div(
            rx.el.h1("Alert Rules", class_name="text-2xl font-bold text-gray-900 mb-6"),
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


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        )
    ],
)
app.add_page(index, route="/", on_load=AlertState.on_load)
app.add_page(rules_page, route="/rules", on_load=AlertState.on_load)
app.add_page(events_page, route="/events", on_load=AlertState.on_load)
app.add_page(
    lambda: layout(settings_page()), route="/settings", on_load=AlertState.on_load
)
app.add_page(lambda: layout(logs_page()), route="/logs", on_load=AlertState.on_load)