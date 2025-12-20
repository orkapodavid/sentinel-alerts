import reflex as rx
from app.states.ui_state import UIState
from app.states.alert_state import AlertState


def template_row(template: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h4(template["name"], class_name="text-sm font-medium text-gray-900"),
            rx.el.code(
                template["json"],
                class_name="text-xs text-gray-500 font-mono mt-1 block truncate max-w-md",
            ),
            class_name="flex-1",
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="w-4 h-4 text-red-500"),
            on_click=AlertState.remove_template(template["name"]),
            class_name="p-2 hover:bg-red-50 rounded-lg transition-colors",
        ),
        class_name="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100",
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
                    "Alert Templates", class_name="text-lg font-bold text-gray-900 mb-4"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h4(
                            "Add New Template",
                            class_name="text-sm font-medium text-gray-900 mb-3",
                        ),
                        rx.el.div(
                            rx.el.input(
                                placeholder="Template Name (e.g. New Metric Alert)",
                                on_change=AlertState.set_new_template_name,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm mb-3",
                                default_value=AlertState.new_template_name,
                            ),
                            rx.el.textarea(
                                placeholder='{"metric": "new_val", "threshold": 100}',
                                on_change=AlertState.set_new_template_json,
                                rows=3,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm font-mono bg-gray-50 mb-3",
                                default_value=AlertState.new_template_json,
                            ),
                            rx.el.button(
                                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                                "Add Template",
                                on_click=AlertState.add_template,
                                class_name="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium text-sm",
                            ),
                            class_name="p-4 bg-gray-50 rounded-xl border border-gray-200 mb-6",
                        ),
                        rx.el.h4(
                            "Existing Templates",
                            class_name="text-sm font-medium text-gray-900 mb-3",
                        ),
                        rx.el.div(
                            rx.foreach(AlertState.template_list, template_row),
                            class_name="space-y-3",
                        ),
                        class_name="flex flex-col",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
            ),
            class_name="max-w-4xl",
        ),
        class_name="w-full",
    )