import customtkinter as ctk

from GUI.styles.colors import PANEL, TEXT_DARK, TEXT_MUTED
from GUI.styles.theme import (
    PANEL_RADIUS,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class Tables(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns,
        rows=None,
        headings=None,
        command=None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
            **kwargs
        )

        self.columns = columns
        self.rows = rows or []
        self.headings = headings or columns
        self.command = command
        self.cells = []
        self.header_labels = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build()

    def _build(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.cells.clear()
        self.header_labels.clear()

        self._build_header()
        self._build_body()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(8, 4)
        )

        for column in range(len(self.columns)):
            header.grid_columnconfigure(column, weight=1)

            label = ctk.CTkLabel(
                header,
                text=self.headings[column],
                text_color=TEXT_MUTED,
                font=FONT_BODY_BOLD,
                anchor="w"
            )

            label.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=8,
                pady=6
            )

            self.header_labels.append(label)

    def _build_body(self):
        body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(0, 8)
        )

        for column in range(len(self.columns)):
            body.grid_columnconfigure(column, weight=1)

        if not self.rows:
            empty = ctk.CTkLabel(
                body,
                text="No records found.",
                text_color=TEXT_MUTED,
                font=FONT_BODY
            )

            empty.grid(
                row=0,
                column=0,
                columnspan=len(self.columns),
                sticky="ew",
                padx=12,
                pady=30
            )

            return

        for row_index, row_data in enumerate(self.rows):
            self._build_row(
                body,
                row_index,
                row_data
            )

    def _build_row(self, parent, row_index, row_data):
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0
        )

        row.grid(
            row=row_index,
            column=0,
            columnspan=len(self.columns),
            sticky="ew",
            pady=2
        )

        for column in range(len(self.columns)):
            row.grid_columnconfigure(column, weight=1)

        row_id = self._get_row_id(row_data)

        row.bind(
            "<Button-1>",
            lambda event, value=row_data: self._row_clicked(value)
        )

        cell_labels = []

        for column, key in enumerate(self.columns):
            value = self._get_value(row_data, key)

            label = ctk.CTkLabel(
                row,
                text="" if value is None else str(value),
                text_color=TEXT_DARK,
                font=FONT_BODY,
                anchor="w"
            )

            label.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=8,
                pady=8
            )

            label.bind(
                "<Button-1>",
                lambda event, value=row_data: self._row_clicked(value)
            )

            cell_labels.append(label)

        self.cells.append({
            "id": row_id,
            "data": row_data,
            "widgets": cell_labels,
            "row": row,
        })

    def _get_value(self, row_data, key):
        if isinstance(row_data, dict):
            return row_data.get(key, "")

        if isinstance(key, int):
            try:
                return row_data[key]
            except (IndexError, TypeError):
                return ""

        try:
            return getattr(row_data, key)
        except AttributeError:
            return ""

    def _get_row_id(self, row_data):
        if isinstance(row_data, dict):
            return row_data.get("id")

        if hasattr(row_data, "id"):
            return row_data.id

        if isinstance(row_data, (list, tuple)) and row_data:
            return row_data[0]

        return None

    def _row_clicked(self, row_data):
        if self.command:
            self.command(row_data)

    def set_rows(self, rows):
        self.rows = rows or []
        self._build()

    def add_row(self, row_data):
        self.rows.append(row_data)
        self._build()

    def update_row(self, row_id, row_data):
        for index, existing in enumerate(self.rows):
            if self._get_row_id(existing) == row_id:
                self.rows[index] = row_data
                self._build()
                return

    def remove_row(self, row_id):
        self.rows = [
            row
            for row in self.rows
            if self._get_row_id(row) != row_id
        ]

        self._build()

    def clear(self):
        self.rows = []
        self._build()

    def get_rows(self):
        return list(self.rows)

    def get_row(self, row_id):
        for row in self.rows:
            if self._get_row_id(row) == row_id:
                return row

        return None

    def set_command(self, command):
        self.command = command

    def set_headings(self, headings):
        self.headings = headings
        self._build()

    def refresh(self):
        self._build()

    def set_loading(self, loading=True, message="Loading..."):
        for widget in self.winfo_children():
            widget.destroy()

        if loading:
            label = ctk.CTkLabel(
                self,
                text=message,
                text_color=TEXT_MUTED,
                font=FONT_BODY
            )

            label.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=20,
                pady=30
            )

        else:
            self._build()

    def set_empty(self, message="No records found."):
        for widget in self.winfo_children():
            widget.destroy()

        label = ctk.CTkLabel(
            self,
            text=message,
            text_color=TEXT_MUTED,
            font=FONT_BODY
        )

        label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=30
        )