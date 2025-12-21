import reflex as rx
from app.states.alert_state import AlertState
from app.models import LogEntry


def log_row(log: LogEntry) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            log.timestamp, class_name="text-xs font-mono text-gray-500 w-36 shrink-0"
        ),
        rx.el.span(
            log.level.upper(),
            class_name=rx.match(
                log.level.lower(),
                ("error", "text-xs font-bold text-red-600 w-20 shrink-0"),
                ("warning", "text-xs font-bold text-orange-600 w-20 shrink-0"),
                ("success", "text-xs font-bold text-green-600 w-20 shrink-0"),
                "text-xs font-bold text-blue-600 w-20 shrink-0",
            ),
        ),
        rx.el.div(
            rx.el.span(log.type, class_name="text-xs font-medium text-gray-900 block"),
            rx.el.div(
                rx.icon("user", class_name="w-3 h-3 text-gray-400 mr-1"),
                rx.el.span(log.user, class_name="text-[10px] text-gray-500 truncate"),
                class_name="flex items-center mt-0.5",
            ),
            rx.cond(
                log.ticker,
                rx.el.span(
                    log.ticker,
                    class_name="text-[10px] font-mono text-gray-500 bg-gray-100 px-1 rounded inline-block mt-1",
                ),
            ),
            class_name="w-36 shrink-0",
        ),
        rx.el.div(
            rx.el.span(log.message, class_name="text-sm text-gray-700 font-mono block"),
            rx.cond(
                log.importance,
                rx.el.span(
                    log.importance,
                    class_name="text-[10px] font-bold uppercase text-gray-400 mt-1 inline-block",
                ),
            ),
            class_name="flex-1",
        ),
        class_name="flex items-start gap-4 p-3 border-b border-gray-100 hover:bg-gray-50",
    )


def logs_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1("System Logs", class_name="text-2xl font-bold text-gray-900"),
            rx.el.div(
                rx.el.span(
                    class_name="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2"
                ),
                rx.el.span(
                    "System Operational",
                    class_name="text-sm font-medium text-green-700",
                ),
                class_name="flex items-center px-3 py-1 bg-green-50 rounded-full border border-green-200",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Activity Log", class_name="text-lg font-bold text-gray-900"
                    ),
                    rx.el.p(
                        "Recent system events and audit trail",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="flex flex-col",
                ),
                rx.el.div(
                    rx.icon(
                        "refresh-cw", class_name="w-4 h-4 text-gray-400 animate-spin"
                    ),
                    rx.el.span("Live Updates", class_name="text-xs text-gray-500 ml-2"),
                    class_name="flex items-center",
                ),
                class_name="flex justify-between items-center p-6 border-b border-gray-100",
            ),
            rx.el.div(
                rx.cond(
                    AlertState.system_logs.length() > 0,
                    rx.foreach(AlertState.system_logs, log_row),
                    rx.el.div(
                        "No system logs available.",
                        class_name="p-8 text-center text-gray-500 italic",
                    ),
                ),
                class_name="overflow-y-auto max-h-[600px]",
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
        ),
        class_name="w-full",
    )