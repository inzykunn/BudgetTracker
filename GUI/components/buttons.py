import customtkinter as ctk

from GUI.styles.colors import (
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    DANGER,
    DANGER_HOVER,
    SUCCESS,
    SUCCESS_HOVER,
)
from GUI.styles.theme import (
    BUTTON_RADIUS,
    BUTTON_HEIGHT,
    BUTTON_PAD_X,
    BUTTON_PAD_Y,
    FONT_BODY_BOLD,
)


class Buttons(ctk.CTkFrame):
    def __init__(
        self,
        master,
        actions=None,
        columns=None,
        height=BUTTON_HEIGHT,
        padx=BUTTON_PAD_X,
        pady=BUTTON_PAD_Y,
    ):
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=0,
        )

        self.actions = []
        self.buttons = []
        self.columns = columns
        self.button_height = height
        self.button_pad_x = padx
        self.button_pad_y = pady

        if actions:
            self.set_actions(actions)

    def _get_style(self, style):
        if style == "primary":
            return (
                TEXT_DARK,
                "#285B4B",
                TEXT_LIGHT,
            )

        if style == "danger":
            return (
                DANGER,
                DANGER_HOVER,
                TEXT_LIGHT,
            )

        if style == "success":
            return (
                SUCCESS,
                SUCCESS_HOVER,
                TEXT_LIGHT,
            )

        return (
            PANEL,
            PANEL_HOVER,
            TEXT_DARK,
        )

    def _create_button(self, action, row, column):
        if isinstance(action, dict):
            label = action.get(
                "label",
                "",
            )

            command = action.get(
                "command"
            )

            style = action.get(
                "style",
                "default",
            )

            width = action.get(
                "width"
            )

            height = action.get(
                "height",
                self.button_height,
            )

            state = action.get(
                "state",
                "normal",
            )

            expand = action.get(
                "expand",
                True,
            )

            padx = action.get(
                "padx",
                self.button_pad_x,
            )

            pady = action.get(
                "pady",
                self.button_pad_y,
            )

        else:
            label, command = action

            style = "default"
            width = None
            height = self.button_height
            state = "normal"
            expand = True
            padx = self.button_pad_x
            pady = self.button_pad_y

        fg_color, hover_color, text_color = self._get_style(
            style
        )

        button_kwargs = {
            "master": self,
            "text": label,
            "command": command,
            "height": height,
            "corner_radius": BUTTON_RADIUS,
            "fg_color": fg_color,
            "hover_color": hover_color,
            "text_color": text_color,
            "font": FONT_BODY_BOLD,
            "state": state,
        }

        if width is not None:
            button_kwargs["width"] = width

        button = ctk.CTkButton(
            **button_kwargs
        )

        button.grid(
            row=row,
            column=column,
            sticky="ew" if expand else "",
            padx=padx,
            pady=pady,
        )

        return button

    def set_actions(self, actions):
        self.clear()

        self.actions = list(actions or [])

        if not self.actions:
            return

        columns = self.columns

        if columns is None:
            columns = len(self.actions)

        columns = max(
            1,
            min(columns, len(self.actions)),
        )

        for column in range(columns):
            self.grid_columnconfigure(
                column,
                weight=1,
            )

        for index, action in enumerate(self.actions):
            row = index // columns
            column = index % columns

            button = self._create_button(
                action,
                row,
                column,
            )

            self.buttons.append(button)

    def add_action(self, action):
        actions = list(self.actions)
        actions.append(action)
        self.set_actions(actions)

    def remove_action(self, index):
        if index < 0 or index >= len(self.actions):
            return

        actions = list(self.actions)
        actions.pop(index)
        self.set_actions(actions)

    def clear(self):
        for button in self.buttons:
            try:
                button.destroy()
            except Exception:
                pass

        self.buttons = []

    def set_button_text(self, index, text):
        if 0 <= index < len(self.buttons):
            self.buttons[index].configure(
                text=text
            )

    def set_button_state(self, index, state):
        if 0 <= index < len(self.buttons):
            self.buttons[index].configure(
                state=state
            )

    def set_button_style(self, index, style):
        if 0 <= index < len(self.buttons):
            fg_color, hover_color, text_color = self._get_style(
                style
            )

            self.buttons[index].configure(
                fg_color=fg_color,
                hover_color=hover_color,
                text_color=text_color,
            )

    def set_button_command(self, index, command):
        if 0 <= index < len(self.buttons):
            self.buttons[index].configure(
                command=command
            )

    def get_button(self, index):
        if 0 <= index < len(self.buttons):
            return self.buttons[index]

        return None

    def get_buttons(self):
        return list(self.buttons)

    def get_actions(self):
        return list(self.actions)