from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from services import inventory_service, account_service
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


class InventoryPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT
        )

        self.navigate = navigate
        self.selected_item_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(CONTENT_PAD_Y, 10)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Inventory",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        actions = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        actions.grid(
            row=0,
            column=1,
            sticky="e"
        )

        buttons = [
            ("Add Item", self._open_add_form),
            ("Sell Item", self._open_sell_form),
            ("Edit Item", self._open_edit_form),
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
                command=command
            ).grid(
                row=0,
                column=index,
                padx=4,
                pady=2
            )

    def _build_table(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y)
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            panel,
            columns=[
                {
                    "label": "NAME",
                    "weight": 3,
                    "minsize": 180
                },
                {
                    "label": "PURCHASE COST",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e"
                },
                {
                    "label": "SALE PRICE",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e"
                },
                {
                    "label": "ACQUIRED",
                    "weight": 1,
                    "minsize": 110
                },
                {
                    "label": "SOLD",
                    "weight": 1,
                    "minsize": 110
                },
                {
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 110,
                    "anchor": "center"
                },
                {
                    "label": "PROFIT",
                    "weight": 1,
                    "minsize": 130,
                    "anchor": "e"
                },
            ],
            empty_text="No inventory items yet",
            on_double_click=self._show_item
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18
        )

    def refresh(self):
        try:
            items = inventory_service.get_inventory_items()

        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load inventory.\n\n{exc}",
                parent=self
            )
            return

        self.table.clear()

        for item in items:
            (
                item_id,
                name,
                purchase_cost,
                sale_price,
                acquired_date,
                sold_date,
                status,
                notes
            ) = item

            profit = 0

            if sale_price is not None:
                profit = sale_price - purchase_cost

            self.table.add_row(
                values=(
                    name,
                    self._money(purchase_cost),
                    (
                        self._money(sale_price)
                        if sale_price is not None
                        else "-"
                    ),
                    acquired_date,
                    sold_date or "-",
                    status,
                    (
                        self._money(profit)
                        if sale_price is not None
                        else "-"
                    ),
                ),
                row_id=item_id,
                cell_styles={
                    1: {
                        "font": FONT_BODY_BOLD,
                        "text_color": TEXT_DARK
                    },
                    2: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if sale_price is not None
                            else TEXT_DARK
                        )
                    },
                    5: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if status == "AVAILABLE"
                            else DANGER
                        )
                    },
                    6: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if profit > 0
                            else DANGER
                            if profit < 0
                            else TEXT_DARK
                        )
                    },
                }
            )

    def _selected_item(self):
        if self.selected_item_id is None:
            messagebox.showinfo(
                "Select Item",
                "Double-click an inventory item first, then use the action buttons to manage it.",
                parent=self
            )
            return None

        try:
            return inventory_service.get_inventory_item_by_id(
                self.selected_item_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Inventory Error",
                f"Unable to load the inventory item.\n\n{exc}",
                parent=self
            )
            return None

    def _open_add_form(self):
        InventoryForm(
            self,
            mode="add",
            on_saved=self.refresh
        )

    def _open_edit_form(self):
        item = self._selected_item()

        if item is None:
            return

        if item[6] == "SOLD":
            messagebox.showwarning(
                "Unavailable",
                "A sold inventory item cannot be edited.",
                parent=self
            )
            return

        InventoryForm(
            self,
            mode="edit",
            item=item,
            on_saved=self.refresh
        )

    def _open_sell_form(self):
        item = self._selected_item()

        if item is None:
            return

        if item[6] == "SOLD":
            messagebox.showwarning(
                "Unavailable",
                "This inventory item has already been sold.",
                parent=self
            )
            return

        SellInventoryForm(
            self,
            item,
            on_saved=self.refresh
        )

    def _show_item(self, item_id):
        self.selected_item_id = item_id

        try:
            item = inventory_service.get_inventory_item_by_id(
                item_id
            )

            profit = inventory_service.calculate_inventory_profit(
                item_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Inventory Error",
                f"Unable to load inventory details.\n\n{exc}",
                parent=self
            )
            return

        if not item:
            return

        (
            _,
            name,
            purchase_cost,
            sale_price,
            acquired_date,
            sold_date,
            status,
            notes
        ) = item

        details = (
            f"Name: {name}\n"
            f"Purchase Cost: {self._money(purchase_cost)}\n"
            f"Sale Price: "
            f"{self._money(sale_price) if sale_price is not None else 'Not sold'}\n"
            f"Acquired Date: {acquired_date}\n"
            f"Sold Date: {sold_date or 'Not sold'}\n"
            f"Status: {status}\n"
            f"Profit: "
            f"{self._money(profit) if sale_price is not None else 'Not sold'}\n"
            f"Notes: {notes or 'None'}"
        )

        messagebox.showinfo(
            "Inventory Item",
            details,
            parent=self
        )

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"


class InventoryForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        mode="add",
        item=None,
        on_saved=None
    ):
        super().__init__(master)

        self.master_page = master
        self.mode = mode
        self.item = item
        self.on_saved = on_saved

        self.title(
            "Add Inventory Item"
            if mode == "add"
            else "Edit Inventory Item"
        )

        self.geometry("560x700")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)

        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            panel,
            text=(
                "Add Inventory Item"
                if self.mode == "add"
                else "Edit Inventory Item"
            ),
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            panel,
            text="Record the inventory item details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18)
        )

        self.name_entry = self._field(
            panel,
            "Name",
            self.item[1] if self.item else ""
        )

        self.purchase_entry = self._field(
            panel,
            "Purchase Cost",
            self._amount(self.item[2])
            if self.item
            else ""
        )

        self.acquired_entry = self._field(
            panel,
            "Acquired Date",
            self.item[4]
            if self.item
            else date.today().isoformat()
        )

        if self.mode == "add":
            self.transaction_date_entry = self._field(
                panel,
                "Purchase Transaction Date",
                date.today().isoformat()
            )

            self.description_entry = self._field(
                panel,
                "Purchase Description",
                ""
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
                )
            )

        self.notes_entry = self._field(
            panel,
            "Notes",
            self.item[7] if self.item else ""
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24)
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1
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
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        ctk.CTkButton(
            buttons,
            text="Save Item",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )

        entry.pack(fill="x")

        if value:
            entry.insert(
                0,
                str(value)
            )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
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
            values=values
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    @staticmethod
    def _amount(value):
        return f"{value / 100:.2f}"

    def _save(self):
        name = self.name_entry.get().strip()
        purchase_text = (
            self.purchase_entry
            .get()
            .strip()
            .replace(",", "")
        )

        acquired_date = (
            self.acquired_entry
            .get()
            .strip()
        )

        notes = (
            self.notes_entry
            .get()
            .strip()
            or None
        )

        if not name or not purchase_text or not acquired_date:
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self
            )
            return

        try:
            date.fromisoformat(acquired_date)

            purchase_cost = int(
                round(
                    float(purchase_text) * 100
                )
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and a valid numeric purchase cost.",
                parent=self
            )
            return

        if purchase_cost < 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Purchase cost cannot be negative.",
                parent=self
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

                account_name = (
                    self.account_combo
                    .get()
                    .strip()
                )

                if not transaction_date or not description:
                    messagebox.showwarning(
                        "Missing Information",
                        "Please complete the purchase transaction fields.",
                        parent=self
                    )
                    return

                date.fromisoformat(
                    transaction_date
                )

                account_id = self.account_map.get(
                    account_name
                )

                if account_id is None:
                    messagebox.showwarning(
                        "Account Required",
                        "Please select an active payment account.",
                        parent=self
                    )
                    return

                inventory_service.buy_inventory(
                    transaction_date,
                    description,
                    account_id,
                    name,
                    purchase_cost,
                    acquired_date,
                    notes
                )

            else:
                inventory_service.update_inventory_item(
                    self.item[0],
                    name,
                    purchase_cost,
                    acquired_date,
                    self.item[3],
                    self.item[4],
                    self.item[6],
                    notes
                )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the inventory item.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class SellInventoryForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        item,
        on_saved=None
    ):
        super().__init__(master)

        self.item = item
        self.on_saved = on_saved

        self.title("Sell Inventory Item")
        self.geometry("560x560")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)

        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            panel,
            text="Sell Inventory Item",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            panel,
            text=(
                f"{self.item[1]} · "
                f"Cost: {self._money(self.item[2])}"
            ),
            font=FONT_BODY,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18)
        )

        self.sale_date_entry = self._field(
            panel,
            "Sale Date",
            date.today().isoformat()
        )

        self.description_entry = self._field(
            panel,
            "Sale Description",
            f"Sale of {self.item[1]}"
        )

        self.price_entry = self._field(
            panel,
            "Sale Price",
            ""
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
            "Deposit Account",
            account_names or ["No accounts available"],
            (
                account_names[0]
                if account_names
                else "No accounts available"
            )
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24)
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1
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
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        ctk.CTkButton(
            buttons,
            text="Sell Item",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=SUCCESS,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )

        entry.pack(fill="x")

        if value:
            entry.insert(
                0,
                str(value)
            )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
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
            values=values
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"

    def _save(self):
        sale_date = (
            self.sale_date_entry
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

        if not sale_date or not description or not price_text:
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self
            )
            return

        if not self.account_map:
            messagebox.showwarning(
                "Account Required",
                "An active account is required to record the sale proceeds.",
                parent=self
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
                "Use YYYY-MM-DD for the date and a valid numeric sale price.",
                parent=self
            )
            return

        if sale_price <= 0:
            messagebox.showwarning(
                "Invalid Sale Price",
                "Sale price must be greater than zero.",
                parent=self
            )
            return

        account_id = self.account_map.get(
            account_name
        )

        if account_id is None:
            messagebox.showwarning(
                "Account Required",
                "Please select an active account.",
                parent=self
            )
            return

        try:
            transaction_id, profit = (
                inventory_service.sell_inventory(
                    sale_date,
                    description,
                    account_id,
                    self.item[0],
                    sale_price,
                    sale_date
                )
            )

        except Exception as exc:
            messagebox.showerror(
                "Sale Error",
                f"Unable to sell the inventory item.\n\n{exc}",
                parent=self
            )
            return

        messagebox.showinfo(
            "Item Sold",
            (
                f"{self.item[1]} was sold successfully.\n\n"
                f"Profit: {self._money(profit)}"
            ),
            parent=self
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()