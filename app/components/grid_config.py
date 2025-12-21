import reflex as rx

ticker_renderer = """
function(params) {
    if (!params || !params.value) return '';
    var logo = params.data ? params.data.logo_url : '';
    return `<div style="display:flex; align-items:center; gap:8px; height: 100%;">
        <img src="${logo}" style="width:24px; height:24px; border-radius:50%; object-fit:contain; background:#f9fafb;" onError="this.style.display='none'"/>
        <span style="font-weight:600; color: #1f2937;">${params.value}</span>
    </div>`;
}
"""
importance_renderer = """
function(params) {
    if (!params || !params.value) return '';
    var val = String(params.value).toLowerCase();
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
    if (!params || !params.value) return '';
    var val = params.value;
    var colors = {
        'Market': {c: '#7c3aed', b: '#f3e8ff', br: '#d8b4fe'},
        'System': {c: '#059669', b: '#ecfdf5', br: '#6ee7b7'},
        'Security': {c: '#be123c', b: '#fff1f2', br: '#fda4af'},
        'Liquidity': {c: '#0891b2', b: '#ecfeff', br: '#a5f3fc'},
        'News': {c: '#ea580c', b: '#fff7ed', br: '#fed7aa'},
        'General': {c: '#4b5563', b: '#f9fafb', br: '#d1d5db'}
    };
    var style = colors[val] || colors['General'];
    return `<div style="display:flex; align-items:center; height: 100%;"><span style="color:${style.c}; background:${style.b}; border: 1px solid ${style.br}; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;">${val}</span></div>`;
}
"""
status_renderer = """
function(params) {
    if (!params || !params.value) return '';
    var val = params.value;
    var color = val === 'Acknowledged' ? '#16a34a' : '#dc2626';
    return `<div style="display:flex; align-items:center; height: 100%; color: ${color}; font-weight: 500;">${val}</div>`;
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
        "cellRenderer": ticker_renderer,
        "width": 200,
    },
    {
        "field": "category",
        "headerName": "Category",
        "sortable": True,
        "filter": True,
        "cellRenderer": category_renderer,
        "width": 130,
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
        "cellRenderer": status_renderer,
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