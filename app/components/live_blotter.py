import reflex as rx
import reflex_ag_grid as ag
from app.states.alert_state import AlertState
from app.models import AlertEvent

badge_renderer = """
function(params) {
    if (!params.value) return '';
    const map = {
        'critical': 'bg-red-100 text-red-800',
        'high': 'bg-orange-100 text-orange-800',
        'medium': 'bg-yellow-100 text-yellow-800',
        'low': 'bg-blue-100 text-blue-800'
    };
    const colorClass = map[params.value.toLowerCase()] || 'bg-gray-100 text-gray-800';
    return `<span class="px-2 py-0.5 rounded text-xs font-medium ${colorClass}">${params.value.toUpperCase()}</span>`;
}
"""
action_renderer = """
function(params) {
    if (params.data.is_acknowledged) {
        return '<span class="text-green-600 font-medium text-xs flex items-center justify-end h-full"><svg class="w-4 h-4 mr-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>Ack</span>';
    } else {
        return '<div class="flex justify-end items-center h-full"><button class="px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded hover:bg-indigo-200 transition-colors">Acknowledge</button></div>';
    }
}
"""
column_defs = [
    {
        "field": "timestamp",
        "headerName": "Time",
        "sortable": True,
        "filter": True,
        "width": 120,
        "suppressMenu": True,
    },
    {
        "field": "importance",
        "headerName": "Importance",
        "sortable": True,
        "filter": True,
        "width": 140,
        "cellRenderer": badge_renderer,
    },
    {
        "field": "message",
        "headerName": "Message",
        "sortable": True,
        "filter": True,
        "flex": 1,
        "minWidth": 300,
    },
    {
        "field": "action_label",
        "headerName": "Action",
        "width": 160,
        "cellRenderer": action_renderer,
        "cellStyle": {"cursor": "pointer"},
        "sortable": False,
        "filter": False,
    },
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
                ag.ag_grid(
                    id="live_grid",
                    column_defs=column_defs,
                    row_data=AlertState.ag_grid_events,
                    on_cell_clicked=AlertState.handle_ag_grid_action,
                    class_name="h-[500px] w-full",
                    theme="alpine",
                ),
                class_name="w-full",
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )