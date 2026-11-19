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
    FONT_BODY,
    FONT_BODY_BOLD,
)
from GUI.utils.feedback import (
    show_warning,
    show_operation_error,
    show_save_success,
)

from services import (
    transaction_service,
    account_service,
    category_service,
)

TRANSACTION_TYPES = [
    "INCOME",
    "EXPENSE",
]


class TransactionsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate
        self.account_names = {}
        self.category_names = {}

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
            text="Transactions",
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
                    "label": "Add Income",
                    "command": lambda: self._open_form("INCOME"),
                    "style": "success",
                    "width": 120,
                    "height": 40,
                },
                {
                    "label": "Add Expense",
                    "command": lambda: self._open_form("EXPENSE"),
                    "style": "danger",
                    "width": 125,
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
                    "key": "date",
                    "label": "DATE",
                    "weight": 1,
                    "minsize": 105,
                },
                {
                    "key": "description",
                    "label": "DESCRIPTION",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "key": "type",
                    "label": "TYPE",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "category",
                    "label": "CATEGORY",
                    "weight": 2,
                    "minsize": 130,
                },
                {
                    "key": "account",
                    "label": "ACCOUNT",
                    "weight": 2,
                    "minsize": 150,
                },
                {
                    "key": "amount",
                    "label": "AMOUNT",
                    "weight": 1,
                    "minsize": 120,
                    "anchor": "e",
                },
            ],
            empty_text="No transactions yet",
            command=self._show_transaction,
        )

        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def _open_form(self, transaction_type):
        TransactionForm(
            self,
            transaction_type=transaction_type,
            on_saved=self.refresh,
        )

    def refresh(self):
        try:
            accounts = account_service.get_accounts()
            categories = category_service.get_categories()
            transactions = transaction_service.get_transactions()

            self.account_names = {
                row[0]: row[1]
                for row in accounts
            }

            self.category_names = {
                row[0]: row[1]
                for row in categories
            }

            rows = []

            for transaction in transactions:
                (
                    transaction_id,
                    transaction_date,
                    description,
                    transaction_type,
                    category_id,
                    _,
                ) = transaction

                try:
                    _, entries = transaction_service.get_transaction_by_id(
                        transaction_id
                    )
                except Exception:
                    entries = []

                rows.append(
                    {
                        "id": transaction_id,
                        "date": transaction_date,
                        "description": description,
                        "type": transaction_type.replace(
                            "_",
                            " ",
                        ),
                        "category": self.category_names.get(
                            category_id,
                            "",
                        ),
                        "account": self._display_account(
                            entries
                        ),
                        "amount": self._display_amount(
                            transaction_type,
                            entries,
                        ),
                    }
                )

            self.table.set_rows(rows)

        except Exception as exc:
            show_operation_error(
                self,
                "Load Transactions",
                exc,
            )

    def _display_amount(
        self,
        transaction_type,
        entries,
    ):
        if not entries:
            return "₱0.00"

        amount = abs(entries[0][2])

        if transaction_type == "INCOME":
            return f"+ ₱{amount / 100:,.2f}"

        if transaction_type == "EXPENSE":
            return f"- ₱{amount / 100:,.2f}"

        return f"₱{amount / 100:,.2f}"

    def _display_account(self, entries):
        if not entries:
            return ""

        names = [
            self.account_names.get(
                entry[1],
                f"Account {entry[1]}",
            )
            for entry in entries
        ]

        if len(names) > 1:
            return " → ".join(names)

        return names[0]

    def _show_transaction(self, row_data):
        transaction_id = row_data.get("id")

        if transaction_id is None:
            return

        try:
            transaction, entries = (
                transaction_service.get_transaction_by_id(
                    transaction_id
                )
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Transaction",
                exc,
            )
            return

        if not transaction:
            show_warning(
                self,
                "Transaction Not Found",
                "The selected transaction no longer exists.",
            )

            self.refresh()
            return

        TransactionDetailsForm(
            self,
            transaction,
            entries,
            self.account_names,
            self.category_names,
        )


class TransactionForm(FormWindow):
    def __init__(
        self,
        master,
        transaction_type,
        on_saved=None,
    ):
        self.transaction_type = transaction_type
        self.on_saved = on_saved
        self.accounts = []
        self.categories = []

        super().__init__(
            master,
            (
                "Add Income"
                if transaction_type == "INCOME"
                else "Add Expense"
            ),
            width=560,
            height=650,
        )

        self._load_data()
        self._build()

    def _load_data(self):
        try:
            self.accounts = [
                row
                for row in account_service.get_accounts()
                if row[3]
            ]

            self.categories = [
                row
                for row in category_service.get_categories()
                if row[2] == self.transaction_type
            ]

        except Exception as exc:
            show_operation_error(
                self,
                "Load Transaction Form",
                exc,
            )

    def _build(self):
        self.add_description(
            "Enter the transaction details below."
        )

        self.date_entry = self.add_date_field(
            "Date",
            value=date.today().strftime("%m/%d/%Y"),
            placeholder_text="MM/DD/YYYY",
        )

        self.description_entry = self.add_field(
            "Description",
            placeholder_text="Enter description",
        )

        self.account_selector = self.add_selector(
            "Account",
            [
                f"{row[0]} - {row[1]}"
                for row in self.accounts
            ],
        )

        self.category_selector = self.add_selector(
            "Category",
            [
                f"{row[0]} - {row[1]}"
                for row in self.categories
            ],
        )

        self.amount_entry = self.add_currency_field(
            "Amount",
            placeholder_text="0.00",
        )

        self.add_buttons(
            save_text=(
                "Save Income"
                if self.transaction_type == "INCOME"
                else "Save Expense"
            ),
            save_command=self._save,
        )

    def _validate(self):
        try:
            transaction_date = self.get_date_value(
                self.date_entry
            )

            description = self.description_entry.get().strip()

            if len(description) > 255:
                raise ValueError(
                    "Transaction description must not exceed 255 characters."
                )

            account_id = self._get_selected_id(
                self.account_selector
            )

            if account_id is None:
                raise ValueError(
                    "Please select an account."
                )

            category_id = self._get_selected_id(
                self.category_selector
            )

            if category_id is None:
                raise ValueError(
                    "Please select a category."
                )

            amount = self.get_currency_value(
                self.amount_entry
            )

            if amount <= 0:
                raise ValueError(
                    "Transaction amount must be greater than zero."
                )

            return (
                transaction_date,
                description,
                account_id,
                category_id,
                amount,
            )

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )

            return None

    @staticmethod
    def _get_selected_id(selector):
        value = selector.get()

        if not value:
            return None

        if value == "No options available":
            return None

        try:
            return int(
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

    def _save(self):
        values = self._validate()

        if values is None:
            return

        (
            transaction_date,
            description,
            account_id,
            category_id,
            amount,
        ) = values

        try:
            transaction_date = transaction_date.isoformat()

            if self.transaction_type == "EXPENSE":
                amount = -amount

            transaction_service.create_transaction(
                transaction_date,
                description,
                self.transaction_type,
                category_id,
                [
                    (
                        account_id,
                        amount,
                    )
                ],
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Transaction",
                exc,
            )
            return

        show_save_success(
            self,
            (
                "Income"
                if self.transaction_type == "INCOME"
                else "Expense"
            ),
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()


class TransactionDetailsForm(FormWindow):
    def __init__(
        self,
        master,
        transaction,
        entries,
        account_names,
        category_names,
    ):
        self.transaction = transaction
        self.entries = entries
        self.account_names = account_names
        self.category_names = category_names

        super().__init__(
            master,
            "Transaction Details",
            width=560,
            height=560,
        )

        self._build()

    def _build(self):
        transaction_type = self.transaction[3]

        self.add_description(
            "Transaction information."
        )

        self._add_detail(
            "Date",
            self.transaction[1],
        )

        self._add_detail(
            "Description",
            self.transaction[2],
        )

        self._add_detail(
            "Type",
            transaction_type.replace(
                "_",
                " ",
            ),
        )

        self._add_detail(
            "Category",
            self.category_names.get(
                self.transaction[4],
                "None",
            ),
        )

        self._add_detail(
            "Account",
            self._display_account(),
        )

        self._add_detail(
            "Amount",
            self._display_amount(
                transaction_type
            ),
        )

        self.add_buttons(
            save_text="Close",
            save_command=self.destroy,
        )

    def _add_detail(self, label, value):
        wrapper = ctk.CTkFrame(
            self.body,
            fg_color="transparent",
            corner_radius=0,
        )

        wrapper.pack(
            fill="x",
            pady=(0, 12),
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_BODY_BOLD,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
        )

        ctk.CTkLabel(
            wrapper,
            text=str(value),
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            pady=(2, 0),
        )

    def _display_account(self):
        if not self.entries:
            return ""

        names = [
            self.account_names.get(
                entry[1],
                f"Account {entry[1]}",
            )
            for entry in self.entries
        ]

        if len(names) > 1:
            return " → ".join(names)

        return names[0]

    def _display_amount(self, transaction_type):
        if not self.entries:
            return "₱0.00"

        amount = abs(
            self.entries[0][2]
        )

        if transaction_type == "INCOME":
            return f"+ ₱{amount / 100:,.2f}"

        if transaction_type == "EXPENSE":
            return f"- ₱{amount / 100:,.2f}"

        return f"₱{amount / 100:,.2f}"