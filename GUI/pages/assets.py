from datetime import date

import customtkinter as ctk

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
    show_info,
    show_operation_error,
    show_save_success,
    show_update_success,
)
from GUI.utils.formatters import (
    format_currency,
    format_date,
)
from GUI.utils.validation import (
    require_id,
    require_text,
    validate_currency,
    validate_date,
)
from services import account_service, asset_service, category_service


class AssetsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.selected_asset_id = None

        self.accounts = []
        self.categories = []

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build_header()
        self._build_table()
        self.refresh()

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
            text="Assets",
            font=FONT_PAGE_TITLE,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.action_buttons = Buttons(
            header,
            actions=[
                {
                    "label": "Add Asset",
                    "command": self._open_add_form,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Edit",
                    "command": self._open_edit_form,
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
            columns=3,
            height=40,
            padx=3,
            pady=0,
        )

        self.action_buttons.grid(
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
                    "key": "category",
                    "label": "CATEGORY",
                    "weight": 2,
                    "minsize": 130,
                },
                {
                    "key": "purchase_cost",
                    "label": "PURCHASE COST",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "key": "current_value",
                    "label": "CURRENT VALUE",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "key": "acquired_date",
                    "label": "ACQUIRED",
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
            ],
            empty_text="No assets yet",
            command=self._select_asset,
        )

        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def refresh(self):
        self.selected_asset_id = None

        try:
            self.accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.categories = list(
                category_service.get_categories()
            )

            assets = asset_service.get_assets()

        except Exception as exc:
            show_operation_error(
                self,
                "Load Assets",
                exc,
            )
            return

        rows = []

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

            rows.append(
                {
                    "id": asset_id,
                    "name": name,
                    "category": category or "",
                    "purchase_cost": format_currency(
                        purchase_cost
                    ),
                    "current_value": format_currency(
                        current_value
                    ),
                    "acquired_date": format_date(
                        acquired_date
                    ),
                    "status": status,
                }
            )

        self.table.set_rows(rows)

    def _select_asset(self, row):
        if isinstance(row, dict):
            self.selected_asset_id = row.get("id")
        else:
            self.selected_asset_id = None

    def _get_selected_asset(self):
        if self.selected_asset_id is None:
            show_info(
                self,
                "Select Asset",
                "Please select an asset first.",
            )
            return None

        try:
            asset_id = require_id(
                self.selected_asset_id,
                "Asset ID",
            )

            asset = asset_service.get_asset_by_id(
                asset_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Asset",
                exc,
            )
            return None

        if not asset:
            show_info(
                self,
                "Asset Not Found",
                "The selected asset could not be found.",
            )
            self.refresh()
            return None

        return asset

    def _open_add_form(self):
        AssetForm(
            self,
            mode="add",
            accounts=self.accounts,
            categories=self.categories,
            on_saved=self.refresh,
        )

    def _open_edit_form(self):
        asset = self._get_selected_asset()

        if asset is None:
            return

        if asset[6] in ("SOLD", "DISPOSED"):
            show_info(
                self,
                "Unavailable",
                "Sold or disposed assets cannot be edited.",
            )
            return

        AssetForm(
            self,
            mode="edit",
            asset=asset,
            accounts=self.accounts,
            categories=self.categories,
            on_saved=self.refresh,
        )


class AssetForm(FormWindow):
    def __init__(
        self,
        master,
        mode="add",
        asset=None,
        accounts=None,
        categories=None,
        on_saved=None,
    ):
        self.mode = mode
        self.asset = asset
        self.accounts = accounts or []
        self.categories = categories or []
        self.on_saved = on_saved

        title = (
            "Add Asset"
            if mode == "add"
            else "Edit Asset"
        )

        height = (
            820
            if mode == "add"
            else 750
        )

        super().__init__(
            master,
            title,
            width=580,
            height=height,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Record the asset details below."
        )

        self.name_entry = self.add_field(
            "Name",
            self.asset[1]
            if self.asset
            else "",
        )

        category_values = [
            category[1]
            for category in self.categories
        ]

        self.category_selector = self.add_selector(
            "Category",
            category_values,
            (
                self.asset[2]
                if self.asset
                else None
            ),
        )

        self.purchase_entry = self.add_currency_field(
            "Purchase Cost",
            self.asset[3]
            if self.asset
            else "",
        )

        self.current_entry = self.add_currency_field(
            "Current Value",
            self.asset[4]
            if self.asset
            else "",
        )

        self.acquired_entry = self.add_date_field(
            "Acquired Date",
            self.asset[5]
            if self.asset
            else date.today(),
        )

        self.notes_entry = self.add_field(
            "Notes",
            self.asset[7]
            if self.asset
            else "",
        )

        if self.mode == "add":
            account_values = [
                f"{account[0]} - {account[1]}"
                for account in self.accounts
            ]

            self.account_selector = self.add_selector(
                "Payment Account",
                account_values,
            )

        self.add_buttons(
            save_text=(
                "Save Asset"
                if self.mode == "add"
                else "Save Changes"
            ),
            save_command=self._save,
        )

    def _get_category(self):
        value = self.category_selector.get().strip()

        if not value or value == "No options available":
            raise ValueError(
                "Category is required."
            )

        return require_text(
            value,
            "Category",
        )

    def _get_account_id(self):
        value = self.account_selector.get().strip()

        if not value or value == "No options available":
            raise ValueError(
                "Payment account is required."
            )

        try:
            account_id = int(
                value.split(" - ", 1)[0]
            )
        except (
            ValueError,
            IndexError,
        ):
            raise ValueError(
                "Please select a valid payment account."
            )

        return require_id(
            account_id,
            "Payment Account",
        )

    def _validate_common_fields(self):
        name = require_text(
            self.name_entry.get(),
            "Name",
        )

        category = self._get_category()

        purchase_cost = validate_currency(
            self.purchase_entry.get(),
            "Purchase Cost",
            allow_zero=True,
        )

        current_value_text = (
            self.current_entry.get().strip()
        )

        if current_value_text:
            current_value = validate_currency(
                current_value_text,
                "Current Value",
                allow_zero=True,
            )
        else:
            current_value = purchase_cost

        acquired_date = validate_date(
            self.acquired_entry.get(),
            "Acquired Date",
        )

        notes = (
            self.notes_entry.get().strip()
            or None
        )

        return (
            name,
            category,
            purchase_cost,
            current_value,
            acquired_date,
            notes,
        )

    def _save(self):
        try:
            (
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                notes,
            ) = self._validate_common_fields()

            if self.mode == "add":
                self._create_asset(
                    name,
                    category,
                    purchase_cost,
                    current_value,
                    acquired_date,
                    notes,
                )
            else:
                self._update_asset(
                    name,
                    category,
                    purchase_cost,
                    current_value,
                    acquired_date,
                    notes,
                )

        except ValueError as exc:
            from GUI.utils.feedback import show_error

            show_error(
                self,
                "Validation Error",
                str(exc),
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Asset",
                exc,
            )

    def _create_asset(
        self,
        name,
        category,
        purchase_cost,
        current_value,
        acquired_date,
        notes,
    ):
        account_id = self._get_account_id()

        transaction_date = acquired_date.isoformat()

        description = (
            f"Purchase of {name}"
        )

        asset_service.buy_asset(
            transaction_date,
            description,
            account_id,
            name,
            category,
            purchase_cost,
            acquired_date.isoformat(),
            current_value,
            notes,
        )

        show_save_success(
            self,
            "Asset",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()

    def _update_asset(
        self,
        name,
        category,
        purchase_cost,
        current_value,
        acquired_date,
        notes,
    ):
        asset_service.update_asset(
            self.asset[0],
            name,
            category,
            purchase_cost,
            current_value,
            acquired_date.isoformat(),
            self.asset[6],
            notes,
        )

        show_update_success(
            self,
            "Asset",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()