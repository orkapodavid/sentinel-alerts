import reflex as rx
from app.states.ui_state import UIState
from app.states.alert_state import AlertState


def feature_group_card(
    title: str, items: list[str], icon: str, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 {color_class} mb-3"),
            rx.el.h4(title, class_name="text-base font-bold text-gray-900 mb-3"),
            rx.el.ul(
                *[
                    rx.el.li(
                        item,
                        class_name="text-sm text-gray-600 mb-2 flex items-start gap-2 before:content-['•'] before:text-gray-400 before:mr-1",
                    )
                    for item in items
                ],
                class_name="list-none p-0",
            ),
            class_name="p-5",
        ),
        class_name="bg-gray-50 rounded-xl border border-gray-100 hover:shadow-md transition-shadow h-full",
    )


def roadmap_item(
    quarter: str, title: str, items: list[str], status: str, priority: str
) -> rx.Component:
    status_colors = {
        "Completed": "bg-green-100 text-green-700 border-green-200",
        "In Progress": "bg-blue-100 text-blue-700 border-blue-200",
        "Planned": "bg-gray-100 text-gray-700 border-gray-200",
    }
    priority_colors = {
        "Critical": "text-red-600 bg-red-50 border-red-100",
        "High": "text-orange-600 bg-orange-50 border-orange-100",
        "Medium": "text-blue-600 bg-blue-50 border-blue-100",
    }
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="w-3 h-3 bg-indigo-600 rounded-full ring-4 ring-white"
            ),
            class_name="absolute left-[-6px] top-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    quarter,
                    class_name="text-xs font-bold text-indigo-600 tracking-wider uppercase mb-1 block",
                ),
                rx.el.div(
                    rx.el.h4(title, class_name="text-lg font-bold text-gray-900"),
                    rx.el.div(
                        rx.el.span(
                            status,
                            class_name=f"px-2 py-0.5 rounded text-xs font-medium border {status_colors.get(status, 'bg-gray-100')}",
                        ),
                        rx.el.span(
                            priority,
                            class_name=f"px-2 py-0.5 rounded text-xs font-medium border {priority_colors.get(priority, 'bg-gray-100')}",
                        ),
                        class_name="flex gap-2",
                    ),
                    class_name="flex justify-between items-start mb-2",
                ),
                rx.el.ul(
                    *[
                        rx.el.li(item, class_name="text-sm text-gray-600 mb-1")
                        for item in items
                    ],
                    class_name="list-disc list-inside",
                ),
            ),
            class_name="bg-white p-5 rounded-xl border border-gray-200 shadow-sm ml-6 mb-8 hover:border-indigo-200 transition-colors",
        ),
        class_name="relative border-l-2 border-indigo-100 last:border-0",
    )


def settings_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1("System Settings", class_name="text-2xl font-bold text-gray-900 mb-6"),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Appearance", class_name="text-lg font-bold text-gray-900 mb-4"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Dark Mode",
                                class_name="text-sm font-medium text-gray-900",
                            ),
                            rx.el.p(
                                "Enable dark mode for the application interface.",
                                class_name="text-xs text-gray-500",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.switch(
                            checked=UIState.dark_mode,
                            on_change=UIState.toggle_dark_mode,
                        ),
                        class_name="flex items-center justify-between",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.h3(
                    "Portfolio Manager Feature Requests",
                    class_name="text-lg font-bold text-gray-900 mb-4",
                ),
                rx.el.div(
                    feature_group_card(
                        "Immediate Value (Quick Wins)",
                        [
                            "Keyboard shortcuts (Ctrl+A)",
                            "Sound notifications",
                            "Bulk acknowledge/dismiss",
                            "Custom column visibility",
                        ],
                        "zap",
                        "text-amber-500",
                    ),
                    feature_group_card(
                        "Risk Management",
                        [
                            "Position-based correlation",
                            "P&L impact estimation",
                            "Risk threshold escalation",
                            "Sector/industry alert grouping",
                        ],
                        "shield-alert",
                        "text-red-500",
                    ),
                    feature_group_card(
                        "Workflow Optimization",
                        [
                            "Alert routing to desks/traders",
                            "Custom alert templates",
                            "Scheduled alert windows",
                            "Mobile push notifications",
                        ],
                        "layers",
                        "text-blue-500",
                    ),
                    feature_group_card(
                        "Analytics & Reporting",
                        [
                            "Frequency analysis by ticker",
                            "SLA tracking metrics",
                            "Historical trend visualization",
                            "Custom report builder",
                        ],
                        "bar-chart-3",
                        "text-purple-500",
                    ),
                    feature_group_card(
                        "Integration Priorities",
                        [
                            "Bloomberg Terminal",
                            "OMS connectivity",
                            "Slack/Teams channels",
                            "Email digest summaries",
                        ],
                        "cable",
                        "text-green-500",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12",
                ),
            ),
            rx.el.div(
                rx.el.h3(
                    "Strategic Roadmap",
                    class_name="text-lg font-bold text-gray-900 mb-6",
                ),
                rx.el.div(
                    roadmap_item(
                        "Q1 2024",
                        "Trader Efficiency Pack",
                        [
                            "Keyboard shortcuts & Hotkeys",
                            "Audio Alerts System",
                            "Bulk Actions Interface",
                        ],
                        "In Progress",
                        "High",
                    ),
                    roadmap_item(
                        "Q2 2024",
                        "Integrations & Mobile",
                        [
                            "Slack & Teams Webhooks",
                            "Mobile App Beta",
                            "Email Digest Service",
                        ],
                        "Planned",
                        "Medium",
                    ),
                    roadmap_item(
                        "Q3 2024",
                        "Advanced Risk Engine",
                        [
                            "Bloomberg Data Integration",
                            "Real-time P&L Correlation",
                            "Sector Exposure Alerts",
                        ],
                        "Planned",
                        "Critical",
                    ),
                    class_name="pl-4",
                ),
                class_name="max-w-3xl",
            ),
            class_name="max-w-6xl",
        ),
        class_name="w-full pb-20",
    )