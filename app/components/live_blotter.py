import reflex as rx
import reflex_enterprise as rxe
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


ticker_renderer = """
function(params) {
    if (!params.value) return '';
    var logo = params.data.logo_url;
    return `<div style="display:flex; align-items:center; gap:8px; height: 100%;">
        <img src="${logo}" style="width:24px; height:24px; border-radius:50%; object-fit:contain; background:#f9fafb;" onError="this.style.display='none'"/>
        <span style="font-weight:600; color: #1f2937;">${params.value}</span>
    </div>`;
}
"""
importance_renderer = """
function(params) {
    var val = params.value.toLowerCase();
    var color = '#4b5563';
    var bg = '#f3f4f6';
    var border = '#e5e7eb';

    if (val === 'critical') { color = '#991b1b'; bg = '#fef2f2'; border = '#fecaca'; }
    else if (val === 'high') { color = '#c2410c'; bg = '#fff7ed'; border = '#fed7aa'; }
    else if (val === 'medium') { color = '#854d0e'; bg = '#fefce8'; border = '#fef08a'; }
    else if (val === 'low') { color = '#1e40af'; bg = '#eff6ff'; border = '#bfdbfe'; }

    return `<div style="display:flex; align-items:center; height: 100%;"><span style="color:${color}; background:${bg}; border: 1px solid ${border}; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">${params.value}</span></div>`;
}
"""
category_renderer = """
function(params) {
    var val = params.value;
    var colors = {
        'Market': {c: '#7c3aed', b: '#f3e8ff', br: '#d8b4fe'},
        'System': {c: '#059669', b: '#ecfdf5', br: '#6ee7b7'},
        'Security': {c: '#be123c', b: '#fff1f2', br: '#fda4af'},
        'General': {c: '#4b5563', b: '#f9fafb', br: '#d1d5db'}
    };
    var style = colors[val] || colors['General'];
    return `<div style="display:flex; align-items:center; height: 100%;"><span style="color:${style.c}; background:${style.b}; border: 1px solid ${style.br}; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;">${val}</span></div>`;
}
"""
column_defs = [
    {
        "field": "timestamp",
        "headerName": "Time",
        "sortable": True,
        "filter": True,
        "width": 160,
        "cellStyle": {"display": "flex", "alignItems": "center"},
    },
    {
        "field": "ticker",
        "headerName": "Ticker / Source",
        "sortable": True,
        "filter": True,
        "cellRenderer": ticker_renderer,
        "width": 180,
    },
    {
        "field": "category",
        "headerName": "Category",
        "sortable": True,
        "filter": True,
        "cellRenderer": category_renderer,
        "width": 120,
    },
    {
        "field": "importance",
        "headerName": "Level",
        "sortable": True,
        "filter": True,
        "cellRenderer": importance_renderer,
        "width": 120,
    },
    {
        "field": "message",
        "headerName": "Message",
        "sortable": True,
        "filter": True,
        "flex": 1,
        "minWidth": 300,
        "cellStyle": {"display": "flex", "alignItems": "center"},
    },
    {
        "field": "status",
        "headerName": "Status",
        "sortable": True,
        "filter": True,
        "cellClassRules": {
            "text-green-600 font-medium": "x == 'Acknowledged'",
            "text-red-600 font-medium": "x == 'Pending'",
        },
        "width": 120,
        "cellStyle": {"display": "flex", "alignItems": "center"},
    },
    {
        "field": "action_label",
        "headerName": "Action",
        "cellClass": "cursor-pointer font-bold text-indigo-600 hover:text-indigo-800",
        "width": 120,
        "cellStyle": {
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        },
    },
]


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
                    filter_button("All Events", "All"),
                    filter_button("Critical Only", "Critical"),
                    filter_button("Market", "Market"),
                    filter_button("System", "System"),
                    class_name="flex gap-2",
                ),
                class_name="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b border-gray-100 gap-4",
            ),
            rx.el.div(
                rx.cond(
                    AlertState.is_grid_ready,
                    rxe.ag_grid(
                        id="live_blotter_grid",
                        column_defs=column_defs,
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