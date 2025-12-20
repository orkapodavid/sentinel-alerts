import reflex as rx


class UIState(rx.State):
    """State for UI-related interactions."""

    sidebar_open: bool = False
    dark_mode: bool = False

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open

    @rx.event
    def close_sidebar(self):
        self.sidebar_open = False

    @rx.event
    def toggle_dark_mode(self, value: bool):
        self.dark_mode = value
        return rx.toggle_color_mode