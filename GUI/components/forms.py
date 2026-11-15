import tkinter as tk
import re
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from GUI.components.buttons import Buttons
from GUI.components.calendar import CalendarPicker
from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    INPUT_BG,
    INPUT_BORDER,
)
from GUI.styles.theme import (
    PANEL_RADIUS,
    INPUT_RADIUS,
    FONT_SECTION,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_FORM_LABEL,
    FONT_FORM_INPUT,
)
from GUI.utils.formatters import (
    format_currency,
    format_date,
    parse_currency,
    parse_date,
)



class FormWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title,
        width=560,
        height=500,
    ):
        super().__init__(master)

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self.panel = None
        self.body = None
        self.button_row = None
        self.buttons = None

        self._build_base(title)

        self.calendar_image = tk.PhotoImage(
            file=os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(__file__)
                    )
                ),
                "Assets",
                "Images",
                "calendar.png",
            )
        )

        image_width = self.calendar_image.width()
        image_height = self.calendar_image.height()

        scale = max(
            1,
            min(
                image_width // 20,
                image_height // 20,
            ),
        )

        if scale > 1:
            self.calendar_image = self.calendar_image.subsample(
                scale,
                scale,
            )

    def _build_base(self, title):
        self.panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )

        self.panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        ctk.CTkLabel(
            self.panel,
            text=title,
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        self.body = ctk.CTkFrame(
            self.panel,
            fg_color="transparent",
            corner_radius=0,
        )

        self.body.pack(
            fill="both",
            expand=True,
            padx=28,
        )

        self.button_row = ctk.CTkFrame(
            self.panel,
            fg_color="transparent",
            corner_radius=0,
        )

        self.button_row.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

    def _create_wrapper(self, label):
        wrapper = ctk.CTkFrame(
            self.body,
            fg_color="transparent",
            corner_radius=0,
        )

        wrapper.pack(
            fill="x",
            pady=(0, 14),
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            pady=(0, 5),
        )

        return wrapper

    def _create_entry(
        self,
        master,
        value="",
        placeholder_text=None,
    ):
        entry = ctk.CTkEntry(
            master,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
            placeholder_text=placeholder_text,
        )

        if value not in (None, ""):
            entry.insert(
                0,
                str(value),
            )

        return entry

    def add_description(self, text):
        ctk.CTkLabel(
            self.body,
            text=text,
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            pady=(0, 18),
        )

    def add_field(
        self,
        label,
        value="",
        placeholder_text=None,
    ):
        wrapper = self._create_wrapper(label)

        entry = self._create_entry(
            wrapper,
            value=value,
            placeholder_text=placeholder_text,
        )

        entry.pack(
            fill="x",
        )

        return entry

    def add_date_field(
        self,
        label,
        value="",
        placeholder_text="MM/DD/YYYY",
    ):
        wrapper = self._create_wrapper(label)

        row = ctk.CTkFrame(
            wrapper,
            fg_color="transparent",
            corner_radius=0,
        )

        row.pack(
            fill="x",
        )

        row.grid_columnconfigure(
            0,
            weight=1,
        )

        display_value = self._display_date_value(value)

        entry = self._create_entry(
            row,
            value=display_value,
            placeholder_text=placeholder_text,
        )

        entry.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        calendar_button = tk.Button(
            row,
            image=self.calendar_image,
            width=42,
            height=36,
            bg=INPUT_BORDER,
            activebackground=PANEL_HOVER,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            command=lambda: self._open_calendar(entry),
        )

        calendar_button.grid(
            row=0,
            column=1,
            padx=(6, 0),
        )

        entry.bind(
            "<KeyRelease>",
            lambda event: self._format_date_input(entry),
        )

        entry.bind(
            "<FocusOut>",
            lambda event: self._normalize_date_input(entry),
        )

        return entry

    def _display_date_value(self, value):
        if value in (None, ""):
            return ""

        if isinstance(value, datetime):
            value = value.date()

        if isinstance(value, date):
            return value.strftime("%m/%d/%Y")

        value = str(value).strip()

        if not value:
            return ""

        try:
            parsed = parse_date(value)
            return parsed.strftime("%m/%d/%Y")
        except ValueError:
            pass

        for fmt in (
            "%m/%d/%Y",
            "%m/%d/%y",
            "%Y-%m-%d",
            "%d/%m/%Y",
        ):
            try:
                parsed = datetime.strptime(
                    value,
                    fmt,
                ).date()

                return parsed.strftime("%m/%d/%Y")
            except ValueError:
                continue

        return value

    def _open_calendar(self, entry):
        current_value = entry.get().strip()

        try:
            initial_date = self.get_date_value(entry)
        except ValueError:
            initial_date = date.today()

        CalendarPicker(
            self,
            initial_date=initial_date,
            on_selected=lambda selected_date: self._set_date_value(
                entry,
                selected_date,
            ),
        )

    def _set_date_value(
        self,
        entry,
        selected_date,
    ):
        entry.delete(
            0,
            "end",
        )

        entry.insert(
            0,
            selected_date.strftime("%m/%d/%Y"),
        )

    def _format_date_input(self, entry):
        value = entry.get()

        digits = re.sub(
            r"\D",
            "",
            value,
        )

        if len(digits) > 8:
            digits = digits[:8]

        if len(digits) > 4:
            formatted = (
                f"{digits[:2]}/"
                f"{digits[2:4]}/"
                f"{digits[4:]}"
            )
        elif len(digits) > 2:
            formatted = (
                f"{digits[:2]}/"
                f"{digits[2:]}"
            )
        else:
            formatted = digits

        if formatted == value:
            return

        cursor_position = entry.index("insert")

        old_digits_before_cursor = re.sub(
            r"\D",
            "",
            value[:cursor_position],
        )

        entry.delete(
            0,
            "end",
        )

        entry.insert(
            0,
            formatted,
        )

        target_digits = len(old_digits_before_cursor)
        digit_count = 0
        new_cursor = 0

        for character in formatted:
            new_cursor += 1

            if character.isdigit():
                digit_count += 1

            if digit_count >= target_digits:
                break

        entry.icursor(
            min(
                new_cursor,
                len(formatted),
            )
        )

    def _normalize_date_input(self, entry):
        value = entry.get().strip()

        if not value:
            return

        try:
            parsed = self._parse_date_input(value)

            entry.delete(
                0,
                "end",
            )

            entry.insert(
                0,
                parsed.strftime("%m/%d/%Y"),
            )

        except ValueError:
            return

    def _parse_date_input(self, value):
        value = value.strip()

        for fmt in (
            "%m/%d/%Y",
            "%m/%d/%y",
            "%Y-%m-%d",
            "%d/%m/%Y",
        ):
            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).date()
            except ValueError:
                continue

        try:
            return parse_date(value)
        except ValueError:
            raise ValueError(
                "Please enter a valid date."
            )

    def get_date_value(self, entry):
        return self._parse_date_input(
            entry.get()
        )

    def add_currency_field(
        self,
        label,
        value="",
        placeholder_text="0.00",
    ):
        wrapper = self._create_wrapper(label)

        entry = self._create_entry(
            wrapper,
            placeholder_text=placeholder_text,
        )

        entry.pack(
            fill="x",
        )

        if value not in (None, ""):
            formatted_value = self._format_initial_currency(
                value
            )

            entry.insert(
                0,
                formatted_value,
            )

        entry.bind(
            "<KeyRelease>",
            lambda event: self._format_currency_input(entry),
        )

        entry.bind(
            "<FocusOut>",
            lambda event: self._normalize_currency_input(entry),
        )

        return entry

    def _format_initial_currency(self, value):
        try:
            if isinstance(value, int):
                amount = Decimal(value) / Decimal("100")
            else:
                numeric = Decimal(str(value))

                if numeric == numeric.to_integral_value():
                    amount = numeric / Decimal("100")
                else:
                    amount = numeric

            return f"{amount:,.2f}"

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):
            return str(value)

    def _format_currency_input(self, entry):
        value = entry.get()

        if not value:
            return

        cursor_position = entry.index("insert")

        before_cursor = value[:cursor_position]

        digits_before_cursor = re.sub(
            r"[^\d.]",
            "",
            before_cursor,
        )

        cleaned = re.sub(
            r"[^\d.]",
            "",
            value,
        )

        if cleaned.count(".") > 1:
            first_dot = cleaned.find(".")
            cleaned = (
                cleaned[:first_dot + 1]
                + cleaned[first_dot + 1:].replace(".", "")
            )

        if "." in cleaned:
            whole, decimal = cleaned.split(
                ".",
                1,
            )

            decimal = decimal[:2]

            if whole:
                try:
                    whole = f"{int(whole):,}"
                except ValueError:
                    whole = ""

            if value.endswith(".") and not decimal:
                formatted = f"{whole}."
            elif decimal:
                formatted = f"{whole}.{decimal}"
            else:
                formatted = whole

        else:
            if cleaned:
                try:
                    formatted = f"{int(cleaned):,}"
                except ValueError:
                    formatted = ""
            else:
                formatted = ""

        if formatted == value:
            return

        entry.delete(
            0,
            "end",
        )

        entry.insert(
            0,
            formatted,
        )

        target_count = len(digits_before_cursor)
        current_count = 0
        new_cursor = 0

        for character in formatted:
            new_cursor += 1

            if character.isdigit() or character == ".":
                current_count += 1

            if current_count >= target_count:
                break

        entry.icursor(
            min(
                new_cursor,
                len(formatted),
            )
        )

    def _normalize_currency_input(self, entry):
        value = entry.get().strip()

        if not value:
            return

        try:
            cents = parse_currency(value)

            amount = Decimal(cents) / Decimal("100")

            entry.delete(
                0,
                "end",
            )

            entry.insert(
                0,
                f"{amount:,.2f}",
            )

        except ValueError:
            return

    def get_currency_value(self, entry):
        return parse_currency(
            entry.get()
        )

    def add_selector(
            self,
            label,
            values,
            value=None,
    ):
        wrapper = self._create_wrapper(label)

        values = list(values or [])

        display_values = []

        for item in values:
            if isinstance(item, str) and " - " in item:
                display_values.append(
                    item.split(" - ", 1)[1]
                )
            else:
                display_values.append(
                    str(item)
                )

        selector = ctk.CTkOptionMenu(
            wrapper,
            values=display_values or ["No options available"],
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

        selector.pack(
            fill="x",
        )

        if value is not None:
            if value in values:
                index = values.index(value)
                selector.set(
                    display_values[index]
                )
            elif value in display_values:
                selector.set(value)
            elif display_values:
                selector.set(display_values[0])
        elif display_values:
            selector.set(display_values[0])
        else:
            selector.set("No options available")

        original_get = selector.get

        def get_original_value():
            displayed_value = original_get()

            if displayed_value in display_values:
                index = display_values.index(
                    displayed_value
                )
                return values[index]

            return displayed_value

        selector.get = get_original_value

        return selector

    def add_buttons(
        self,
        save_text="Save",
        save_command=None,
        cancel_command=None,
    ):
        if self.buttons is not None:
            self.buttons.destroy()

        self.buttons = Buttons(
            self.button_row,
            actions=[
                {
                    "label": "Cancel",
                    "command": (
                        cancel_command
                        if cancel_command
                        else self.destroy
                    ),
                    "style": "default",
                    "height": 40,
                    "padx": 0,
                    "pady": 0,
                },
                {
                    "label": save_text,
                    "command": save_command,
                    "style": "primary",
                    "height": 40,
                    "padx": 0,
                    "pady": 0,
                },
            ],
            columns=2,
            padx=0,
            pady=0,
        )

        self.buttons.pack(
            fill="x",
        )

        return self.buttons


class SelectionForm(FormWindow):
    def __init__(
        self,
        master,
        title,
        items,
        display_key="name",
        value_key="id",
        on_selected=None,
        description=None,
        select_button_text="Select",
        width=440,
        height=300,
    ):
        super().__init__(
            master,
            title,
            width,
            height,
        )

        self.items = items or []
        self.display_key = display_key
        self.value_key = value_key
        self.on_selected = on_selected

        if description:
            self.add_description(
                description
            )

        values = [
            self._format_item(item)
            for item in self.items
        ]

        self.selector = self.add_selector(
            "Selection",
            values,
        )

        self.add_buttons(
            save_text=select_button_text,
            save_command=self._select,
        )

    def _format_item(self, item):
        if isinstance(item, dict):
            item_id = item.get(
                self.value_key,
                "",
            )

            display_value = item.get(
                self.display_key,
                "",
            )

            return f"{item_id} - {display_value}"

        if isinstance(item, (list, tuple)):
            item_id = (
                item[0]
                if item
                else ""
            )

            display_value = (
                item[1]
                if len(item) > 1
                else ""
            )

            return f"{item_id} - {display_value}"

        item_id = getattr(
            item,
            self.value_key,
            "",
        )

        display_value = getattr(
            item,
            self.display_key,
            "",
        )

        return f"{item_id} - {display_value}"

    def _get_selected_item(self):
        value = self.selector.get()

        if not value:
            return None

        try:
            selected_id = int(
                value.split(
                    " - ",
                    1,
                )[0]
            )
        except (
            ValueError,
            IndexError,
        ):
            return None

        for item in self.items:
            if isinstance(item, dict):
                item_id = item.get(
                    self.value_key
                )

            elif isinstance(
                item,
                (list, tuple),
            ):
                item_id = (
                    item[0]
                    if item
                    else None
                )

            else:
                item_id = getattr(
                    item,
                    self.value_key,
                    None,
                )

            if item_id == selected_id:
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