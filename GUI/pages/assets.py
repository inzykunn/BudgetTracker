from datetime import date
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
)


class AssetsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)

        self.navigate = navigate
        self.accounts = []
        self.account_map = {}
        self.selected_asset_id = None

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
            ("Update Value", self._open_value_form),
            ("Sell Asset", self._open_sell_form),
            ("Edit Asset", self._open_edit_form),
            ("Dispose", self._dispose_asset),
            ("Refresh", self.refresh),
        ]

        for index, (text, command) in enumerate(buttons):
            row = index // 3
            column = index % 3

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
                row=row,
                column=column,
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
        if self.selected_asset_id is None:
            messagebox.showinfo(
                "Select Asset",
                "Double-click an asset row first, then use the action buttons to manage it.",
                parent=self,
            )
            return None

        try:
            return asset_service.get_asset_by_id(
                self.selected_asset_id
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

        self.selected_asset_id = None
        self.refresh()

    def _show_asset(self, asset_id):
        self.selected_asset_id = asset_id

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
        self.geometry("580x800")
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

        self.acquired_entry = self._field(
            panel,
            "Acquired Date",
            (
                self.asset[5]
                if self.asset
                else date.today().isoformat()
            ),
        )

        if self.mode == "add":
            self.transaction_date_entry = self._field(
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
        self.geometry("560x500")
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

        self.date_entry = self._field(
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