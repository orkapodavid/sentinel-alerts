import reflex as rx


def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    """Sidebar navigation item."""
    return rx.el.a(
        rx.el.div(
            rx.icon(icon, class_name="w-5 h-5 text-gray-500"),
            rx.el.span(text, class_name="font-medium text-gray-700"),
            class_name="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors duration-200",
        ),
        href=url,
        class_name="block w-full",
    )


def sidebar() -> rx.Component:
    """Main sidebar component."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("shield-alert", class_name="w-8 h-8 text-indigo-600"),
                rx.el.span("Sentinel", class_name="text-xl font-bold text-gray-900"),
                class_name="flex items-center gap-3 px-2",
            ),
            class_name="h-16 flex items-center border-b border-gray-100 mb-6",
        ),
        rx.el.nav(
            rx.el.div(
                rx.el.p(
                    "DASHBOARD",
                    class_name="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2",
                ),
                rx.el.div(
                    sidebar_item("Overview", "layout-dashboard", "/"),
                    class_name="space-y-1",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.p(
                    "MANAGEMENT",
                    class_name="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2",
                ),
                rx.el.div(
                    sidebar_item("Alert Rules", "list-filter", "/rules"),
                    sidebar_item("Alert Events", "bell-ring", "/events"),
                    class_name="space-y-1",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.p(
                    "SYSTEM",
                    class_name="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 px-2",
                ),
                rx.el.div(
                    sidebar_item("Settings", "settings", "/settings"),
                    sidebar_item("Logs", "scroll-text", "/logs"),
                    class_name="space-y-1",
                ),
            ),
            class_name="flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.image(
                        src="/placeholder.svg",
                        class_name="w-8 h-8 rounded-full bg-gray-200",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Admin User", class_name="text-sm font-medium text-gray-900"
                        ),
                        rx.el.p(
                            "admin@sentinel.io", class_name="text-xs text-gray-500"
                        ),
                        class_name="flex flex-col",
                    ),
                    class_name="flex items-center gap-3",
                ),
                rx.icon(
                    "log-out",
                    class_name="w-5 h-5 text-gray-400 hover:text-gray-600 cursor-pointer",
                ),
                class_name="flex items-center justify-between",
            ),
            class_name="border-t border-gray-100 pt-4 mt-auto",
        ),
        class_name="w-64 h-screen bg-white border-r border-gray-200 flex flex-col p-4 shrink-0 fixed top-0 left-0",
    )