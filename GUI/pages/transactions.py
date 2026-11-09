import customtkinter as ctk
from tkinter import messagebox

from services import (
    transaction_service,
    account_service,
    category_service,
)

from GUI.components.quick_action_buttons import QuickActionButtons
from GUI.components.tables import Tables
from GUI.components.transaction_form import TransactionForm

from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    SUCCESS,
    DANGER,
)

from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    PANEL_RADIUS,
    FONT_SECTION,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL_BOLD,
)


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

        header.grid_columnconfigure(
            0,
            weight=1,
        )

        ctk.CTkLabel(
            header,
            text="Transactions",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        actions = QuickActionButtons(
            header,
            [
                (
                    "Add Income",
                    lambda: self._open_form("INCOME"),
                ),
                (
                    "Add Expense",
                    lambda: self._open_form("EXPENSE"),
                ),
                (
                    "Refresh",
                    self.refresh,
                ),
            ],
            columns=3,
        )

        actions.grid(
            row=0,
            column=1,
            sticky="e",
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

        panel.grid_columnconfigure(
            0,
            weight=1,
        )

        panel.grid_rowconfigure(
            0,
            weight=1,
        )

        self.table = Tables(
            panel,
            columns=[
                {
                    "label": "DATE",
                    "weight": 1,
                    "minsize": 105,
                },
                {
                    "label": "DESCRIPTION",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "label": "TYPE",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "label": "CATEGORY",
                    "weight": 2,
                    "minsize": 130,
                },
                {
                    "label": "ACCOUNT",
                    "weight": 2,
                    "minsize": 150,
                },
                {
                    "label": "AMOUNT",
                    "weight": 1,
                    "minsize": 120,
                    "anchor": "e",
                },
            ],
            empty_text="No transactions yet",
            on_double_click=self._show_transaction,
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18,
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

        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load transactions.\n\n{exc}",
                parent=self,
            )
            return

        self.table.clear()

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

            amount = self._display_amount(
                transaction_type,
                entries,
            )

            account = self._display_account(entries)

            category = self.category_names.get(
                category_id,
                "",
            )

            cell_styles = {
                2: {
                    "font": FONT_BODY_BOLD,
                    "text_color": self._type_color(
                        transaction_type
                    ),
                },
                5: {
                    "font": FONT_BODY_BOLD,
                    "text_color": self._amount_color(
                        transaction_type
                    ),
                },
            }

            self.table.add_row(
                values=(
                    transaction_date,
                    description,
                    transaction_type.replace(
                        "_",
                        " ",
                    ),
                    category,
                    account,
                    amount,
                ),
                row_id=transaction_id,
                cell_styles=cell_styles,
            )

    @staticmethod
    def _type_color(transaction_type):
        if transaction_type == "INCOME":
            return SUCCESS

        if transaction_type in {
            "EXPENSE",
            "RECEIVABLE",
            "LIABILITY_PAYMENT",
        }:
            return DANGER

        return TEXT_DARK

    @staticmethod
    def _amount_color(transaction_type):
        if transaction_type == "INCOME":
            return SUCCESS

        if transaction_type in {
            "EXPENSE",
            "RECEIVABLE",
            "LIABILITY_PAYMENT",
        }:
            return DANGER

        return TEXT_DARK

    @staticmethod
    def _display_amount(
        transaction_type,
        entries,
    ):
        if not entries:
            return "₱0.00"

        if transaction_type == "TRANSFER":
            amount = max(
                abs(entry[2])
                for entry in entries
            )

            return f"₱{amount / 100:,.2f}"

        amount = abs(entries[0][2])

        if transaction_type in {
            "EXPENSE",
            "RECEIVABLE",
            "LIABILITY_PAYMENT",
        }:
            return f"- ₱{amount / 100:,.2f}"

        return f"+ ₱{amount / 100:,.2f}"

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

    def _show_transaction(self, transaction_id):
        try:
            transaction, entries = transaction_service.get_transaction_by_id(
                transaction_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Transaction Error",
                f"Unable to load the transaction.\n\n{exc}",
                parent=self,
            )
            return

        if not transaction:
            return

        transaction_type = transaction[3]

        details = (
            f"Date: {transaction[1]}\n"
            f"Description: {transaction[2]}\n"
            f"Type: {transaction_type.replace('_', ' ')}\n"
            f"Category: {self.category_names.get(transaction[4], 'None')}\n"
            f"Account: {self._display_account(entries)}\n"
            f"Amount: {self._display_amount(transaction_type, entries)}"
        )

        messagebox.showinfo(
            "Transaction Details",
            details,
            parent=self,
        )