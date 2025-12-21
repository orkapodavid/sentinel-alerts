import reflex as rx

base_columns = [
    {
        "field": "timestamp",
        "headerName": "Time (UTC)",
        "sortable": True,
        "filter": True,
        "width": 170,
    },
    {
        "field": "ticker",
        "headerName": "Ticker / Source",
        "sortable": True,
        "filter": True,
        "width": 140,
    },
    {
        "field": "category",
        "headerName": "Category",
        "sortable": True,
        "filter": True,
        "width": 130,
    },
    {
        "field": "importance",
        "headerName": "Level",
        "sortable": True,
        "filter": True,
        "width": 120,
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
        "field": "status",
        "headerName": "Status",
        "sortable": True,
        "filter": True,
        "width": 130,
    },
]


def get_live_columns() -> list[dict]:
    """Columns for the Live Blotter."""
    return base_columns + [
        {"field": "action_label", "headerName": "Action", "width": 140}
    ]


def get_history_columns() -> list[dict]:
    """Columns for the Historical Blotter."""
    return base_columns + [
        {"field": "action_label", "headerName": "Action", "width": 140}
    ]