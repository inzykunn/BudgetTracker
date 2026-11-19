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
    show_warning,
    show_operation_error,
    show_save_success,
)

from GUI.utils.validation import (
    require_text,
    validate_length,
)

from services import (
    account_service,
    finance_service,
    transaction_service,
)

class TransferPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.accounts = []
        self.account_names = {}

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
            text="Transfer",
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
                    "label": "New Transfer",
                    "command": self._open_transfer_form,
                    "style": "primary",
                    "width": 140,
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
            columns=2,
            height=40,
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
                    "weight": 2,
                    "minsize": 120,
                },
                {
                    "key": "description",
                    "label": "DESCRIPTION",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "key": "source",
                    "label": "FROM ACCOUNT",
                    "weight": 2,
                    "minsize": 140,
                },
                {
                    "key": "destination",
                    "label": "TO ACCOUNT",
                    "weight": 2,
                    "minsize": 140,
                },
                {
                    "key": "amount",
                    "label": "AMOUNT",
                    "weight": 2,
                    "minsize": 120,
                    "anchor": "e",
                },
            ],
            empty_text="No transfers recorded yet.",
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
            accounts = account_service.get_accounts()

            self.accounts = [
                account
                for account in accounts
                if account[3]
            ]

            self.account_names = {
                account[0]: account[1]
                for account in self.accounts
            }

            transactions = transaction_service.get_transactions()

            rows = []

            for transaction in transactions:
                transaction_id = transaction[0]
                transaction_date = transaction[1]
                description = transaction[2]
                transaction_type = transaction[3]

                if transaction_type != "TRANSFER":
                    continue

                _, entries = transaction_service.get_transaction_by_id(
                    transaction_id
                )

                if len(entries) != 2:
                    continue

                source_entry = next(
                    (
                        entry
                        for entry in entries
                        if entry[2] < 0
                    ),
                    None,
                )

                destination_entry = next(
                    (
                        entry
                        for entry in entries
                        if entry[2] > 0
                    ),
                    None,
                )

                if not source_entry or not destination_entry:
                    continue

                source_id = source_entry[1]
                destination_id = destination_entry[1]

                amount = abs(source_entry[2])

                rows.append(
                    {
                        "id": transaction_id,
                        "date": transaction_date,
                        "description": description,
                        "source": self.account_names.get(
                            source_id,
                            f"Account {source_id}",
                        ),
                        "destination": self.account_names.get(
                            destination_id,
                            f"Account {destination_id}",
                        ),
                        "amount": f"₱{amount / 100:,.2f}",
                    }
                )

            self.table.set_rows(rows)

        except Exception as exc:
            show_operation_error(
                self,
                "Load Transfers",
                exc,
            )

    def _open_transfer_form(self):
        if len(self.accounts) < 2:
            show_warning(
                self,
                "Not Enough Accounts",
                "You need at least two active accounts to make a transfer.",
            )
            return

        TransferForm(
            self,
            accounts=self.accounts,
            on_saved=self.refresh,
        )


class TransferForm(FormWindow):
    def __init__(
        self,
        master,
        accounts,
        on_saved=None,
    ):
        super().__init__(
            master,
            "Transfer Money",
            width=560,
            height=720,
        )

        self.accounts = accounts
        self.on_saved = on_saved

        self.account_options = [
            f"{account[0]} - {account[1]}"
            for account in accounts
        ]

        self._build()

    def _build(self):
        self.add_description(
            "Move money from one account to another."
        )

        self.date_entry = self.add_date_field(
            "Date",
            value=date.today(),
            placeholder_text="MM/DD/YYYY",
        )

        self.description_entry = self.add_field(
            "Description",
            placeholder_text="Enter description",
        )

        self.source_selector = self.add_selector(
            "Source Account",
            self.account_options,
            value=self.account_options[0],
        )

        self.destination_selector = self.add_selector(
            "Destination Account",
            self.account_options,
            value=self.account_options[1],
        )

        self.amount_entry = self.add_currency_field(
            "Amount",
            placeholder_text="0.00",
        )

        self.add_buttons(
            save_text="Transfer Money",
            save_command=self._save,
        )

    def _get_account_id(self, selector):
        selected_value = selector.get()

        if not selected_value:
            return None

        try:
            account_id = int(
                selected_value.split(
                    " - ",
                    1,
                )[0]
            )

            if any(
                account[0] == account_id
                for account in self.accounts
            ):
                return account_id

        except (
            ValueError,
            IndexError,
        ):
            pass

        for account in self.accounts:
            if account[1] == selected_value:
                return account[0]

        return None

    def _validate(self):
        try:
            transfer_date = self.get_date_value(
                self.date_entry
            )

            description = validate_length(
                require_text(
                    self.description_entry.get(),
                    "Description",
                ),
                "Description",
                min_length=1,
                max_length=255,
            )

            source_account_id = self._get_account_id(
                self.source_selector
            )

            destination_account_id = self._get_account_id(
                self.destination_selector
            )

            if source_account_id is None:
                raise ValueError(
                    "Please select a source account."
                )

            if destination_account_id is None:
                raise ValueError(
                    "Please select a destination account."
                )

            if source_account_id == destination_account_id:
                raise ValueError(
                    "Source and destination accounts must be different."
                )

            amount = self.get_currency_value(
                self.amount_entry
            )

            if amount <= 0:
                raise ValueError(
                    "Transfer amount must be greater than zero."
                )

            return (
                transfer_date,
                description,
                source_account_id,
                destination_account_id,
                amount,
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
            transfer_date,
            description,
            source_account_id,
            destination_account_id,
            amount,
        ) = values

        try:
            finance_service.record_transfer(
                transfer_date.isoformat(),
                description,
                source_account_id,
                destination_account_id,
                amount,
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Record Transfer",
                exc,
            )
            return

        show_save_success(
            self,
            "Transfer",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()