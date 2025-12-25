import reflex as rx
import reflex_enterprise as rxe
from app.states.alert_state import AlertState
from app.models import AlertRule
from app.components.grid_config import get_rule_columns


def rule_list() -> rx.Component:
    """List of existing rules using AG Grid."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Existing Rules", class_name="text-lg font-bold text-gray-900"
                ),
                rx.el.p(
                    "Manage your active alert definitions",
                    class_name="text-sm text-gray-500",
                ),
                class_name="flex flex-col",
            ),
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
                ),
                rx.el.input(
                    placeholder="Search rules...",
                    on_change=AlertState.set_rules_search_query,
                    class_name="pl-9 block w-64 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border",
                    default_value=AlertState.rules_search_query,
                ),
                class_name="relative",
            ),
            class_name="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b border-gray-100 gap-4",
        ),
        rx.el.div(
            rx.cond(
                AlertState.is_grid_ready,
                rxe.ag_grid(
                    id="rules_grid",
                    column_defs=get_rule_columns(),
                    row_data=AlertState.rules_grid_data,
                    pagination=True,
                    pagination_page_size=20,
                    pagination_page_size_selector=[20, 50, 100],
                    on_cell_clicked=AlertState.handle_rules_grid_cell_clicked,
                    width="100%",
                    height="500px",
                    theme="quartz",
                ),
                rx.el.div(
                    rx.spinner(),
                    class_name="h-[500px] w-full flex items-center justify-center bg-gray-50",
                ),
            )
        ),
        class_name="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden",
    )


def rules_layout() -> rx.Component:
    """Layout for the Rules Page."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("info", class_name="h-5 w-5 text-blue-600"),
                rx.el.div(
                    rx.el.p(
                        "Rules Management Notice",
                        class_name="text-sm font-semibold text-blue-900",
                    ),
                    rx.el.p(
                        "Alert rules and deployments are managed exclusively within the Prefect dashboard. This interface provides a read-only view of active definitions and their current sync status.",
                        class_name="text-sm text-blue-700 mt-1",
                    ),
                    class_name="ml-3",
                ),
                class_name="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-xl mb-6",
            ),
            rule_list(),
            class_name="w-full",
        ),
        class_name="flex flex-col gap-8 w-full",
    )