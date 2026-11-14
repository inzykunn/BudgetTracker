import customtkinter as ctk

from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    INPUT_BG,
    INPUT_BORDER,
)
from GUI.styles.theme import (
    PANEL_RADIUS,
    BUTTON_RADIUS,
    INPUT_RADIUS,
    FONT_SECTION,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_FORM_INPUT,
)


class Selector(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title,
        items,
        display_key=None,
        value_key="id",
        on_selected=None,
        description=None,
        select_button_text="Select",
        width=440,
        height=300,
    ):
        super().__init__(master)

        self.items = items or []
        self.display_key = display_key
        self.value_key = value_key
        self.on_selected = on_selected

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build(
            title,
            description,
            select_button_text,
        )

    def _build(
        self,
        title,
        description,
        select_button_text,
    ):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        ctk.CTkLabel(
            panel,
            text=title,
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=24,
            pady=(22, 4),
        )

        if description:
            ctk.CTkLabel(
                panel,
                text=description,
                font=FONT_BODY,
                text_color=TEXT_DARK,
            ).pack(
                anchor="w",
                padx=24,
                pady=(0, 14),
            )

        values = [
            self._format_item(item)
            for item in self.items
        ]

        self.selector = ctk.CTkOptionMenu(
            panel,
            values=values,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            button_color=INPUT_BORDER,
            button_hover_color=PANEL_HOVER,
            dropdown_fg_color=PANEL,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXT_DARK,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        self.selector.pack(
            fill="x",
            padx=24,
            pady=(0, 20),
        )

        if values:
            self.selector.set(values[0])

        button_row = ctk.CTkFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
        )

        button_row.pack(
            fill="x",
            padx=24,
            pady=(0, 22),
        )

        button_row.grid_columnconfigure(
            0,
            weight=1,
        )

        button_row.grid_columnconfigure(
            1,
            weight=1,
        )

        ctk.CTkButton(
            button_row,
            text="Cancel",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self.destroy,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6),
        )

        ctk.CTkButton(
            button_row,
            text=select_button_text,
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._select,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _format_item(self, item):
        if isinstance(item, dict):
            display_value = (
                item.get(self.display_key, "")
                if self.display_key
                else item
            )

            if isinstance(display_value, dict):
                display_value = str(display_value)

            return str(display_value)

        if self.display_key:
            display_value = getattr(
                item,
                self.display_key,
                "",
            )

            return str(display_value)

        if isinstance(item, (list, tuple)):
            return str(
                item[1]
                if len(item) > 1
                else item[0] if item else ""
            )

        return str(item)

    def _get_selected_item(self):
        value = self.selector.get()

        if not value:
            return None

        for item in self.items:
            if self._format_item(item) == value:
                return item

        return None

    def _select(self):
        item = self._get_selected_item()

        if item is None:
            return

        self.destroy()

        if self.on_selected:
            self.on_selected(item)

    def get_selected(self):
        return self._get_selected_item()