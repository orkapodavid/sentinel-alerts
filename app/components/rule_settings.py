import reflex as rx
from app.states.alert_state import AlertState
from app.models import AlertRule


def clone_rule_modal() -> rx.Component:
    """Modal to clone settings from an existing rule."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Clone Existing Rule"),
            rx.dialog.description(
                "Search and select a rule to copy its settings.", class_name="mb-4"
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Search rules by name...",
                    on_change=AlertState.set_clone_search_query,
                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm mb-4",
                ),
                rx.el.div(
                    rx.cond(
                        AlertState.clone_paginated_rules.length() > 0,
                        rx.foreach(
                            AlertState.clone_paginated_rules,
                            lambda r: rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        r.name, class_name="font-medium text-gray-900"
                                    ),
                                    rx.el.p(
                                        f"{r.category} • {r.importance}",
                                        class_name="text-xs text-gray-500",
                                    ),
                                    class_name="flex flex-col",
                                ),
                                rx.el.button(
                                    "Select",
                                    on_click=AlertState.select_clone_rule(r.id),
                                    class_name="px-3 py-1 text-xs font-medium text-indigo-700 bg-indigo-50 rounded-md hover:bg-indigo-100",
                                ),
                                class_name="flex justify-between items-center p-3 border rounded-lg hover:border-indigo-300 transition-colors",
                            ),
                        ),
                        rx.el.p(
                            "No matching rules found.",
                            class_name="text-sm text-gray-500 italic text-center p-4",
                        ),
                    ),
                    class_name="space-y-2 max-h-[300px] overflow-y-auto mb-4 pr-1",
                ),
                rx.cond(
                    AlertState.clone_total_pages > 1,
                    rx.el.div(
                        rx.el.button(
                            rx.icon("chevron-left", class_name="w-4 h-4"),
                            on_click=AlertState.prev_clone_page,
                            disabled=AlertState.clone_page == 1,
                            class_name="p-1 rounded hover:bg-gray-100 disabled:opacity-50",
                        ),
                        rx.el.span(
                            f"Page {AlertState.clone_page} of {AlertState.clone_total_pages}",
                            class_name="text-xs text-gray-500 font-medium",
                        ),
                        rx.el.button(
                            rx.icon("chevron-right", class_name="w-4 h-4"),
                            on_click=AlertState.next_clone_page,
                            disabled=AlertState.clone_page
                            == AlertState.clone_total_pages,
                            class_name="p-1 rounded hover:bg-gray-100 disabled:opacity-50",
                        ),
                        class_name="flex justify-between items-center bg-gray-50 p-2 rounded-lg",
                    ),
                ),
            ),
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Cancel",
                        on_click=AlertState.close_clone_modal,
                        class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50",
                    )
                ),
                class_name="flex justify-end mt-4",
            ),
            class_name="max-w-md bg-white p-6 rounded-xl shadow-xl",
        ),
        open=AlertState.clone_modal_open,
    )


def action_target_item(target: str, index: int) -> rx.Component:
    return rx.el.div(
        rx.el.input(
            on_change=lambda v: AlertState.update_action_target(index, v),
            class_name="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            placeholder="email@example.com",
            default_value=target,
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="w-4 h-4 text-gray-500 hover:text-red-500"),
            on_click=AlertState.remove_action_target(index),
            class_name="p-2 hover:bg-gray-100 rounded-lg transition-colors",
            type="button",
        ),
        class_name="flex gap-2",
    )


def rule_form() -> rx.Component:
    """Form to create a new alert rule."""
    return rx.el.div(
        clone_rule_modal(),
        rx.el.div(
            rx.el.h3("Create New Rule", class_name="text-lg font-bold text-gray-900"),
            rx.el.button(
                rx.icon("copy", class_name="w-4 h-4 mr-2"),
                "Clone Existing",
                on_click=AlertState.open_clone_modal,
                class_name="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50",
            ),
            class_name="flex justify-between items-center mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Trigger Type",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("Select a trigger...", value="custom"),
                        rx.foreach(
                            AlertState.available_triggers,
                            lambda x: rx.el.option(x["name"], value=x["script"]),
                        ),
                        value=AlertState.rule_form_trigger_script,
                        on_change=AlertState.set_rule_form_trigger_script,
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                    ),
                    class_name="col-span-1",
                ),
                rx.el.div(
                    rx.el.label(
                        "Importance",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("Low", value="low"),
                        rx.el.option("Medium", value="medium"),
                        rx.el.option("High", value="high"),
                        rx.el.option("Critical", value="critical"),
                        value=AlertState.rule_form_importance,
                        on_change=AlertState.set_rule_form_importance,
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                    ),
                    class_name="col-span-1",
                ),
                rx.el.div(
                    rx.el.label(
                        "Category",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("General", value="General"),
                        rx.el.option("Market", value="Market"),
                        rx.el.option("System", value="System"),
                        rx.el.option("Security", value="Security"),
                        value=AlertState.rule_form_category,
                        on_change=AlertState.set_rule_form_category,
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                    ),
                    class_name="col-span-1",
                ),
                class_name="grid grid-cols-3 gap-4 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Rule Name",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.input(
                        on_change=AlertState.set_rule_form_name,
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                        placeholder="Name your rule",
                        default_value=AlertState.rule_form_name,
                    ),
                    class_name="col-span-2",
                ),
                rx.el.div(
                    rx.el.label(
                        "Display Duration",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.div(
                        rx.el.input(
                            type="number",
                            min="1",
                            on_change=AlertState.set_rule_form_duration_value,
                            class_name="w-16 px-2 py-2 border border-gray-300 rounded-l-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                            default_value=AlertState.rule_form_duration_value,
                        ),
                        rx.el.select(
                            rx.el.option("Min", value="Minutes"),
                            rx.el.option("Hr", value="Hours"),
                            rx.el.option("Day", value="Days"),
                            value=AlertState.rule_form_duration_unit,
                            on_change=AlertState.set_rule_form_duration_unit,
                            class_name="flex-1 px-2 py-2 border-t border-b border-r border-gray-300 rounded-r-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                        ),
                        class_name="flex",
                    ),
                    class_name="col-span-1",
                ),
                class_name="grid grid-cols-3 gap-4 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Action Targets (Emails)",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.div(
                        rx.foreach(
                            AlertState.rule_form_action_targets, action_target_item
                        ),
                        class_name="space-y-2 mb-2",
                    ),
                    rx.el.button(
                        "+ Add Email",
                        on_click=AlertState.add_action_target,
                        class_name="text-sm text-indigo-600 hover:text-indigo-800 font-medium",
                        type="button",
                    ),
                    class_name="col-span-2",
                ),
                rx.el.div(
                    rx.el.label(
                        "Check Every",
                        class_name="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    rx.el.div(
                        rx.el.input(
                            type="number",
                            min="1",
                            on_change=AlertState.set_rule_form_period_value,
                            class_name="w-16 px-2 py-2 border border-gray-300 rounded-l-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                            default_value=AlertState.rule_form_period_value,
                        ),
                        rx.el.select(
                            rx.el.option("Min", value="Minutes"),
                            rx.el.option("Hr", value="Hours"),
                            rx.el.option("Day", value="Days"),
                            value=AlertState.rule_form_period_unit,
                            on_change=AlertState.set_rule_form_period_unit,
                            class_name="flex-1 px-2 py-2 border-t border-b border-r border-gray-300 rounded-r-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                        ),
                        class_name="flex",
                    ),
                    class_name="col-span-1",
                ),
                class_name="grid grid-cols-3 gap-4 mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Parameters (JSON)",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.textarea(
                    on_change=AlertState.set_rule_form_parameters,
                    rows=3,
                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm font-mono bg-gray-50",
                    placeholder='{"ticker": "AAPL", "threshold": 100}',
                    default_value=AlertState.rule_form_parameters,
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                "Create Alert Rule",
                on_click=AlertState.add_rule,
                class_name="w-full inline-flex justify-center items-center py-2.5 px-4 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors",
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-200",
    )


def rule_item(rule: AlertRule) -> rx.Component:
    """Display a single rule in the list."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4(rule.name, class_name="text-base font-medium text-gray-900"),
                rx.el.div(
                    rx.el.span(
                        rule.category,
                        class_name="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200",
                    ),
                    rx.el.span(
                        rule.importance.upper(),
                        class_name=rx.match(
                            rule.importance.lower(),
                            (
                                "critical",
                                "ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800",
                            ),
                            (
                                "high",
                                "ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800",
                            ),
                            (
                                "medium",
                                "ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800",
                            ),
                            (
                                "low",
                                "ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800",
                            ),
                            "ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800",
                        ),
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex items-center",
            ),
            rx.el.p(
                f"Frequency: {rule.period_seconds}s",
                class_name="text-xs text-gray-500 mt-1",
            ),
            class_name="flex flex-col",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "Active", class_name="text-xs font-medium text-gray-700 mr-2"
                ),
                rx.el.button(
                    rx.cond(
                        rule.is_active,
                        rx.icon("toggle-right", class_name="w-8 h-8 text-indigo-600"),
                        rx.icon("toggle-left", class_name="w-8 h-8 text-gray-300"),
                    ),
                    on_click=AlertState.toggle_rule_active(rule.id),
                    class_name="focus:outline-none",
                ),
                class_name="flex items-center mr-4",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="w-4 h-4"),
                on_click=AlertState.delete_rule(rule.id),
                class_name="text-gray-400 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50",
            ),
            class_name="flex items-center",
        ),
        class_name="flex justify-between items-center p-4 bg-white border border-gray-100 rounded-xl hover:shadow-sm transition-shadow",
    )


def rule_list() -> rx.Component:
    """List of existing rules."""
    return rx.el.div(
        rx.el.h3("Existing Rules", class_name="text-lg font-bold text-gray-900 mb-4"),
        rx.el.div(
            rx.cond(
                AlertState.rules.length() > 0,
                rx.foreach(AlertState.rules, rule_item),
                rx.el.p(
                    "No rules defined yet.",
                    class_name="text-gray-500 text-sm italic p-4 text-center",
                ),
            ),
            class_name="space-y-3",
        ),
        class_name="mt-8",
    )


def rules_layout() -> rx.Component:
    """Layout for the Rules Page."""
    return rx.el.div(
        rx.el.div(rule_form(), class_name="w-full lg:w-1/3"),
        rx.el.div(rule_list(), class_name="w-full lg:w-2/3"),
        class_name="flex flex-col lg:flex-row gap-8",
    )