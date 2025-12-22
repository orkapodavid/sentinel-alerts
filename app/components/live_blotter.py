import reflex as rx
import reflex_enterprise as rxe
from app.states.alert_state import AlertState
from app.components.grid_config import get_live_columns


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


def filter_button(label: str, filter_value: str) -> rx.Component:
    """Button for quick filtering the blotter."""
    is_active = AlertState.quick_filter == filter_value
    return rx.el.button(
        label,
        on_click=lambda: AlertState.set_quick_filter(filter_value),
        class_name=rx.cond(
            is_active,
            "px-3 py-1.5 text-sm font-medium rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 transition-colors",
            "px-3 py-1.5 text-sm font-medium rounded-lg text-gray-600 hover:bg-gray-50 border border-transparent transition-colors",
        ),
    )


def live_blotter() -> rx.Component:
    """The main Live Blotter component using rxe.ag_grid."""
    return rx.el.div(
        rx.el.div(
            rx.moment(interval=30000, on_change=AlertState.tick), class_name="hidden"
        ),
        acknowledge_modal(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Live Event Blotter",
                        class_name="text-lg font-bold text-gray-900",
                    ),
                    rx.el.div(
                        rx.el.span(
                            class_name="w-2 h-2 rounded-full bg-green-500 animate-pulse mr-2"
                        ),
                        rx.el.span(
                            "Live Polling",
                            class_name="text-xs font-medium text-gray-500",
                        ),
                        class_name="flex items-center bg-gray-50 px-3 py-1 rounded-full border border-gray-200 ml-4",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("Prefect State: All", value="All"),
                        rx.el.option("None (Manual)", value="None"),
                        rx.el.option("Running", value="RUNNING"),
                        rx.el.option("Failed", value="FAILED"),
                        rx.el.option("Completed", value="COMPLETED"),
                        value=AlertState.prefect_state_filter,
                        on_change=AlertState.set_prefect_state_filter,
                        class_name="block rounded-lg border-gray-200 text-sm font-medium text-gray-700 focus:border-indigo-500 focus:ring-indigo-500 p-1.5 border",
                    ),
                    rx.el.div(class_name="w-px h-6 bg-gray-300 mx-2"),
                    filter_button("All Events", "All"),
                    filter_button("Critical Only", "Critical"),
                    filter_button("Market", "Market"),
                    filter_button("System", "System"),
                    rx.el.button(
                        rx.icon("refresh-cw", class_name="w-3 h-3 mr-1"),
                        "Refresh States",
                        on_click=AlertState.sync_prefect_status,
                        class_name="ml-2 inline-flex items-center px-2 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none",
                    ),
                    class_name="flex items-center gap-2 flex-wrap",
                ),
                class_name="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b border-gray-100 gap-4",
            ),
            rx.el.div(
                rx.cond(
                    AlertState.is_grid_ready,
                    rxe.ag_grid(
                        id="live_blotter_grid",
                        column_defs=get_live_columns(),
                        row_data=AlertState.all_live_events,
                        pagination=True,
                        pagination_page_size=20,
                        pagination_page_size_selector=[20, 50, 100],
                        on_cell_clicked=AlertState.handle_live_grid_cell_clicked,
                        width="100%",
                        height="600px",
                        theme="quartz",
                    ),
                    rx.el.div(
                        rx.spinner(),
                        class_name="h-[600px] w-full flex items-center justify-center bg-gray-50",
                    ),
                )
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )