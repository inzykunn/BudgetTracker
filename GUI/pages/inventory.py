import customtkinter as ctk

from services import inventory_service, account_service

from GUI.components.buttons import Buttons
from GUI.components.forms import FormWindow
from GUI.components.tables import Tables

from GUI.styles.colors import (
    CONTENT,
    TEXT_DARK,
)

from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    FONT_PAGE_TITLE,
)

from GUI.utils.feedback import (
    show_warning,
    show_operation_error,
    show_save_success,
    show_update_success,
    show_info,
)

from GUI.utils.validation import (
    require_text,
    validate_length,
)

from GUI.utils.formatters import format_currency


class InventoryPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.selected_item_id = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build()
        self.refresh()

    def _build(self):
        self._build_header()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(CONTENT_PAD_Y, 12),
        )

        header.grid_columnconfigure(
            0,
            weight=1,
        )

        ctk.CTkLabel(
            header,
            text="Inventory",
            font=FONT_PAGE_TITLE,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.header_buttons = Buttons(
            header,
            actions=[
                {
                    "label": "Add Inventory",
                    "command": self._open_add,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Sell",
                    "command": self._open_sell,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "Edit",
                    "command": self._open_edit,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "Refresh",
                    "command": self.refresh,
                    "style": "default",
                    "width": 90,
                    "height": 40,
                },
            ],
            columns=4,
            padx=3,
            pady=0,
        )

        self.header_buttons.grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _build_table(self):
        self.table = Tables(
            self,
            columns=[
                {
                    "key": "name",
                    "label": "NAME",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "key": "purchase_cost",
                    "label": "PURCHASE COST",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "key": "sale_price",
                    "label": "SALE PRICE",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "key": "acquired",
                    "label": "ACQUIRED",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "sold",
                    "label": "SOLD",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "status",
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 110,
                    "anchor": "center",
                },
                {
                    "key": "profit",
                    "label": "PROFIT",
                    "weight": 1,
                    "minsize": 130,
                    "anchor": "e",
                },
            ],
            empty_text="No inventory items yet",
            command=self._select_item,
        )

        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def refresh(self):
        try:
            items = inventory_service.get_inventory_items()

            rows = []

            for item in items:
                (
                    item_id,
                    name,
                    purchase_cost,
                    sale_price,
                    acquired_date,
                    sold_date,
                    status,
                    notes,
                ) = item

                profit = 0

                if sale_price is not None:
                    profit = sale_price - purchase_cost

                rows.append(
                    {
                        "id": item_id,
                        "name": name,
                        "purchase_cost": format_currency(
                            purchase_cost
                        ),
                        "sale_price": (
                            format_currency(sale_price)
                            if sale_price is not None
                            else "-"
                        ),
                        "acquired": str(
                            acquired_date or ""
                        )[:10],
                        "sold": (
                            str(sold_date)[:10]
                            if sold_date
                            else "-"
                        ),
                        "status": status,
                        "profit": (
                            format_currency(profit)
                            if sale_price is not None
                            else "-"
                        ),
                    }
                )

            self.table.set_rows(rows)

            if self.selected_item_id is not None:
                if not any(
                    row["id"] == self.selected_item_id
                    for row in rows
                ):
                    self.selected_item_id = None

        except Exception as exc:
            show_operation_error(
                self,
                "Load Inventory",
                exc,
            )

    def _select_item(self, item):
        if not item:
            return

        if isinstance(item, dict):
            self.selected_item_id = item.get("id")
        else:
            self.selected_item_id = item

    def _get_selected_item(self):
        if self.selected_item_id is None:
            show_warning(
                self,
                "Select Item",
                "Select an inventory item first.",
            )
            return None

        try:
            item = inventory_service.get_inventory_item_by_id(
                self.selected_item_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Inventory Item",
                exc,
            )
            return None

        if not item:
            show_warning(
                self,
                "Item Not Found",
                "The selected inventory item no longer exists.",
            )
            self.selected_item_id = None
            self.refresh()
            return None

        return item

    def _open_add(self):
        InventoryForm(
            self,
            on_saved=self.refresh,
        )

    def _open_edit(self):
        item = self._get_selected_item()

        if item is None:
            return

        if item[6] == "SOLD":
            show_warning(
                self,
                "Unavailable",
                "A sold inventory item cannot be edited.",
            )
            return

        InventoryForm(
            self,
            item=item,
            on_saved=self.refresh,
        )

    def _open_sell(self):
        item = self._get_selected_item()

        if item is None:
            return

        if item[6] == "SOLD":
            show_warning(
                self,
                "Unavailable",
                "This inventory item has already been sold.",
            )
            return

        SellInventoryForm(
            self,
            item,
            on_saved=self.refresh,
        )

class InventoryForm(FormWindow):
    def __init__(
        self,
        master,
        item=None,
        on_saved=None,
    ):
        self.item = item
        self.on_saved = on_saved

        super().__init__(
            master,
            "Edit Inventory Item"
            if item
            else "Add Inventory Item",
            width=560,
            height=820 if not item else 560,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Enter the inventory item details below."
        )

        self.name_entry = self.add_field(
            "Name",
            self.item[1]
            if self.item
            else "",
        )

        self.purchase_cost_entry = self.add_currency_field(
            "Purchase Cost",
            self.item[2]
            if self.item
            else "",
        )

        self.acquired_date_entry = self.add_date_field(
            "Acquired Date",
            self.item[4]
            if self.item
            else "",
        )

        if self.item is None:
            self.transaction_date_entry = self.add_date_field(
                "Purchase Transaction Date",
                "",
            )

            self.description_entry = self.add_field(
                "Purchase Description",
                "",
            )

            accounts = [
                f"{account[0]} - {account[1]}"
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.payment_account_selector = self.add_selector(
                "Payment Account",
                accounts,
            )

        self.notes_entry = self.add_field(
            "Notes",
            self.item[7]
            if self.item
            else "",
        )

        self.add_buttons(
            save_text=(
                "Save Changes"
                if self.item
                else "Save Inventory"
            ),
            save_command=self._save,
        )

    def _validate(self):
        try:
            name = validate_length(
                require_text(
                    self.name_entry.get(),
                    "Inventory name",
                ),
                "Inventory name",
                min_length=1,
                max_length=100,
            )

            purchase_cost = self.get_currency_value(
                self.purchase_cost_entry
            )

            if purchase_cost < 0:
                raise ValueError(
                    "Purchase cost cannot be negative."
                )

            acquired_date = self.get_date_value(
                self.acquired_date_entry
            )

            notes = self.notes_entry.get().strip()

            if self.item is None:
                transaction_date = self.get_date_value(
                    self.transaction_date_entry
                )

                description = validate_length(
                    require_text(
                        self.description_entry.get(),
                        "Purchase description",
                    ),
                    "Purchase description",
                    min_length=1,
                    max_length=200,
                )

                account = self.payment_account_selector.get()

                if not account:
                    raise ValueError(
                        "Payment account is required."
                    )

                account_id = int(
                    account.split(" - ", 1)[0]
                )

                return (
                    name,
                    purchase_cost,
                    acquired_date,
                    notes or None,
                    transaction_date,
                    description,
                    account_id,
                )

            return (
                name,
                purchase_cost,
                acquired_date,
                notes or None,
            )

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )
            return None

    def _save(self):
        values = self._validate()

        if values is None:
            return

        try:
            if self.item is None:
                (
                    name,
                    purchase_cost,
                    acquired_date,
                    notes,
                    transaction_date,
                    description,
                    account_id,
                ) = values

                inventory_service.buy_inventory(
                    transaction_date.isoformat(),
                    description,
                    account_id,
                    name,
                    purchase_cost,
                    acquired_date.isoformat(),
                    notes,
                )

                show_save_success(
                    self,
                    "Inventory item",
                )

            else:
                (
                    name,
                    purchase_cost,
                    acquired_date,
                    notes,
                ) = values

                inventory_service.update_inventory_item(
                    self.item[0],
                    name,
                    purchase_cost,
                    acquired_date.isoformat(),
                    self.item[3],
                    self.item[4],
                    self.item[6],
                    notes,
                )

                show_update_success(
                    self,
                    "Inventory item",
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Inventory",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class SellInventoryForm(FormWindow):
    def __init__(
        self,
        master,
        item,
        on_saved=None,
    ):
        self.item = item
        self.on_saved = on_saved

        super().__init__(
            master,
            "Sell Inventory Item",
            width=560,
            height=620,
        )

        self._build()

    def _build(self):
        self.add_description(
            f"Sell {self.item[1]} and record the sale proceeds."
        )

        self.sale_date_entry = self.add_date_field(
            "Sale Date",
            "",
        )

        self.description_entry = self.add_field(
            "Sale Description",
            f"Sale of {self.item[1]}",
        )

        self.sale_price_entry = self.add_currency_field(
            "Sale Price",
            "",
        )

        accounts = [
            f"{account[0]} - {account[1]}"
            for account in account_service.get_accounts()
            if account[3]
        ]

        self.deposit_account_selector = self.add_selector(
            "Deposit Account",
            accounts,
        )

        self.add_buttons(
            save_text="Sell Item",
            save_command=self._save,
        )

    def _validate(self):
        try:
            sale_date = self.get_date_value(
                self.sale_date_entry
            )

            description = validate_length(
                require_text(
                    self.description_entry.get(),
                    "Sale description",
                ),
                "Sale description",
                min_length=1,
                max_length=200,
            )

            sale_price = self.get_currency_value(
                self.sale_price_entry
            )

            if sale_price <= 0:
                raise ValueError(
                    "Sale price must be greater than zero."
                )

            account = self.deposit_account_selector.get()

            if not account:
                raise ValueError(
                    "Deposit account is required."
                )

            account_id = int(
                account.split(" - ", 1)[0]
            )

            return (
                sale_date,
                description,
                sale_price,
                account_id,
            )

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )
            return None

    def _save(self):
        values = self._validate()

        if values is None:
            return

        (
            sale_date,
            description,
            sale_price,
            account_id,
        ) = values

        try:
            transaction_id, profit = (
                inventory_service.sell_inventory(
                    sale_date.isoformat(),
                    description,
                    account_id,
                    self.item[0],
                    sale_price,
                    sale_date.isoformat(),
                )
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Sell Inventory",
                exc,
            )
            return

        show_info(
            self,
            "Item Sold",
            (
                f"{self.item[1]} was sold successfully.\n\n"
                f"Profit: {format_currency(profit)}"
            ),
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()