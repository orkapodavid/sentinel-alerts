import reflex as rx
from app.states.alert_state import AlertState
from app.models import AlertEvent


def importance_badge(importance: str) -> rx.Component:
    """Render a colored badge for event importance."""
    return rx.match(
        importance.lower(),
        (
            "critical",
            rx.el.span(
                "CRITICAL",
                class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800",
            ),
        ),
        (
            "high",
            rx.el.span(
                "HIGH",
                class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800",
            ),
        ),
        (
            "medium",
            rx.el.span(
                "MEDIUM",
                class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800",
            ),
        ),
        (
            "low",
            rx.el.span(
                "LOW",
                class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800",
            ),
        ),
        rx.el.span(
            importance,
            class_name="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800",
        ),
    )


def blotter_row(event: AlertEvent) -> rx.Component:
    """Render a single row in the blotter table."""
    return rx.el.tr(
        rx.el.td(
            rx.moment(
                event.timestamp,
                format="HH:mm:ss",
                class_name="font-mono text-sm text-gray-900",
            ),
            rx.el.div(
                rx.moment(event.timestamp, from_now=True),
                class_name="text-xs text-gray-500",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            importance_badge(event.importance), class_name="px-6 py-4 whitespace-nowrap"
        ),
        rx.el.td(
            rx.el.div(event.message, class_name="text-sm text-gray-900 font-medium"),
            rx.cond(
                event.comment,
                rx.el.div(
                    rx.icon("message-square", class_name="w-3 h-3 mr-1 inline"),
                    event.comment,
                    class_name="text-xs text-gray-500 mt-1 flex items-center",
                ),
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.cond(
                event.is_acknowledged,
                rx.el.span(
                    rx.icon("circle_check_big", class_name="w-4 h-4 mr-1"),
                    "Ack",
                    class_name="inline-flex items-center text-xs font-medium text-green-600",
                ),
                rx.el.button(
                    "Acknowledge",
                    on_click=AlertState.open_acknowledge_modal(event.id),
                    class_name="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="bg-white border-b border-gray-100 hover:bg-gray-50 transition-colors",
    )


def acknowledge_modal() -> rx.Component:
    """Modal for acknowledging an event."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Acknowledge Event"),
            rx.dialog.description(
                "Add an optional comment regarding this alert acknowledgement.",
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.textarea(
                    placeholder="Analysis or action taken...",
                    on_change=AlertState.set_acknowledgement_comment,
                    class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 min-h-[100px] p-2 border",
                    default_value=AlertState.acknowledgement_comment,
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Cancel",
                        on_click=AlertState.cancel_acknowledgement,
                        class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50",
                    )
                ),
                rx.dialog.close(
                    rx.el.button(
                        "Confirm Acknowledgment",
                        on_click=AlertState.submit_acknowledgement,
                        class_name="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700",
                    )
                ),
                class_name="flex justify-end gap-3",
            ),
            class_name="max-w-md bg-white p-6 rounded-xl shadow-xl",
        ),
        open=AlertState.selected_event_id != -1,
    )


def live_blotter() -> rx.Component:
    """The main Live Blotter component."""
    return rx.el.div(
        rx.el.div(
            rx.moment(interval=30000, on_change=AlertState.tick), class_name="hidden"
        ),
        acknowledge_modal(),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Live Event Blotter", class_name="text-lg font-bold text-gray-900"
                ),
                rx.el.div(
                    rx.el.span(
                        class_name="w-2 h-2 rounded-full bg-green-500 animate-pulse mr-2"
                    ),
                    rx.el.span(
                        "Live Polling", class_name="text-xs font-medium text-gray-500"
                    ),
                    class_name="flex items-center bg-gray-50 px-3 py-1 rounded-full border border-gray-200",
                ),
                class_name="flex justify-between items-center p-6 border-b border-gray-100",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Time",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Importance",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Message",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Action",
                                class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        ),
                        class_name="bg-gray-50",
                    ),
                    rx.el.tbody(
                        rx.cond(
                            AlertState.displayed_events.length() > 0,
                            rx.foreach(AlertState.displayed_events, blotter_row),
                            rx.el.tr(
                                rx.el.td(
                                    "No active alerts requiring attention.",
                                    col_span=4,
                                    class_name="px-6 py-8 text-center text-sm text-gray-500 italic",
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
        ),
        class_name="w-full",
    )