import reflex as rx
from reflex_ag_grid import ag_grid
from app.states.alert_state import AlertState
from app.models import AlertEvent

column_defs = [
    ag_grid.column_def(
        field="timestamp",
        header_name="Time",
        filter=ag_grid.filters.text,
        width=120,
        suppress_menu=True,
    ),
    ag_grid.column_def(
        field="importance",
        header_name="Importance",
        filter=ag_grid.filters.text,
        width=140,
    ),
    ag_grid.column_def(
        field="message",
        header_name="Message",
        filter=ag_grid.filters.text,
        flex=1,
        min_width=300,
    ),
    ag_grid.column_def(
        field="action_label",
        header_name="Action",
        width=160,
        cell_style={"cursor": "pointer"},
        sortable=False,
        filter=False,
    ),
]


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
                ag_grid(
                    id="live_grid",
                    column_defs=column_defs,
                    row_data=AlertState.ag_grid_events,
                    on_cell_clicked=AlertState.handle_ag_grid_action,
                    default_col_def={
                        "sortable": True,
                        "resizable": True,
                        "filter": True,
                    },
                    style={"height": "100%", "width": "100%"},
                    suppressBrowserResizeObserver=True,
                ),
                class_name="w-full h-[500px]",
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )