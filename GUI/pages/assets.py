from datetime import date
import calendar
from tkinter import messagebox
import customtkinter as ctk

from services import asset_service, account_service
from GUI.components.tables import Tables
from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    SUCCESS,
    DANGER,
    INPUT_BG,
    INPUT_BORDER,
    TEXT_MUTED,
)
from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    PANEL_RADIUS,
    BUTTON_RADIUS,
    INPUT_RADIUS,
    FONT_SECTION,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_FORM_LABEL,
    FONT_FORM_INPUT,
    FONT_SMALL_BOLD,
)


class DatePicker(ctk.CTkToplevel):
    def __init__(self, master, entry):
        super().__init__(master)
        self.entry = entry
        self.current = self._read_date()

        self.title("Select Date")
        self.geometry("390x350")
        self.resizable(False, False)
        self.configure(fg_color=PANEL)
        self.transient(master)
        self.grab_set()

        self._build()

    def _read_date(self):
        try:
            return date.fromisoformat(self.entry.get().strip())
        except ValueError:
            return date.today()

    def _build(self):
        for widget in self.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header.pack(
            fill="x",
            padx=12,
            pady=(12, 8),
        )

        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            header,
            text="‹",
            width=38,
            height=32,
            corner_radius=8,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            command=self._previous_month,
        ).grid(
            row=0,
            column=0,
            padx=(0, 6),
        )

        month_values = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        self.month_combo = ctk.CTkComboBox(
            header,
            values=month_values,
            width=125,
            height=32,
            corner_radius=8,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            button_color=PANEL_HOVER,
            button_hover_color=CONTENT,
            dropdown_fg_color=INPUT_BG,
            dropdown_hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self._set_month,
        )
        self.month_combo.set(
            month_values[self.current.month - 1]
        )
        self.month_combo.grid(
            row=0,
            column=1,
            padx=3,
        )

        year_frame = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        year_frame.grid(
            row=0,
            column=2,
            padx=3,
        )

        self.year_entry = ctk.CTkEntry(
            year_frame,
            width=70,
            height=32,
            corner_radius=8,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            justify="center",
        )
        self.year_entry.insert(0, str(self.current.year))
        self.year_entry.grid(
            row=0,
            column=0,
        )

        ctk.CTkButton(
            year_frame,
            text="✓",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            command=self._set_year,
        ).grid(
            row=0,
            column=1,
            padx=(3, 0),
        )

        ctk.CTkButton(
            header,
            text="›",
            width=38,
            height=32,
            corner_radius=8,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            command=self._next_month,
        ).grid(
            row=0,
            column=3,
            padx=(6, 0),
        )

        weekdays = [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun",
        ]

        week_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        week_frame.pack(
            fill="x",
            padx=12,
            pady=(0, 3),
        )

        for index, name in enumerate(weekdays):
            week_frame.grid_columnconfigure(
                index,
                weight=1,
            )

            ctk.CTkLabel(
                week_frame,
                text=name,
                font=FONT_SMALL_BOLD,
                text_color=(
                    TEXT_MUTED
                    if name in ("Sat", "Sun")
                    else TEXT_DARK
                ),
            ).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=1,
                pady=2,
            )

        days_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        days_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8),
        )

        month_weeks = calendar.monthcalendar(
            self.current.year,
            self.current.month,
        )

        for row_index, week in enumerate(month_weeks):
            days_frame.grid_rowconfigure(
                row_index,
                weight=1,
            )

            for col_index, day_number in enumerate(week):
                days_frame.grid_columnconfigure(
                    col_index,
                    weight=1,
                )

                if day_number == 0:
                    ctk.CTkLabel(
                        days_frame,
                        text="",
                    ).grid(
                        row=row_index,
                        column=col_index,
                        sticky="nsew",
                        padx=1,
                        pady=1,
                    )
                    continue

                day_date = date(
                    self.current.year,
                    self.current.month,
                    day_number,
                )

                selected_date = self._read_date()
                is_selected = day_date == selected_date

                ctk.CTkButton(
                    days_frame,
                    text=str(day_number),
                    width=36,
                    height=30,
                    corner_radius=7,
                    fg_color=(
                        TEXT_DARK
                        if is_selected
                        else PANEL_HOVER
                    ),
                    hover_color=PANEL_HOVER,
                    text_color=(
                        TEXT_LIGHT
                        if is_selected
                        else TEXT_DARK
                    ),
                    font=FONT_BODY,
                    command=lambda selected=day_date: self._select(
                        selected
                    ),
                ).grid(
                    row=row_index,
                    column=col_index,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                )

    def _set_month(self, value):
        month = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ].index(value) + 1

        self.current = date(
            self.current.year,
            month,
            1,
        )

        self._build()

    def _set_year(self):
        try:
            year = int(self.year_entry.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Year",
                "Enter a valid year from 2010 to 2026.",
                parent=self,
            )
            return

        if year < 2010 or year > 2026:
            messagebox.showwarning(
                "Invalid Year",
                "Enter a year from 2010 to 2026.",
                parent=self,
            )
            return

        self.current = date(
            year,
            self.current.month,
            1,
        )

        self._build()

    def _previous_month(self):
        year = self.current.year
        month = self.current.month - 1

        if month == 0:
            year -= 1
            month = 12

        self.current = date(
            year,
            month,
            1,
        )

        self._build()

    def _next_month(self):
        year = self.current.year
        month = self.current.month + 1

        if month == 13:
            year += 1
            month = 1

        self.current = date(
            year,
            month,
            1,
        )

        self._build()

    def _select(self, selected):
        self.entry.delete(0, "end")
        self.entry.insert(0, selected.isoformat())
        self.destroy()


class AssetsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)

        self.navigate = navigate
        self.accounts = []
        self.account_map = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(CONTENT_PAD_Y, 10),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Assets",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        actions = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        actions.grid(
            row=0,
            column=1,
            sticky="e",
        )

        buttons = [
            ("Add Asset", self._open_add_form),
            ("Edit Asset", self._open_edit_form),
            ("Sell Asset", self._open_sell_form),
            ("Refresh", self.refresh),
        ]

        for index, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                actions,
                text=text,
                width=140,
                height=44,
                corner_radius=BUTTON_RADIUS,
                fg_color=PANEL,
                hover_color=PANEL_HOVER,
                text_color=TEXT_DARK,
                font=FONT_BODY_BOLD,
                command=command,
            ).grid(
                row=0,
                column=index,
                padx=4,
                pady=2,
            )

    def _build_table(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )
        panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            panel,
            columns=[
                {
                    "label": "NAME",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "label": "CATEGORY",
                    "weight": 2,
                    "minsize": 130,
                },
                {
                    "label": "PURCHASE COST",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "label": "CURRENT VALUE",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "label": "ACQUIRED",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 110,
                    "anchor": "center",
                },
            ],
            empty_text="No assets yet",
            on_double_click=self._show_asset,
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18,
        )

    def refresh(self):
        try:
            self.accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.account_map = {
                account[1]: account[0]
                for account in self.accounts
            }

            assets = asset_service.get_assets()

        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load assets.\n\n{exc}",
                parent=self,
            )
            return

        self.table.clear()

        for asset in assets:
            (
                asset_id,
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes,
            ) = asset

            self.table.add_row(
                values=(
                    name,
                    category or "",
                    self._money(purchase_cost),
                    self._money(current_value),
                    acquired_date,
                    status,
                ),
                row_id=asset_id,
                cell_styles={
                    2: {
                        "font": FONT_BODY_BOLD,
                        "text_color": TEXT_DARK,
                    },
                    3: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if current_value >= purchase_cost
                            else DANGER
                        ),
                    },
                    5: {
                        "font": FONT_BODY_BOLD,
                        "text_color": self._status_color(status),
                    },
                },
            )

    def _open_add_form(self):
        AssetForm(
            self,
            mode="add",
            on_saved=self.refresh,
        )

    def _open_value_form(self):
        asset = self._selected_asset()

        if asset is None:
            return

        AssetValueForm(
            self,
            asset,
            on_saved=self.refresh,
        )

    def _open_edit_form(self):
        asset = self._selected_asset()

        if asset is None:
            return

        if asset[6] in ("DISPOSED", "SOLD"):
            messagebox.showwarning(
                "Unavailable",
                "Disposed or sold assets cannot be edited.",
                parent=self,
            )
            return

        AssetForm(
            self,
            mode="edit",
            asset=asset,
            on_saved=self.refresh,
        )

    def _open_sell_form(self):
        asset = self._selected_asset()

        if asset is None:
            return

        if asset[6] in ("DISPOSED", "SOLD"):
            messagebox.showwarning(
                "Unavailable",
                "This asset has already been disposed or sold.",
                parent=self,
            )
            return

        SellAssetForm(
            self,
            asset,
            self.account_map,
            on_saved=self.refresh,
        )

    def _selected_asset(self):
        asset_id = self.table.get_selected_row_id()

        if asset_id is None:
            messagebox.showinfo(
                "Select Asset",
                "Please select an asset first.",
                parent=self,
            )
            return None

        try:
            return asset_service.get_asset_by_id(
                asset_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Asset Error",
                f"Unable to load the asset.\n\n{exc}",
                parent=self,
            )
            return None

    def _dispose_asset(self):
        asset = self._selected_asset()

        if asset is None:
            return

        if asset[6] in ("DISPOSED", "SOLD"):
            messagebox.showwarning(
                "Unavailable",
                "This asset has already been disposed or sold.",
                parent=self,
            )
            return

        if not messagebox.askyesno(
            "Dispose Asset",
            f'Dispose "{asset[1]}"?\n\n'
            "This will mark the asset as DISPOSED.",
            parent=self,
        ):
            return

        try:
            asset_service.dispose_asset(asset[0])

        except Exception as exc:
            messagebox.showerror(
                "Dispose Error",
                f"Unable to dispose the asset.\n\n{exc}",
                parent=self,
            )
            return

        self.refresh()

    def _show_asset(self, asset_id):
        try:
            asset = asset_service.get_asset_by_id(asset_id)
            history = asset_service.get_asset_valuation_history(asset_id)

        except Exception as exc:
            messagebox.showerror(
                "Asset Error",
                f"Unable to load asset details.\n\n{exc}",
                parent=self,
            )
            return

        if not asset:
            return

        (
            _,
            name,
            category,
            purchase_cost,
            current_value,
            acquired_date,
            status,
            notes,
        ) = asset

        history_text = "\n".join(
            f"{row[2]}  -  {self._money(row[3])}"
            for row in history
        ) or "No valuation history"

        details = (
            f"Name: {name}\n"
            f"Category: {category or 'None'}\n"
            f"Purchase Cost: {self._money(purchase_cost)}\n"
            f"Current Value: {self._money(current_value)}\n"
            f"Acquired Date: {acquired_date}\n"
            f"Status: {status}\n"
            f"Notes: {notes or 'None'}\n\n"
            f"Valuation History:\n{history_text}"
        )

        messagebox.showinfo(
            "Asset Details",
            details,
            parent=self,
        )

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"

    @staticmethod
    def _status_color(status):
        if status == "ACTIVE":
            return SUCCESS

        if status in ("DISPOSED", "SOLD"):
            return DANGER

        return TEXT_DARK


class AssetForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        mode="add",
        asset=None,
        on_saved=None,
    ):
        super().__init__(master)

        self.master_page = master
        self.mode = mode
        self.asset = asset
        self.on_saved = on_saved

        self.title(
            "Add Asset"
            if mode == "add"
            else "Edit Asset"
        )
        self.geometry("580x950")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
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
            text=(
                "Add Asset"
                if self.mode == "add"
                else "Edit Asset"
            ),
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        ctk.CTkLabel(
            panel,
            text="Record the asset details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        self.name_entry = self._field(
            panel,
            "Name",
            self.asset[1] if self.asset else "",
        )

        self.category_entry = self._field(
            panel,
            "Category",
            self.asset[2] if self.asset else "",
        )

        self.purchase_entry = self._field(
            panel,
            "Purchase Cost",
            self._amount_value(
                self.asset[3]
            ) if self.asset else "",
        )

        self.current_entry = self._field(
            panel,
            "Current Value",
            self._amount_value(
                self.asset[4]
            ) if self.asset else "",
        )

        self.acquired_entry = self._date_field(
            panel,
            "Acquired Date",
            (
                self.asset[5]
                if self.asset
                else date.today().isoformat()
            ),
        )

        if self.mode == "add":
            self.transaction_date_entry = self._date_field(
                panel,
                "Purchase Transaction Date",
                date.today().isoformat(),
            )

            self.description_entry = self._field(
                panel,
                "Purchase Description",
                (
                    f"Purchase of {self.asset[1]}"
                    if self.asset
                    else ""
                ),
            )

            accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.account_map = {
                account[1]: account[0]
                for account in accounts
            }

            account_names = list(
                self.account_map.keys()
            )

            self.account_combo = self._combo(
                panel,
                "Payment Account",
                account_names or ["No accounts available"],
                (
                    account_names[0]
                    if account_names
                    else "No accounts available"
                ),
            )

        self.notes_entry = self._field(
            panel,
            "Notes",
            self.asset[7] if self.asset else "",
        )

        if self.mode == "edit":
            status_values = [
                "ACTIVE",
                "SOLD",
                "DISPOSED",
            ]

            self.status_combo = self._combo(
                panel,
                "Status",
                status_values,
                self.asset[6],
            )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        ctk.CTkButton(
            buttons,
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
            buttons,
            text=(
                "Save Asset"
                if self.mode == "add"
                else "Save Changes"
            ),
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _open_value_form(self):
        AssetValueForm(
            self.master_page,
            self.asset,
            on_saved=self.on_saved,
        )

    def _dispose_asset(self):
        if self.asset[6] in ("DISPOSED", "SOLD"):
            messagebox.showwarning(
                "Unavailable",
                "This asset has already been disposed or sold.",
                parent=self,
            )
            return

        if not messagebox.askyesno(
            "Dispose Asset",
            f'Dispose "{self.asset[1]}"?\n\n'
            "This will mark the asset as DISPOSED.",
            parent=self,
        ):
            return

        try:
            asset_service.dispose_asset(self.asset[0])

        except Exception as exc:
            messagebox.showerror(
                "Dispose Error",
                f"Unable to dispose the asset.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        entry.pack(fill="x")

        if value:
            entry.insert(
                0,
                str(value),
            )

        return entry

    def _date_field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        date_row = ctk.CTkFrame(
            wrapper,
            fg_color="transparent",
        )
        date_row.pack(fill="x")

        date_row.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            date_row,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )
        entry.grid(row=0, column=0, sticky="ew")

        if value:
            entry.insert(0, str(value))

        ctk.CTkButton(
            date_row,
            text="Calendar",
            width=96,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
            command=lambda: DatePicker(self, entry),
        ).grid(
            row=0,
            column=1,
            padx=(8, 0),
        )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected,
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        combo = ctk.CTkComboBox(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            button_color=PANEL_HOVER,
            button_hover_color=CONTENT,
            text_color=TEXT_DARK,
            dropdown_fg_color=INPUT_BG,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
            state="readonly",
            values=values,
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    def _amount_value(self, cents):
        return f"{cents / 100:.2f}"

    def _save(self):
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip() or None
        purchase_text = (
            self.purchase_entry.get()
            .strip()
            .replace(",", "")
        )
        current_text = (
            self.current_entry.get()
            .strip()
            .replace(",", "")
        )
        acquired_date = (
            self.acquired_entry.get().strip()
        )
        notes = (
            self.notes_entry.get().strip()
            or None
        )

        if (
            not name
            or not purchase_text
            or not current_text
            or not acquired_date
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self,
            )
            return

        try:
            date.fromisoformat(acquired_date)

            purchase_cost = int(
                round(
                    float(purchase_text) * 100
                )
            )

            current_value = int(
                round(
                    float(current_text) * 100
                )
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and valid numeric amounts.",
                parent=self,
            )
            return

        if purchase_cost < 0 or current_value < 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Amounts cannot be negative.",
                parent=self,
            )
            return

        try:
            if self.mode == "add":
                transaction_date = (
                    self.transaction_date_entry
                    .get()
                    .strip()
                )

                description = (
                    self.description_entry
                    .get()
                    .strip()
                )

                account_id = self.account_map.get(
                    self.account_combo.get().strip()
                )

                if (
                    not transaction_date
                    or not description
                    or account_id is None
                ):
                    messagebox.showwarning(
                        "Purchase Information",
                        "Enter a purchase date, description, and active payment account.",
                        parent=self,
                    )
                    return

                date.fromisoformat(
                    transaction_date
                )

                asset_service.buy_asset(
                    transaction_date,
                    description,
                    account_id,
                    name,
                    category,
                    purchase_cost,
                    acquired_date,
                    current_value,
                    notes,
                )

            else:
                status = (
                    self.status_combo
                    .get()
                    .strip()
                )

                asset_service.update_asset(
                    self.asset[0],
                    name,
                    category,
                    purchase_cost,
                    current_value,
                    acquired_date,
                    status,
                    notes,
                )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the asset.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class AssetValueForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        asset,
        on_saved=None,
    ):
        super().__init__(master)

        self.asset = asset
        self.on_saved = on_saved

        self.title("Update Asset Value")
        self.geometry("520x430")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
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
            text="Update Asset Value",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        ctk.CTkLabel(
            panel,
            text=(
                f"{self.asset[1]} · "
                f"Current: {self._money(self.asset[4])}"
            ),
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        self.value_entry = self._field(
            panel,
            "New Current Value",
            "",
        )

        self.date_entry = self._field(
            panel,
            "Valuation Date",
            date.today().isoformat(),
        )

        self.notes_entry = self._field(
            panel,
            "Notes",
            "",
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        ctk.CTkButton(
            buttons,
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
            buttons,
            text="Save Value",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        entry.pack(fill="x")

        if value:
            entry.insert(
                0,
                str(value),
            )

        return entry

    def _save(self):
        value_text = (
            self.value_entry
            .get()
            .strip()
            .replace(",", "")
        )

        valuation_date = (
            self.date_entry
            .get()
            .strip()
        )

        notes = (
            self.notes_entry
            .get()
            .strip()
            or None
        )

        if not value_text or not valuation_date:
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self,
            )
            return

        try:
            date.fromisoformat(
                valuation_date
            )

            current_value = int(
                round(
                    float(value_text) * 100
                )
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and a valid numeric amount.",
                parent=self,
            )
            return

        if current_value < 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Current value cannot be negative.",
                parent=self,
            )
            return

        try:
            asset_service.update_asset_value(
                self.asset[0],
                current_value,
                valuation_date,
                notes,
            )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to update the asset value.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"


class SellAssetForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        asset,
        account_map,
        on_saved=None,
    ):
        super().__init__(master)

        self.asset = asset
        self.account_map = account_map
        self.on_saved = on_saved

        self.title("Sell Asset")
        self.geometry("560x650")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
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
            text="Sell Asset",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        ctk.CTkLabel(
            panel,
            text=(
                f"{self.asset[1]} · "
                f"Current Value: {self._money(self.asset[4])}"
            ),
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        self.date_entry = self._date_field(
            panel,
            "Sale Date",
            date.today().isoformat(),
        )

        self.description_entry = self._field(
            panel,
            "Description",
            f"Sale of {self.asset[1]}",
        )

        self.price_entry = self._field(
            panel,
            "Sale Price",
            "",
        )

        account_names = list(
            self.account_map.keys()
        )

        self.account_combo = self._combo(
            panel,
            "Deposit Account",
            account_names or ["No accounts available"],
            (
                account_names[0]
                if account_names
                else "No accounts available"
            ),
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        ctk.CTkButton(
            buttons,
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
            buttons,
            text="Sell Asset",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=DANGER,
            hover_color="#913E3E",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        entry.pack(fill="x")

        if value:
            entry.insert(
                0,
                str(value),
            )

        return entry

    def _date_field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        date_row = ctk.CTkFrame(
            wrapper,
            fg_color="transparent",
        )
        date_row.pack(fill="x")

        date_row.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            date_row,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )
        entry.grid(row=0, column=0, sticky="ew")

        if value:
            entry.insert(0, str(value))

        ctk.CTkButton(
            date_row,
            text="Calendar",
            width=96,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
            command=lambda: DatePicker(self, entry),
        ).grid(
            row=0,
            column=1,
            padx=(8, 0),
        )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected,
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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

        combo = ctk.CTkComboBox(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            button_color=PANEL_HOVER,
            button_hover_color=CONTENT,
            text_color=TEXT_DARK,
            dropdown_fg_color=INPUT_BG,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
            state="readonly",
            values=values,
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    def _save(self):
        sale_date = (
            self.date_entry
            .get()
            .strip()
        )

        description = (
            self.description_entry
            .get()
            .strip()
        )

        price_text = (
            self.price_entry
            .get()
            .strip()
            .replace(",", "")
        )

        account_name = (
            self.account_combo
            .get()
            .strip()
        )

        if (
            not sale_date
            or not description
            or not price_text
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self,
            )
            return

        if not self.account_map:
            messagebox.showwarning(
                "Account Required",
                "An active account is required to record the sale proceeds.",
                parent=self,
            )
            return

        try:
            date.fromisoformat(sale_date)

            sale_price = int(
                round(
                    float(price_text) * 100
                )
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and a valid numeric amount.",
                parent=self,
            )
            return

        if sale_price <= 0:
            messagebox.showwarning(
                "Invalid Sale Price",
                "Sale price must be greater than zero.",
                parent=self,
            )
            return

        account_id = self.account_map.get(
            account_name
        )

        if account_id is None:
            messagebox.showwarning(
                "Account Required",
                "Please select an active account.",
                parent=self,
            )
            return

        try:
            asset_service.sell_asset(
                sale_date,
                description,
                account_id,
                self.asset[0],
                sale_price,
                sale_date,
            )

        except Exception as exc:
            messagebox.showerror(
                "Sale Error",
                f"Unable to sell the asset.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"
