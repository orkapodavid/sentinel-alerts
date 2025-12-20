import reflex as rx
from app.states.alert_state import AlertState


def history_row(event: dict) -> rx.Component:
    """Row for historical blotter table."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(event["timestamp"], class_name="font-mono text-sm text-gray-900"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                event["ticker"],
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(event["message"], class_name="text-sm text-gray-900"),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.match(
                event["importance"].to(str).lower(),
                (
                    "critical",
                    rx.el.span("CRITICAL", class_name="text-xs font-bold text-red-600"),
                ),
                (
                    "high",
                    rx.el.span("HIGH", class_name="text-xs font-bold text-orange-600"),
                ),
                (
                    "medium",
                    rx.el.span(
                        "MEDIUM", class_name="text-xs font-medium text-yellow-600"
                    ),
                ),
                (
                    "low",
                    rx.el.span("LOW", class_name="text-xs font-medium text-blue-600"),
                ),
                rx.el.span(event["importance"], class_name="text-xs text-gray-500"),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.cond(
                event["is_acknowledged"],
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "circle_check_big",
                            class_name="w-4 h-4 text-green-500 mr-1.5",
                        ),
                        rx.el.span(
                            "Acknowledged",
                            class_name="text-xs font-medium text-green-700",
                        ),
                        class_name="flex items-center mb-1",
                    ),
                    rx.cond(
                        event["ack_comment"],
                        rx.el.p(
                            event["ack_comment"],
                            class_name="text-xs text-gray-500 italic",
                        ),
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.span(
                    "Pending",
                    class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800",
                ),
            ),
            class_name="px-6 py-4",
        ),
        class_name="bg-white border-b border-gray-100 hover:bg-gray-50",
    )


def historical_blotter() -> rx.Component:
    """Full historical event blotter with filters."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3("Event History", class_name="text-lg font-bold text-gray-900"),
                rx.el.p(
                    "Full audit trail of all generated alerts",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("All Importances", value="All"),
                    rx.el.option("Critical", value="critical"),
                    rx.el.option("High", value="high"),
                    rx.el.option("Medium", value="medium"),
                    rx.el.option("Low", value="low"),
                    value=AlertState.history_importance_filter,
                    on_change=AlertState.set_history_importance_filter,
                    class_name="block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                ),
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Search ticker or message...",
                        on_change=AlertState.set_history_search_query,
                        class_name="pl-9 block w-64 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        default_value=AlertState.history_search_query,
                    ),
                    class_name="relative",
                ),
                class_name="flex gap-3",
            ),
            class_name="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b border-gray-100 gap-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Time (UTC)",
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Ticker",
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Message",
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Level",
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Status",
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                    ),
                    class_name="bg-gray-50",
                ),
                rx.el.tbody(
                    rx.cond(
                        AlertState.filtered_history.length() > 0,
                        rx.foreach(AlertState.filtered_history, history_row),
                        rx.el.tr(
                            rx.el.td(
                                "No events found matching your filters.",
                                col_span=5,
                                class_name="px-6 py-12 text-center text-sm text-gray-500 italic",
                            )
                        ),
                    ),
                    class_name="bg-white divide-y divide-gray-100",
                ),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
    )