import customtkinter as ctk

from GUI.styles.table_style import (
    TABLE_BG,
    TABLE_RADIUS,
    TABLE_HEADER_BG,
    TABLE_HEADER_TEXT,
    TABLE_HEADER_FONT,
    TABLE_ROW_BG,
    TABLE_ROW_HOVER,
    TABLE_ROW_SELECTED,
    TABLE_TEXT,
    TABLE_MUTED_TEXT,
    TABLE_EMPTY_TEXT,
    TABLE_CELL_FONT,
    TABLE_ROW_PAD_Y,
    TABLE_CELL_PAD_X,
    TABLE_CELL_PAD_Y,
    TABLE_HEADER_PAD_X,
    TABLE_HEADER_PAD_Y,
    TABLE_OUTER_PAD_X,
    TABLE_OUTER_PAD_TOP,
    TABLE_OUTER_PAD_BOTTOM,
    TABLE_BODY_PAD_X,
    TABLE_BODY_PAD_TOP,
    TABLE_BODY_PAD_BOTTOM,
    TABLE_EMPTY_PAD_X,
    TABLE_EMPTY_PAD_Y,
    TABLE_HEADER_CORNER_RADIUS,
    TABLE_ROW_CORNER_RADIUS,
    TABLE_COLUMN_DEFAULT_WEIGHT,
    TABLE_COLUMN_DEFAULT_MIN_SIZE,
    TABLE_COLUMN_DEFAULT_ANCHOR,
    TABLE_HEADER_ANCHOR,
    TABLE_CELL_ANCHOR,
    TABLE_ENABLE_ROW_HOVER,
    TABLE_ENABLE_ROW_SELECTION,
    TABLE_HOVER_TEXT,
    TABLE_SELECTED_TEXT,
    TABLE_LOADING_TEXT,
    TABLE_LOADING_FONT,
    TABLE_EMPTY_FONT,
)


class Tables(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns,
        rows=None,
        headings=None,
        command=None,
        empty_text="No records found.",
        row_height=None,
        cell_pad_x=None,
        cell_pad_y=None,
        header_pad_x=None,
        header_pad_y=None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=TABLE_BG,
            corner_radius=TABLE_RADIUS,
            **kwargs
        )

        self.columns = columns or []
        self.rows = rows or []
        self.headings = headings or self._get_headings()
        self.command = command
        self.empty_text = empty_text

        self.row_height = (
            row_height
            if row_height is not None
            else 34
        )

        self.cell_pad_x = (
            cell_pad_x
            if cell_pad_x is not None
            else TABLE_CELL_PAD_X
        )

        self.cell_pad_y = (
            cell_pad_y
            if cell_pad_y is not None
            else TABLE_CELL_PAD_Y
        )

        self.header_pad_x = (
            header_pad_x
            if header_pad_x is not None
            else TABLE_HEADER_PAD_X
        )

        self.header_pad_y = (
            header_pad_y
            if header_pad_y is not None
            else TABLE_HEADER_PAD_Y
        )

        self.cells = []
        self.header_labels = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build()

    def _get_headings(self):
        headings = []

        for column in self.columns:
            if isinstance(column, dict):
                headings.append(column.get("label", ""))
            else:
                headings.append(str(column))

        return headings

    def _get_column_key(self, column):
        if isinstance(column, dict):
            return column.get(
                "key",
                column.get("label", "")
            )

        return column

    def _get_column_weight(self, column):
        if isinstance(column, dict):
            return column.get(
                "weight",
                TABLE_COLUMN_DEFAULT_WEIGHT
            )

        return TABLE_COLUMN_DEFAULT_WEIGHT

    def _get_column_minsize(self, column):
        if isinstance(column, dict):
            return column.get(
                "minsize",
                TABLE_COLUMN_DEFAULT_MIN_SIZE
            )

        return TABLE_COLUMN_DEFAULT_MIN_SIZE

    def _get_column_anchor(self, column):
        if isinstance(column, dict):
            return column.get(
                "anchor",
                TABLE_COLUMN_DEFAULT_ANCHOR
            )

        return TABLE_COLUMN_DEFAULT_ANCHOR

    def _get_column_font(self, column):
        if isinstance(column, dict):
            return column.get(
                "font",
                TABLE_CELL_FONT
            )

        return TABLE_CELL_FONT

    def _get_column_text_color(self, column):
        if isinstance(column, dict):
            return column.get(
                "text_color",
                TABLE_TEXT
            )

        return TABLE_TEXT

    def _get_column_heading_font(self, column):
        if isinstance(column, dict):
            return column.get(
                "heading_font",
                TABLE_HEADER_FONT
            )

        return TABLE_HEADER_FONT

    def _get_column_heading_color(self, column):
        if isinstance(column, dict):
            return column.get(
                "heading_color",
                TABLE_HEADER_TEXT
            )

        return TABLE_HEADER_TEXT

    def _get_column_row_color(self, column):
        if isinstance(column, dict):
            return column.get(
                "row_color",
                TABLE_ROW_BG
            )

        return TABLE_ROW_BG

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
            fg_color=TABLE_HEADER_BG,
            corner_radius=TABLE_HEADER_CORNER_RADIUS
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=TABLE_OUTER_PAD_X,
            pady=(
                TABLE_OUTER_PAD_TOP,
                TABLE_OUTER_PAD_BOTTOM // 2
            )
        )

        for column_index, column_config in enumerate(
            self.columns
        ):
            header.grid_columnconfigure(
                column_index,
                weight=self._get_column_weight(
                    column_config
                ),
                minsize=self._get_column_minsize(
                    column_config
                )
            )

            label = ctk.CTkLabel(
                header,
                text=self.headings[column_index],
                text_color=self._get_column_heading_color(
                    column_config
                ),
                font=self._get_column_heading_font(
                    column_config
                ),
                anchor=self._get_column_anchor(
                    column_config
                )
            )

            label.grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=self.header_pad_x,
                pady=self.header_pad_y
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
            padx=TABLE_BODY_PAD_X,
            pady=(
                TABLE_BODY_PAD_TOP,
                TABLE_BODY_PAD_BOTTOM
            )
        )

        for column_index, column_config in enumerate(
            self.columns
        ):
            body.grid_columnconfigure(
                column_index,
                weight=self._get_column_weight(
                    column_config
                ),
                minsize=self._get_column_minsize(
                    column_config
                )
            )

        if not self.rows:
            empty = ctk.CTkLabel(
                body,
                text=self.empty_text,
                text_color=TABLE_EMPTY_TEXT,
                font=TABLE_EMPTY_FONT,
            )

            empty.grid(
                row=0,
                column=0,
                columnspan=max(
                    1,
                    len(self.columns)
                ),
                sticky="ew",
                padx=TABLE_EMPTY_PAD_X,
                pady=TABLE_EMPTY_PAD_Y
            )

            return

        for row_index, row_data in enumerate(
            self.rows
        ):
            self._build_row(
                body,
                row_index,
                row_data
            )

    def _build_row(
        self,
        parent,
        row_index,
        row_data
    ):
        row = ctk.CTkFrame(
            parent,
            fg_color=TABLE_ROW_BG,
            corner_radius=TABLE_ROW_CORNER_RADIUS
        )

        row.grid(
            row=row_index,
            column=0,
            columnspan=max(
                1,
                len(self.columns)
            ),
            sticky="ew",
            pady=TABLE_ROW_PAD_Y
        )

        for column_index, column_config in enumerate(
            self.columns
        ):
            row.grid_columnconfigure(
                column_index,
                weight=self._get_column_weight(
                    column_config
                ),
                minsize=self._get_column_minsize(
                    column_config
                )
            )

        row_id = self._get_row_id(row_data)

        if self.command:
            row.bind(
                "<Button-1>",
                lambda event, value=row_data:
                self._row_clicked(value)
            )

        cell_labels = []

        for column_index, column_config in enumerate(
            self.columns
        ):
            key = self._get_column_key(
                column_config
            )

            value = self._get_value(
                row_data,
                key
            )

            label = ctk.CTkLabel(
                row,
                text="" if value is None else str(value),
                text_color=self._get_column_text_color(
                    column_config
                ),
                font=self._get_column_font(
                    column_config
                ),
                anchor=self._get_column_anchor(
                    column_config
                ),
                fg_color=self._get_column_row_color(
                    column_config
                ),
            )

            label.grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=self.cell_pad_x,
                pady=self.cell_pad_y
            )

            if self.command:
                label.bind(
                    "<Button-1>",
                    lambda event, value=row_data:
                    self._row_clicked(value)
                )

            cell_labels.append(label)

        self.cells.append({
            "id": row_id,
            "data": row_data,
            "widgets": cell_labels,
            "row": row,
        })

        if TABLE_ENABLE_ROW_HOVER:
            self._bind_row_hover(
                row,
                cell_labels
            )

    def _bind_row_hover(self, row, labels):
        def on_enter(event):
            row.configure(
                fg_color=TABLE_ROW_HOVER
            )

            for label in labels:
                label.configure(
                    fg_color=TABLE_ROW_HOVER,
                    text_color=TABLE_HOVER_TEXT
                )

        def on_leave(event):
            row.configure(
                fg_color=TABLE_ROW_BG
            )

            for label in labels:
                label.configure(
                    fg_color=TABLE_ROW_BG
                )

        row.bind(
            "<Enter>",
            on_enter
        )

        row.bind(
            "<Leave>",
            on_leave
        )

        for label in labels:
            label.bind(
                "<Enter>",
                on_enter
            )

            label.bind(
                "<Leave>",
                on_leave
            )

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

        if isinstance(
            row_data,
            (list, tuple)
        ) and row_data:
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
        for index, existing in enumerate(
            self.rows
        ):
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

    def set_empty_text(self, text):
        self.empty_text = text
        self._build()

    def refresh(self):
        self._build()

    def set_loading(
        self,
        loading=True,
        message="Loading..."
    ):
        for widget in self.winfo_children():
            widget.destroy()

        if loading:
            label = ctk.CTkLabel(
                self,
                text=message,
                text_color=TABLE_LOADING_TEXT,
                font=TABLE_LOADING_FONT
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

    def set_empty(
        self,
        message="No records found."
    ):
        self.empty_text = message
        self.rows = []
        self._build()