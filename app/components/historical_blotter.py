import reflex as rx
import reflex_enterprise as rxe
from app.states.alert_state import AlertState
from app.components.grid_config import get_history_columns


def historical_blotter() -> rx.Component:
    """Full historical event blotter with filters and Ag-Grid."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3("Event History", class_name="text-lg font-bold text-gray-900"),
                rx.el.p(
                    "Full audit trail of all generated alerts",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.input(
                        type="date",
                        class_name="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        on_change=AlertState.set_history_start_date,
                    ),
                    rx.el.span("to", class_name="text-sm text-gray-500 font-medium"),
                    rx.el.input(
                        type="date",
                        class_name="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        on_change=AlertState.set_history_end_date,
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.select(
                    rx.el.option("All Importances", value="All"),
                    rx.el.option("Critical", value="critical"),
                    rx.el.option("High", value="high"),
                    rx.el.option("Medium", value="medium"),
                    rx.el.option("Low", value="low"),
                    value=AlertState.history_importance_filter,
                    on_change=AlertState.set_history_importance_filter,
                    class_name="block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                ),
                rx.el.select(
                    rx.el.option("Prefect: All", value="All"),
                    rx.el.option("None", value="None"),
                    rx.el.option("Running", value="RUNNING"),
                    rx.el.option("Failed", value="FAILED"),
                    rx.el.option("Completed", value="COMPLETED"),
                    value=AlertState.prefect_state_filter,
                    on_change=AlertState.set_prefect_state_filter,
                    class_name="block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="w-4 h-4 text-gray-500"),
                    title="Refresh Prefect States",
                    on_click=AlertState.sync_prefect_status,
                    class_name="p-2 border border-gray-300 rounded-md hover:bg-gray-50",
                ),
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                    ),
                    rx.el.input(
                        placeholder="Search ticker or message...",
                        on_change=AlertState.set_history_search_query,
                        class_name="pl-9 block w-64 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                        default_value=AlertState.history_search_query,
                    ),
                    class_name="relative",
                ),
                rx.el.button(
                    rx.icon("download", class_name="w-4 h-4 mr-2"),
                    "Export",
                    on_click=AlertState.export_history_csv,
                    class_name="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                ),
                class_name="flex flex-wrap gap-3 items-center",
            ),
            class_name="flex flex-col xl:flex-row justify-between items-start xl:items-center p-6 border-b border-gray-100 gap-4",
        ),
        rx.el.div(
            rx.cond(
                AlertState.is_grid_ready,
                rxe.ag_grid(
                    id="history_blotter_grid",
                    column_defs=get_history_columns(),
                    row_data=AlertState.history_grid_data,
                    pagination=True,
                    pagination_page_size=20,
                    pagination_page_size_selector=[20, 50, 100],
                    on_cell_clicked=AlertState.handle_history_grid_cell_clicked,
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
    )