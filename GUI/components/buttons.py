import customtkinter as ctk

from GUI.styles.colors import PANEL, PANEL_HOVER, TEXT_DARK
from GUI.styles.theme import (
    BUTTON_RADIUS,
    BUTTON_HEIGHT,
    BUTTON_PAD_X,
    BUTTON_PAD_Y,
    FONT_BODY_BOLD,
)


class Buttons(ctk.CTkFrame):
    def __init__(self, master, actions, columns=None):
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=0,
        )

        self.actions = actions
        self.buttons = []

        if not actions:
            return

        if columns is None:
            columns = len(actions)

        columns = max(1, min(columns, len(actions)))

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

        for index, action in enumerate(actions):
            row = index // columns
            column = index % columns

            button = self._create_button(
                action,
                row,
                column,
            )

            self.buttons.append(button)

    def _create_button(self, action, row, column):
        label, callback = action

        button = ctk.CTkButton(
            self,
            text=label,
            command=callback,
            height=BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL,
            hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
        )

        button.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=BUTTON_PAD_X,
            pady=BUTTON_PAD_Y,
        )

        return button

    def set_actions(self, actions):
        self.clear()

        self.actions = actions

        if not actions:
            return

        columns = min(len(actions), len(self.buttons) or len(actions))

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

        for index, action in enumerate(actions):
            row = index // columns
            column = index % columns

            button = self._create_button(
                action,
                row,
                column,
            )

            self.buttons.append(button)

    def clear(self):
        for button in self.buttons:
            button.destroy()

        self.buttons.clear()

    def set_button_text(self, index, text):
        if 0 <= index < len(self.buttons):
            self.buttons[index].configure(text=text)

    def set_button_state(self, index, state):
        if 0 <= index < len(self.buttons):
            self.buttons[index].configure(state=state)

    def get_button(self, index):
        if 0 <= index < len(self.buttons):
            return self.buttons[index]

        return None