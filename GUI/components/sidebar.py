import customtkinter as ctk

from GUI.styles.colors import SIDEBAR, SIDEBAR_HOVER, TEXT_LIGHT, TEXT_MUTED
from GUI.styles.theme import (
    SIDEBAR_WIDTH,
    SIDEBAR_PAD_X,
    SIDEBAR_PAD_Y,
    BUTTON_RADIUS,
    BUTTON_HEIGHT,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, items, command=None):
        super().__init__(
            master,
            width=SIDEBAR_WIDTH,
            fg_color=SIDEBAR,
            corner_radius=0,
        )

        self.grid_propagate(False)

        self.items = items
        self.command = command
        self.buttons = {}
        self.active_item = None

        self._build()

    def _build(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.buttons.clear()

        for item in self.items:
            key = item.get("key", item.get("label"))
            label = item.get("label", key)
            callback = item.get("command")

            if callback is None:
                callback = self.command

            self._create_button(
                key=key,
                label=label,
                command=callback,
            )

    def _create_button(self, key, label, command):
        button = ctk.CTkButton(
            self,
            text=label,
            command=lambda k=key, c=command: self._handle_click(k, c),
            height=BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            fg_color="transparent",
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_LIGHT,
            font=FONT_BODY,
            anchor="w",
        )

        button.pack(
            fill="x",
            padx=SIDEBAR_PAD_X,
            pady=SIDEBAR_PAD_Y,
        )

        self.buttons[key] = button

    def _handle_click(self, key, command):
        self.set_active(key)

        if command:
            command(key)

    def set_active(self, key):
        if self.active_item in self.buttons:
            self.buttons[self.active_item].configure(
                fg_color="transparent",
                font=FONT_BODY,
            )

        if key in self.buttons:
            self.buttons[key].configure(
                fg_color=SIDEBAR_HOVER,
                font=FONT_BODY_BOLD,
            )
            self.active_item = key

    def set_items(self, items):
        self.items = items
        self.active_item = None
        self._build()

    def add_item(self, key, label, command=None):
        self.items.append({
            "key": key,
            "label": label,
            "command": command,
        })

        self._build()

    def remove_item(self, key):
        self.items = [
            item
            for item in self.items
            if item.get("key", item.get("label")) != key
        ]

        if self.active_item == key:
            self.active_item = None

        self._build()

    def get_button(self, key):
        return self.buttons.get(key)

    def set_enabled(self, key, enabled=True):
        button = self.buttons.get(key)

        if button:
            button.configure(
                state="normal" if enabled else "disabled"
            )