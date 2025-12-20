import reflex as rx
from app.states.alert_state import AlertState
from app.models import AlertEvent


def sort_icon(col_name: str) -> rx.Component:
    """Icon to indicate sorting status."""
    return rx.cond(
        AlertState.live_sort_col == col_name,
        rx.cond(
            AlertState.live_sort_reverse,
            rx.icon("arrow-down", class_name="w-4 h-4 ml-1"),
            rx.icon("arrow-up", class_name="w-4 h-4 ml-1"),
        ),
        rx.icon("arrow-up-down", class_name="w-4 h-4 ml-1 text-gray-300"),
    )


def table_header(text: str, col_name: str) -> rx.Component:
    """Clickable table header for sorting."""
    return rx.el.th(
        rx.el.div(
            text,
            sort_icon(col_name),
            class_name="flex items-center cursor-pointer select-none hover:text-gray-700",
        ),
        on_click=AlertState.sort_live(col_name),
        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
    )


def live_row(event: AlertEvent) -> rx.Component:
    """Render a single row in the live blotter."""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                event.timestamp.to_string(),
                class_name="font-mono text-sm text-gray-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.match(
                event.importance.lower(),
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
                rx.el.span(event.importance, class_name="text-xs text-gray-500"),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(event.message, class_name="text-sm text-gray-900"),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.cond(
                event.is_acknowledged,
                rx.el.span(
                    "Acknowledged",
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
                ),
                rx.el.button(
                    rx.el.span("Acknowledge"),
                    on_click=AlertState.open_acknowledge_modal(event.id),
                    class_name="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-sm",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        class_name="bg-white border-b border-gray-100 hover:bg-gray-50",
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
                            table_header("Time", "tickets"),
                            table_header("Importance", "image"),
                            table_header("Message", "mail_warning"),
                            rx.el.th(
                                "Action",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        ),
                        class_name="bg-gray-50",
                    ),
                    rx.el.tbody(
                        rx.cond(
                            AlertState.live_events_paginated.length() > 0,
                            rx.foreach(AlertState.live_events_paginated, live_row),
                            rx.el.tr(
                                rx.el.td(
                                    "No active alerts to display.",
                                    col_span=4,
                                    class_name="px-6 py-12 text-center text-sm text-gray-500 italic",
                                )
                            ),
                        ),
                        class_name="bg-white divide-y divide-gray-100",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="overflow-x-auto min-h-[400px]",
            ),
            rx.cond(
                AlertState.displayed_events.length() > 0,
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            f"Showing {AlertState.live_start_index} to {AlertState.live_end_index} of {AlertState.displayed_events.length()} alerts",
                            class_name="text-sm text-gray-700",
                        ),
                        class_name="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between",
                    ),
                    rx.el.div(
                        rx.el.nav(
                            rx.el.button(
                                "Previous",
                                on_click=AlertState.prev_live_page,
                                disabled=AlertState.live_page == 1,
                                class_name=rx.cond(
                                    AlertState.live_page == 1,
                                    "relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-300 bg-gray-50 cursor-not-allowed",
                                    "relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50",
                                ),
                            ),
                            rx.el.button(
                                "Next",
                                on_click=AlertState.next_live_page,
                                disabled=AlertState.live_page
                                == AlertState.live_total_pages,
                                class_name=rx.cond(
                                    AlertState.live_page == AlertState.live_total_pages,
                                    "ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-300 bg-gray-50 cursor-not-allowed",
                                    "ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50",
                                ),
                            ),
                            class_name="relative z-0 inline-flex rounded-md shadow-sm",
                        ),
                        class_name="flex items-center justify-between sm:justify-end gap-4 w-full sm:w-auto mt-4 sm:mt-0",
                    ),
                    class_name="flex flex-col sm:flex-row items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6",
                ),
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )