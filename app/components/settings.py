import reflex as rx
from app.states.ui_state import UIState
from app.states.alert_state import AlertState


def settings_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1("System Settings", class_name="text-2xl font-bold text-gray-900 mb-6"),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Prefect Integration",
                    class_name="text-lg font-bold text-gray-900 mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Prefect API URL",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                on_change=AlertState.set_prefect_api_url,
                                default_value=AlertState.prefect_api_url,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                                placeholder="http://localhost:4200/api",
                            ),
                            rx.el.p(
                                "The API endpoint for your Prefect server.",
                                class_name="mt-1 text-xs text-gray-500",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Prefect UI URL",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                on_change=AlertState.set_prefect_ui_url,
                                default_value=AlertState.prefect_ui_url,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
                                placeholder="http://localhost:4200",
                            ),
                            rx.el.p(
                                "Base URL for the Prefect Dashboard UI.",
                                class_name="mt-1 text-xs text-gray-500",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("plug", class_name="w-4 h-4 mr-2"),
                                "Test Connection",
                                on_click=AlertState.test_prefect_connection,
                                class_name="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                            ),
                            rx.el.div(
                                rx.cond(
                                    AlertState.prefect_connection_status,
                                    rx.el.span(
                                        "Connected",
                                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
                                    ),
                                    rx.el.span(
                                        "Disconnected",
                                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800",
                                    ),
                                ),
                                class_name="ml-4 flex items-center",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.cond(
                            ~AlertState.prefect_connection_status,
                            rx.el.p(
                                AlertState.prefect_status_message,
                                class_name="mt-2 text-sm text-red-600",
                            ),
                        ),
                        class_name="flex flex-col",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
                class_name="mb-8",
            ),
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
            class_name="max-w-6xl",
        ),
        class_name="w-full pb-20",
    )