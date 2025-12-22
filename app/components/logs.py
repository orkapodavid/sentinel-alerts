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


def search_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "search",
                class_name="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
            ),
            rx.el.input(
                placeholder="Search logs...",
                on_change=AlertState.set_log_search_query,
                class_name="pl-9 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                default_value=AlertState.log_search_query,
            ),
            class_name="relative flex-1 min-w-[200px]",
        ),
        rx.el.select(
            rx.el.option("All Levels", value="All"),
            rx.el.option("Info", value="info"),
            rx.el.option("Success", value="success"),
            rx.el.option("Warning", value="warning"),
            rx.el.option("Error", value="error"),
            value=AlertState.log_level_filter,
            on_change=AlertState.set_log_level_filter,
            class_name="block w-32 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
        ),
        rx.el.input(
            type="date",
            on_change=AlertState.set_log_start_date,
            class_name="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
            default_value=AlertState.log_start_date,
        ),
        rx.el.span("to", class_name="text-sm text-gray-500 font-medium"),
        rx.el.input(
            type="date",
            on_change=AlertState.set_log_end_date,
            class_name="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
            default_value=AlertState.log_end_date,
        ),
        rx.el.button(
            "Clear Filters",
            on_click=AlertState.reset_log_filters,
            class_name="text-sm text-red-600 hover:text-red-800 font-medium px-2",
        ),
        class_name="flex flex-wrap gap-3 items-center p-4 bg-gray-50 border-b border-gray-200",
    )


def pagination_controls() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Showing ",
            rx.el.span(
                AlertState.filtered_logs.length().to_string(), class_name="font-medium"
            ),
            " results",
            class_name="text-sm text-gray-700",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("chevron-left", class_name="w-4 h-4"),
                on_click=AlertState.prev_log_page,
                disabled=AlertState.log_page == 1,
                class_name="p-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            rx.el.span(
                f"Page {AlertState.log_page} of {AlertState.total_log_pages}",
                class_name="px-4 py-2 border-t border-b border-gray-300 bg-white text-sm font-medium text-gray-700",
            ),
            rx.el.button(
                rx.icon("chevron-right", class_name="w-4 h-4"),
                on_click=AlertState.next_log_page,
                disabled=AlertState.log_page == AlertState.total_log_pages,
                class_name="p-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="inline-flex shadow-sm rounded-md",
        ),
        class_name="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6",
    )


def latest_logs_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "refresh-cw", class_name="w-4 h-4 text-indigo-500 animate-spin mr-2"
            ),
            rx.el.span(
                "Live Stream (Most Recent)",
                class_name="text-sm font-medium text-gray-900",
            ),
            class_name="flex items-center p-4 bg-indigo-50 border-b border-indigo-100",
        ),
        rx.el.div(
            rx.cond(
                AlertState.system_logs.length() > 0,
                rx.foreach(AlertState.system_logs, log_row),
                rx.el.div(
                    "No logs available.",
                    class_name="p-8 text-center text-gray-500 italic",
                ),
            ),
            class_name="overflow-y-auto max-h-[600px]",
        ),
    )


def search_history_view() -> rx.Component:
    return rx.el.div(
        search_controls(),
        rx.el.div(
            rx.cond(
                AlertState.paginated_logs.length() > 0,
                rx.el.div(
                    rx.foreach(AlertState.paginated_logs, log_row),
                    class_name="divide-y divide-gray-100",
                ),
                rx.el.div(
                    "No matching logs found.",
                    class_name="p-12 text-center text-gray-500 italic flex flex-col items-center",
                ),
            ),
            class_name="overflow-y-auto h-[530px]",
        ),
        pagination_controls(),
        class_name="flex flex-col h-full",
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
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Latest Logs", value="latest"),
                    rx.tabs.trigger("Search History", value="search"),
                ),
                rx.tabs.content(latest_logs_view(), value="latest"),
                rx.tabs.content(search_history_view(), value="search"),
                default_value="latest",
                value=AlertState.log_active_tab,
                on_change=AlertState.set_log_active_tab,
            ),
            class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden min-h-[700px]",
        ),
        class_name="w-full",
    )