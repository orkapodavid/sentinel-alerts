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
        "field": "prefect_state",
        "headerName": "Flow State",
        "sortable": True,
        "filter": True,
        "width": 130,
        "cellClassRules": {
            "text-green-600 font-bold": "x == 'COMPLETED'",
            "text-red-600 font-bold": "x == 'FAILED' || x == 'CRASHED'",
            "text-blue-600 font-bold": "x == 'RUNNING'",
            "text-orange-500 font-bold": "x == 'PENDING' || x == 'SCHEDULED'",
            "text-gray-400": "x == 'CANCELLED' || x == 'PAUSED'",
        },
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
        {
            "field": "prefect_link",
            "headerName": "Prefect UI",
            "width": 120,
            "cellStyle": {
                "cursor": "pointer",
                "color": "#4F46E5",
                "textDecoration": "underline",
            },
        },
        {"field": "action_label", "headerName": "Action", "width": 140},
    ]


def get_history_columns() -> list[dict]:
    """Columns for the Historical Blotter."""
    return base_columns + [
        {
            "field": "prefect_link",
            "headerName": "Prefect UI",
            "width": 120,
            "cellStyle": {
                "cursor": "pointer",
                "color": "#4F46E5",
                "textDecoration": "underline",
            },
        },
        {"field": "action_label", "headerName": "Action", "width": 140},
    ]


def get_rule_columns() -> list[dict]:
    """Columns for the Rule Settings Grid."""
    return [
        {
            "field": "name",
            "headerName": "Rule Name",
            "sortable": True,
            "filter": True,
            "flex": 1,
            "minWidth": 200,
        },
        {
            "field": "prefect_info",
            "headerName": "Deployment",
            "width": 200,
            "cellClass": "font-mono text-xs text-gray-600",
        },
        {
            "field": "last_prefect_state",
            "headerName": "Last State",
            "width": 130,
            "cellClassRules": {
                "text-green-600 font-bold": "x == 'COMPLETED'",
                "text-red-600 font-bold": "x == 'FAILED' || x == 'CRASHED'",
                "text-blue-600 font-bold": "x == 'RUNNING'",
            },
        },
        {
            "field": "last_sync",
            "headerName": "Last Sync",
            "width": 150,
            "cellClass": "text-xs text-gray-500",
        },
        {"field": "period", "headerName": "Freq", "width": 100},
        {
            "field": "status",
            "headerName": "Status",
            "sortable": True,
            "width": 100,
            "cellStyle": {"cursor": "pointer", "fontWeight": "bold"},
        },
        {
            "field": "action",
            "headerName": "Del",
            "width": 70,
            "cellStyle": {
                "cursor": "pointer",
                "textAlign": "center",
                "color": "#EF4444",
            },
        },
    ]