import reflex as rx
from app.states.ui_state import UIState


def nav_link(text: str, url: str) -> rx.Component:
    """Standard navigation link for desktop."""
    return rx.el.a(
        text,
        href=url,
        class_name="text-sm font-medium text-gray-500 hover:text-indigo-600 px-3 py-2 rounded-md transition-colors",
    )


def mobile_nav_link(text: str, icon: str, url: str) -> rx.Component:
    """Navigation link for mobile menu."""
    return rx.el.a(
        rx.icon(icon, class_name="w-5 h-5 mr-3 text-gray-500"),
        text,
        href=url,
        class_name="flex items-center px-4 py-3 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600 w-full transition-colors",
        on_click=UIState.close_sidebar,
    )


def sidebar() -> rx.Component:
    """Top navigation bar component (replaces sidebar)."""
    return rx.el.nav(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("shield-alert", class_name="h-8 w-8 text-indigo-600"),
                        rx.el.span(
                            "Sentinel",
                            class_name="ml-2 text-xl font-bold text-gray-900",
                        ),
                        class_name="flex-shrink-0 flex items-center cursor-pointer",
                        on_click=rx.redirect("/"),
                    ),
                    rx.el.div(
                        nav_link("Overview", "/"),
                        nav_link("Alert Rules", "/rules"),
                        nav_link("Alert Events", "/events"),
                        nav_link("Settings", "/settings"),
                        nav_link("Logs", "/logs"),
                        class_name="hidden md:ml-10 md:flex md:space-x-4",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    "Admin User",
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                rx.el.p(
                                    "admin@sentinel.io",
                                    class_name="text-xs text-gray-500",
                                ),
                                class_name="flex flex-col items-end mr-3",
                            ),
                            rx.image(
                                src="/placeholder.svg",
                                class_name="h-8 w-8 rounded-full bg-gray-200 border border-gray-200",
                            ),
                            class_name="flex items-center",
                        ),
                        class_name="hidden md:flex md:items-center",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                UIState.sidebar_open,
                                rx.icon("x", class_name="block h-6 w-6"),
                                rx.icon("menu", class_name="block h-6 w-6"),
                            ),
                            on_click=UIState.toggle_sidebar,
                            class_name="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500",
                        ),
                        class_name="-mr-2 flex items-center md:hidden",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex justify-between h-16",
            ),
            class_name="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8",
        ),
        rx.cond(
            UIState.sidebar_open,
            rx.el.div(
                rx.el.div(
                    mobile_nav_link("Overview", "layout-dashboard", "/"),
                    mobile_nav_link("Alert Rules", "list-filter", "/rules"),
                    mobile_nav_link("Alert Events", "bell-ring", "/events"),
                    mobile_nav_link("Settings", "settings", "/settings"),
                    mobile_nav_link("Logs", "scroll-text", "/logs"),
                    class_name="pt-2 pb-3 space-y-1",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.image(
                                src="/placeholder.svg",
                                class_name="h-10 w-10 rounded-full bg-gray-200 border border-gray-200",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    "Admin User",
                                    class_name="text-base font-medium text-gray-800",
                                ),
                                rx.el.div(
                                    "admin@sentinel.io",
                                    class_name="text-sm font-medium text-gray-500",
                                ),
                                class_name="ml-3",
                            ),
                            class_name="flex items-center px-5",
                        ),
                        class_name="pt-4 pb-4 border-t border-gray-200",
                    ),
                    class_name="border-t border-gray-200",
                ),
                class_name="md:hidden bg-white shadow-lg border-b border-gray-200 absolute w-full z-50",
            ),
        ),
        class_name="bg-white border-b border-gray-200 fixed w-full z-50 top-0",
    )