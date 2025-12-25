import reflex as rx

base_columns = [
    {
        "field": "timestamp",
        "headerName": "Time (UTC)",
        "sortable": True,
        "filter": True,
        "width": 170,
        "cellClassRules": {
            "critical-cell-border": "data.is_critical",
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
    {
        "field": "ticker",
        "headerName": "Ticker / Source",
        "sortable": True,
        "filter": True,
        "width": 140,
        "cellClassRules": {
            "font-bold": "data.raw_importance === 'CRITICAL'",
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
    {
        "field": "category",
        "headerName": "Category",
        "sortable": True,
        "filter": True,
        "width": 130,
        "cellClassRules": {
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
    {
        "field": "importance",
        "headerName": "Level",
        "sortable": True,
        "filter": True,
        "width": 145,
        "cellClassRules": {
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
            "healthy-cell": "data.category === 'HealthCheck' && data.raw_importance === 'LOW'",
        },
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
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
    {
        "field": "message",
        "headerName": "Message",
        "sortable": True,
        "filter": True,
        "flex": 1,
        "minWidth": 300,
        "cellClassRules": {
            "font-bold": "data.raw_importance === 'CRITICAL'",
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
    {
        "field": "status",
        "headerName": "Status",
        "sortable": True,
        "filter": True,
        "width": 130,
        "cellClassRules": {
            "critical-pulse": "data.raw_importance === 'CRITICAL' && data.status === 'Pending'",
            "text-green-600 font-medium": "data.status === 'Acknowledged'",
            "text-green-600 font-bold": "data.category === 'HealthCheck' && data.raw_importance === 'LOW'",
            "critical-cell": "data.is_critical",
            "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
        },
    },
]


def get_live_columns() -> list[dict]:
    """Columns for the Live Blotter."""
    return base_columns + [
        {
            "field": "prefect_link",
            "headerName": "Prefect UI",
            "width": 120,
            "cellClassRules": {
                "prefect-link": "true",
                "critical-cell": "data.is_critical",
                "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
            },
        },
        {
            "field": "action_label",
            "headerName": "Action",
            "width": 140,
            "cellClassRules": {
                "critical-cell": "data.is_critical",
                "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
            },
        },
    ]


def get_history_columns() -> list[dict]:
    """Columns for the Historical Blotter."""
    return base_columns + [
        {
            "field": "prefect_link",
            "headerName": "Prefect UI",
            "width": 120,
            "cellClassRules": {
                "prefect-link": "true",
                "critical-cell": "data.is_critical",
                "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
            },
        },
        {
            "field": "action_label",
            "headerName": "Action",
            "width": 140,
            "cellClassRules": {
                "critical-cell": "data.is_critical",
                "warning-cell": "data.raw_importance === 'HIGH' && !data.is_acknowledged",
            },
        },
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
            "field": "category",
            "headerName": "Category",
            "width": 130,
            "sortable": True,
            "filter": True,
        },
        {
            "field": "importance",
            "headerName": "Importance",
            "width": 130,
            "sortable": True,
            "filter": True,
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
    ]