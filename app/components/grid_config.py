import reflex as rx

importance_style = """
(params) => {
    if (!params.value) return null;
    const val = params.value.toLowerCase();
    const common = { fontWeight: '600', display: 'flex', alignItems: 'center', height: '100%', paddingLeft: '8px' };
    if (val === 'critical') return { ...common, color: '#991b1b', backgroundColor: '#fef2f2', borderLeft: '4px solid #ef4444' };
    if (val === 'high') return { ...common, color: '#9a3412', backgroundColor: '#fff7ed', borderLeft: '4px solid #f97316' };
    if (val === 'medium') return { ...common, color: '#854d0e', backgroundColor: '#fefce8', borderLeft: '4px solid #eab308' };
    if (val === 'low') return { ...common, color: '#1e40af', backgroundColor: '#eff6ff', borderLeft: '4px solid #3b82f6' };
    return common;
}
"""
category_style = """
(params) => {
    if (!params.value) return null;
    const val = params.value;
    const common = { display: 'flex', alignItems: 'center', height: '100%', paddingLeft: '8px' };
    if (val === 'Market') return { ...common, color: '#7c3aed', backgroundColor: '#f3e8ff' };
    if (val === 'System') return { ...common, color: '#059669', backgroundColor: '#ecfdf5' };
    if (val === 'Security') return { ...common, color: '#be123c', backgroundColor: '#fff1f2' };
    if (val === 'Liquidity') return { ...common, color: '#0891b2', backgroundColor: '#ecfeff' };
    if (val === 'News') return { ...common, color: '#ea580c', backgroundColor: '#fff7ed' };
    return { ...common, color: '#374151', backgroundColor: '#f3f4f6' };
}
"""
status_style = """
(params) => {
    const common = { display: 'flex', alignItems: 'center', height: '100%' };
    if (params.value === 'Acknowledged') return { ...common, color: '#16a34a', fontWeight: '600' };
    return { ...common, color: '#dc2626', fontWeight: '600' };
}
"""
base_columns = [
    {
        "field": "timestamp",
        "headerName": "Time (UTC)",
        "sortable": True,
        "filter": True,
        "width": 170,
        "cellStyle": {"display": "flex", "alignItems": "center"},
    },
    {
        "field": "ticker",
        "headerName": "Ticker / Source",
        "sortable": True,
        "filter": True,
        "width": 140,
        "cellStyle": {"display": "flex", "alignItems": "center", "fontWeight": "600"},
    },
    {
        "field": "category",
        "headerName": "Category",
        "sortable": True,
        "filter": True,
        "cellStyle": category_style,
        "width": 130,
    },
    {
        "field": "importance",
        "headerName": "Level",
        "sortable": True,
        "filter": True,
        "cellStyle": importance_style,
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
        "cellStyle": status_style,
        "width": 130,
    },
]


def get_live_columns() -> list[dict]:
    """Columns for the Live Blotter."""
    return base_columns + [
        {
            "field": "action_label",
            "headerName": "Action",
            "width": 140,
            "cellStyle": {
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "cursor": "pointer",
                "fontWeight": "600",
                "color": "#4f46e5",
            },
        }
    ]


def get_history_columns() -> list[dict]:
    """Columns for the Historical Blotter."""
    return base_columns + [
        {
            "field": "action_label",
            "headerName": "Action",
            "width": 140,
            "cellStyle": {
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "cursor": "pointer",
                "fontWeight": "600",
                "color": "#4b5563",
            },
        }
    ]