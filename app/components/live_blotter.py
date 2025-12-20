import reflex as rx
import reflex_ag_grid as ag
from app.states.alert_state import AlertState


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
    """The main Live Blotter component using AG Grid."""
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
                ag.ag_grid(
                    id="live_grid",
                    column_defs=[
                        {
                            "field": "timestamp",
                            "headerName": "Time",
                            "sortable": True,
                            "filter": True,
                            "width": 180,
                        },
                        {
                            "field": "importance",
                            "headerName": "Level",
                            "sortable": True,
                            "filter": True,
                            "width": 120,
                            "cellStyle": {"fontWeight": "bold"},
                        },
                        {
                            "field": "message",
                            "headerName": "Message",
                            "filter": True,
                            "flex": 1,
                        },
                        {"field": "status", "headerName": "Status", "width": 140},
                        {
                            "field": "action",
                            "headerName": "Action",
                            "width": 160,
                            "cellStyle": {
                                "cursor": "pointer",
                                "fontWeight": "bold",
                                "color": "#4F46E5",
                            },
                        },
                    ],
                    row_data=AlertState.live_grid_data,
                    pagination=True,
                    pagination_page_size=10,
                    on_cell_clicked=AlertState.handle_live_grid_click,
                    theme="quartz",
                    width="100%",
                    height="100%",
                ),
                class_name="h-[600px] w-full p-4",
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )