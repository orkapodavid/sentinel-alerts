import reflex as rx
from app.states.ui_state import UIState
from app.states.alert_state import AlertState


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
            class_name="max-w-4xl",
        ),
        class_name="w-full",
    )