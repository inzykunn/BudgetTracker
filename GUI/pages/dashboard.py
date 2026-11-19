import customtkinter as ctk
from datetime import date

from services import (
    account_service,
    asset_service,
    financial_review_service,
    inventory_service,
    transaction_service,
)

from GUI.components.buttons import Buttons
from GUI.components.cards import Cards
from GUI.components.tables import Tables
from GUI.pages.transactions import TransactionForm

from GUI.styles.colors import (
    CONTENT,
    TEXT_DARK,
)

from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    FONT_PAGE_TITLE,
    FONT_SECTION,
)

from GUI.utils.feedback import show_operation_error
from GUI.utils.formatters import format_currency, format_date


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, navigate):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build()
        self.refresh()

    def _build(self):
        self._build_header()
        self._build_summary()
        self._build_secondary_summary()
        self._build_detail_sections()
        self._build_quick_actions()

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
            pady=(CONTENT_PAD_Y, 10),
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=FONT_PAGE_TITLE,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        Buttons(
            header,
            actions=[
                {
                    "label": "Refresh",
                    "command": self.refresh,
                    "width": 90,
                    "height": 40,
                },
            ],
            columns=1,
            height=40,
            padx=3,
            pady=0,
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _build_summary(self):
        self.summary = Cards(
            self,
            [
                {
                    "key": "income",
                    "title": "TOTAL INCOME",
                    "value": "₱0.00",
                },
                {
                    "key": "expenses",
                    "title": "TOTAL EXPENSES",
                    "value": "₱0.00",
                },
                {
                    "key": "net_position",
                    "title": "NET POSITION",
                    "value": "₱0.00",
                },
            ],
        )

        self.summary.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(0, 8),
        )

    def _build_secondary_summary(self):
        self.secondary_summary = Cards(
            self,
            [
                {
                    "key": "assets",
                    "title": "ASSETS",
                    "value": "₱0.00",
                },
                {
                    "key": "inventory",
                    "title": "INVENTORY",
                    "value": "₱0.00",
                },
                {
                    "key": "receivables",
                    "title": "RECEIVABLES",
                    "value": "₱0.00",
                },
                {
                    "key": "liabilities",
                    "title": "LIABILITIES",
                    "value": "₱0.00",
                },
            ],
        )

        self.secondary_summary.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(0, 8),
        )

    def _build_detail_sections(self):
        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        container.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, 8),
        )

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self._build_account_balances(container)
        self._build_recent_transactions(container)

    def _build_account_balances(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#87AB9D",
            corner_radius=10,
        )

        panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 4),
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="Account Balances",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(12, 6),
        )

        self.account_table = Tables(
            panel,
            columns=[
                {
                    "key": "account",
                    "label": "ACCOUNT",
                    "weight": 3,
                    "minsize": 160,
                },
                {
                    "key": "type",
                    "label": "TYPE",
                    "weight": 2,
                    "minsize": 120,
                },
                {
                    "key": "balance",
                    "label": "BALANCE",
                    "weight": 2,
                    "minsize": 130,
                    "anchor": "e",
                },
            ],
            empty_text="No accounts found",
        )

        self.account_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12),
        )

    def _build_recent_transactions(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#87AB9D",
            corner_radius=10,
        )

        panel.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(4, 0),
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="Recent Transactions",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(12, 6),
        )

        self.transaction_table = Tables(
            panel,
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
                    "minsize": 160,
                },
                {
                    "key": "type",
                    "label": "TYPE",
                    "weight": 2,
                    "minsize": 130,
                },
                {
                    "key": "amount",
                    "label": "AMOUNT",
                    "weight": 2,
                    "minsize": 120,
                    "anchor": "e",
                },
            ],
            empty_text="No recent transactions",
        )

        self.transaction_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12),
        )

    def _build_quick_actions(self):
        Buttons(
            self,
            actions=[
                {
                    "label": "Add Income",
                    "command": lambda: self._open_transaction_form("INCOME"),
                    "style": "success",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Add Expense",
                    "command": lambda: self._open_transaction_form("EXPENSE"),
                    "style": "danger",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Transfer",
                    "command": lambda: self.navigate("Transfer"),
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Accounts",
                    "command": lambda: self.navigate("Accounts"),
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Reports",
                    "command": lambda: self.navigate("Reports"),
                    "width": 140,
                    "height": 40,
                },
            ],
            columns=5,
            height=40,
            padx=3,
            pady=0,
        ).grid(
            row=4,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X - 3,
            pady=(0, CONTENT_PAD_Y),
        )

    def _open_transaction_form(self, transaction_type):
        TransactionForm(
            self,
            transaction_type=transaction_type,
            on_saved=self.refresh,
        )

    def refresh(self):
        try:
            data = self._get_dashboard_data()

            self.summary.set_values(
                {
                    "income": format_currency(data["income"]),
                    "expenses": format_currency(data["expenses"]),
                    "net_position": format_currency(
                        data["net_position"]
                    ),
                }
            )

            self.secondary_summary.set_values(
                {
                    "assets": format_currency(data["assets"]),
                    "inventory": format_currency(data["inventory"]),
                    "receivables": format_currency(
                        data["receivables"]
                    ),
                    "liabilities": format_currency(
                        data["liabilities"]
                    ),
                }
            )

            self.account_table.set_rows(
                data["accounts"]
            )

            self.transaction_table.set_rows(
                data["transactions"]
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Refresh Dashboard",
                exc,
            )

    def _get_dashboard_data(self):
        transactions = transaction_service.get_transactions()

        if transactions:
            transaction_dates = [
                transaction[1]
                for transaction in transactions
                if transaction[1]
            ]

            start_date = min(transaction_dates)
        else:
            start_date = date.today().isoformat()

        review = financial_review_service.review_period(
            start_date,
            date.today().isoformat(),
        )

        accounts = []

        for account in account_service.get_accounts():
            account_id = account[0]
            account_name = account[1]
            account_type = account[2]
            active = account[3]

            if not active:
                continue

            balance = transaction_service.get_account_balance(
                account_id
            )

            accounts.append(
                {
                    "account": account_name,
                    "type": account_type,
                    "balance": format_currency(balance),
                }
            )

        assets = sum(
            asset[4] or 0
            for asset in asset_service.get_assets()
            if asset[6] == "ACTIVE"
        )

        inventory = sum(
            item[2] or 0
            for item in inventory_service.get_inventory_items()
            if item[6] == "AVAILABLE"
        )

        recent_transactions = []

        for transaction in transactions[:8]:
            transaction_id = transaction[0]
            transaction_date = transaction[1]
            description = transaction[2]
            transaction_type = transaction[3]

            try:
                _, entries = transaction_service.get_transaction_by_id(
                    transaction_id
                )
            except Exception:
                entries = []

            recent_transactions.append(
                {
                    "date": format_date(transaction_date),
                    "description": description,
                    "type": transaction_type.replace(
                        "_",
                        " ",
                    ),
                    "amount": self._display_amount(
                        transaction_type,
                        entries,
                    ),
                }
            )

        return {
            "income": review["income"],
            "expenses": review["expenses"],
            "net_position": review["estimated_net_worth"],
            "assets": assets,
            "inventory": inventory,
            "receivables": review["outstanding_receivables"],
            "liabilities": review["outstanding_liabilities"],
            "accounts": accounts,
            "transactions": recent_transactions,
        }

    @staticmethod
    def _display_amount(transaction_type, entries):
        if not entries:
            return "₱0.00"

        amount = abs(entries[0][2])
        amount_text = format_currency(amount)

        if transaction_type == "INCOME":
            return f"+ {amount_text}"

        if transaction_type == "EXPENSE":
            return f"- {amount_text}"

        if transaction_type in {
            "RECEIVABLE",
            "LIABILITY_PAYMENT",
        }:
            return f"- {amount_text}"

        return amount_text