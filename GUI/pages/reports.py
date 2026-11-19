from datetime import date

import customtkinter as ctk

from services import (
    financial_review_service,
    receivable_service,
    liability_service,
    people_service,
)

from GUI.components.buttons import Buttons
from GUI.components.cards import Cards
from GUI.components.forms import FormWindow
from GUI.components.tables import Tables

from GUI.styles.colors import (
    CONTENT,
    TEXT_DARK,
    SUCCESS,
    DANGER,
)

from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    FONT_PAGE_TITLE,
    FONT_BODY_BOLD,
)

from GUI.utils.feedback import (
    show_warning,
    show_operation_error,
)

from GUI.utils.formatters import (
    format_currency,
)


class ReportsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate
        self.report = None
        self.start_date = date.today().replace(day=1).isoformat()
        self.end_date = date.today().isoformat()
        self.current_section = "Financial Summary"

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            3,
            weight=1,
        )

        self._build()
        self._generate_report(
            self.start_date,
            self.end_date,
        )

    def _build(self):
        self._build_header()
        self._build_summary()
        self._build_navigation()
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

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent",
            corner_radius=0,
        )

        title_frame.grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkLabel(
            title_frame,
            text="Reports",
            font=FONT_PAGE_TITLE,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
        )

        self.period_label = ctk.CTkLabel(
            title_frame,
            text="",
            font=FONT_BODY_BOLD,
            text_color=TEXT_DARK,
        )

        self.period_label.pack(
            anchor="w",
            pady=(3, 0),
        )

        actions = Buttons(
            header,
            actions=[
                {
                    "label": "Generate Report",
                    "command": self._open_period_form,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Refresh",
                    "command": self._refresh_report,
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

        actions.grid(
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
                    "title": "INCOME",
                    "value": "₱0.00",
                },
                {
                    "key": "expenses",
                    "title": "EXPENSES",
                    "value": "₱0.00",
                },
                {
                    "key": "net_cash_flow",
                    "title": "NET CASH FLOW",
                    "value": "₱0.00",
                },
                {
                    "key": "net_worth",
                    "title": "ESTIMATED NET WORTH",
                    "value": "₱0.00",
                },
            ],
        )

        self.summary.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(0, 12),
        )

    def _build_navigation(self):
        navigation = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        navigation.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(0, 12),
        )

        navigation.grid_columnconfigure(
            0,
            weight=1,
        )

        self.section_buttons = Buttons(
            navigation,
            actions=[
                {
                    "label": "Financial Summary",
                    "command": lambda: self._show_section(
                        "Financial Summary"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 150,
                },
                {
                    "label": "Accounts",
                    "command": lambda: self._show_section(
                        "Accounts"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 100,
                },
                {
                    "label": "Categories",
                    "command": lambda: self._show_section(
                        "Categories"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 110,
                },
                {
                    "label": "Transactions",
                    "command": lambda: self._show_section(
                        "Transactions"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 110,
                },
                {
                    "label": "Assets",
                    "command": lambda: self._show_section(
                        "Assets"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 90,
                },
                {
                    "label": "Inventory",
                    "command": lambda: self._show_section(
                        "Inventory"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 100,
                },
                {
                    "label": "Receivables",
                    "command": lambda: self._show_section(
                        "Receivables"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 110,
                },
                {
                    "label": "Liabilities",
                    "command": lambda: self._show_section(
                        "Liabilities"
                    ),
                    "style": "default",
                    "height": 40,
                    "width": 110,
                },
            ],
            columns=4,
            height=40,
            padx=3,
            pady=3,
        )

        self.section_buttons.grid(
            row=0,
            column=0,
            sticky="ew",
        )

    def _build_table(self):
        self.table = Tables(
            self,
            columns=[],
            empty_text="Generate a report to view results",
        )

        self.table.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def _open_period_form(self):
        ReportPeriodForm(
            self,
            self.start_date,
            self.end_date,
            self._generate_report,
        )

    def _refresh_report(self):
        if not self.start_date or not self.end_date:
            self._open_period_form()
            return

        self._generate_report(
            self.start_date,
            self.end_date,
        )

    def _generate_report(self, start_date, end_date):
        try:
            report = financial_review_service.review_period(
                start_date,
                end_date,
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Generate Report",
                exc,
            )
            return

        self.start_date = start_date
        self.end_date = end_date
        self.report = report

        self.period_label.configure(
            text=f"{start_date} to {end_date}",
        )

        self.summary.set_values(
            {
                "income": format_currency(
                    report["income"]
                ),
                "expenses": format_currency(
                    report["expenses"]
                ),
                "net_cash_flow": format_currency(
                    report["net_cash_flow"]
                ),
                "net_worth": format_currency(
                    report["estimated_net_worth"]
                ),
            }
        )

        self._show_section(
            self.current_section
        )

    def _show_section(self, section):
        self.current_section = section

        if not self.report:
            return

        self.table.destroy()

        columns, rows, empty_text = self._get_section_data(
            section
        )

        self.table = Tables(
            self,
            columns=columns,
            rows=rows,
            empty_text=empty_text,
        )

        self.table.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def _get_section_data(self, section):
        if section == "Financial Summary":
            return self._financial_summary()

        if section == "Accounts":
            return self._accounts_summary()

        if section == "Categories":
            return self._categories_summary()

        if section == "Transactions":
            return self._transactions_summary()

        if section == "Assets":
            return self._assets_summary()

        if section == "Inventory":
            return self._inventory_summary()

        if section == "Receivables":
            return self._receivables_summary()

        if section == "Liabilities":
            return self._liabilities_summary()

        return [], [], "No report data available"

    def _financial_summary(self):
        report = self.report

        columns = [
            {
                "key": "metric",
                "label": "METRIC",
                "weight": 2,
                "minsize": 220,
            },
            {
                "key": "value",
                "label": "VALUE",
                "weight": 1,
                "minsize": 180,
                "anchor": "e",
            },
        ]

        rows = [
            {
                "metric": "Income",
                "value": format_currency(
                    report["income"]
                ),
            },
            {
                "metric": "Expenses",
                "value": format_currency(
                    report["expenses"]
                ),
            },
            {
                "metric": "Net Cash Flow",
                "value": format_currency(
                    report["net_cash_flow"]
                ),
            },
            {
                "metric": "Inventory Profit / Loss",
                "value": format_currency(
                    report["inventory_profit_loss"]
                ),
            },
            {
                "metric": "Outstanding Receivables",
                "value": format_currency(
                    report["outstanding_receivables"]
                ),
            },
            {
                "metric": "Outstanding Liabilities",
                "value": format_currency(
                    report["outstanding_liabilities"]
                ),
            },
            {
                "metric": "Estimated Net Worth",
                "value": format_currency(
                    report["estimated_net_worth"]
                ),
            },
        ]

        return (
            columns,
            rows,
            "No financial summary available",
        )

    def _accounts_summary(self):
        columns = [
            {
                "key": "account_name",
                "label": "ACCOUNT",
                "weight": 3,
                "minsize": 180,
            },
            {
                "key": "net_change",
                "label": "NET CHANGE",
                "weight": 1,
                "minsize": 150,
                "anchor": "e",
            },
        ]

        rows = []

        for item in self.report["transactions_by_account"]:
            rows.append(
                {
                    "id": item["account_id"],
                    "account_name": item["account_name"],
                    "net_change": format_currency(
                        item["net_change"]
                    ),
                }
            )

        return (
            columns,
            rows,
            "No account activity found",
        )

    def _categories_summary(self):
        columns = [
            {
                "key": "category",
                "label": "CATEGORY",
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
                "key": "transaction_count",
                "label": "TRANSACTIONS",
                "weight": 1,
                "minsize": 120,
                "anchor": "e",
            },
            {
                "key": "amount",
                "label": "AMOUNT",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
        ]

        rows = []

        for item in self.report["transactions_by_category"]:
            rows.append(
                {
                    "id": (
                        f"{item['category_id']}-"
                        f"{item['type']}"
                    ),
                    "category": item["category"],
                    "type": item["type"],
                    "transaction_count": item[
                        "transaction_count"
                    ],
                    "amount": format_currency(
                        item["amount"]
                    ),
                }
            )

        return (
            columns,
            rows,
            "No category activity found",
        )

    def _transactions_summary(self):
        columns = [
            {
                "key": "date",
                "label": "DATE",
                "weight": 1,
                "minsize": 110,
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
                "minsize": 120,
            },
            {
                "key": "amount",
                "label": "AMOUNT",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
        ]

        rows = []

        for item in self.report["transactions"]:
            amount = item["net_amount"]

            if item["type"] == "INCOME":
                amount_text = (
                    f"+ {format_currency(abs(amount))}"
                )
            elif item["type"] == "EXPENSE":
                amount_text = (
                    f"- {format_currency(abs(amount))}"
                )
            else:
                amount_text = format_currency(
                    abs(amount)
                )

            rows.append(
                {
                    "id": item["id"],
                    "date": item["date"],
                    "description": (
                        item["description"]
                        or ""
                    ),
                    "type": item["type"].replace(
                        "_",
                        " ",
                    ),
                    "amount": amount_text,
                }
            )

        return (
            columns,
            rows,
            "No transactions found",
        )

    def _assets_summary(self):
        columns = [
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
                "minsize": 140,
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
                "key": "status",
                "label": "STATUS",
                "weight": 1,
                "minsize": 110,
            },
            {
                "key": "acquired_date",
                "label": "ACQUIRED",
                "weight": 1,
                "minsize": 120,
            },
        ]

        rows = []

        for item in self.report["asset_activity"]:
            rows.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "category": item["category"],
                    "purchase_cost": format_currency(
                        item["purchase_cost"]
                    ),
                    "current_value": format_currency(
                        item["current_value"]
                    ),
                    "status": item["status"],
                    "acquired_date": item[
                        "acquired_date"
                    ],
                }
            )

        return (
            columns,
            rows,
            "No asset activity found",
        )

    def _inventory_summary(self):
        columns = [
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
                "minsize": 130,
                "anchor": "e",
            },
            {
                "key": "profit_loss",
                "label": "PROFIT / LOSS",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
            {
                "key": "status",
                "label": "STATUS",
                "weight": 1,
                "minsize": 110,
            },
            {
                "key": "acquired_date",
                "label": "ACQUIRED",
                "weight": 1,
                "minsize": 120,
            },
            {
                "key": "sold_date",
                "label": "SOLD",
                "weight": 1,
                "minsize": 120,
            },
        ]

        rows = []

        for item in self.report["inventory_sales"]:
            sale_price = item["sale_price"]
            profit_loss = item["profit_loss"]

            rows.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "purchase_cost": format_currency(
                        item["purchase_cost"]
                    ),
                    "sale_price": (
                        format_currency(sale_price)
                        if sale_price is not None
                        else "-"
                    ),
                    "profit_loss": (
                        format_currency(profit_loss)
                        if profit_loss is not None
                        else "-"
                    ),
                    "status": item["status"],
                    "acquired_date": item[
                        "acquired_date"
                    ],
                    "sold_date": (
                        item["sold_date"]
                        if item["sold_date"]
                        else "-"
                    ),
                }
            )

        return (
            columns,
            rows,
            "No inventory activity found",
        )

    def _receivables_summary(self):
        columns = [
            {
                "key": "description",
                "label": "DESCRIPTION",
                "weight": 3,
                "minsize": 180,
            },
            {
                "key": "original_amount",
                "label": "ORIGINAL AMOUNT",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
            {
                "key": "balance",
                "label": "OUTSTANDING",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
            {
                "key": "due_date",
                "label": "DUE DATE",
                "weight": 1,
                "minsize": 120,
            },
            {
                "key": "status",
                "label": "STATUS",
                "weight": 1,
                "minsize": 110,
            },
        ]

        rows = []

        try:
            receivables = receivable_service.get_receivables()

            for item in receivables:
                balance = (
                    receivable_service.get_receivable_balance_as_of(
                        item[0],
                        self.end_date,
                    )
                )

                if balance is None:
                    balance = 0

                rows.append(
                    {
                        "id": item[0],
                        "description": item[2] or "",
                        "original_amount": format_currency(
                            item[3]
                        ),
                        "balance": format_currency(
                            balance
                        ),
                        "due_date": (
                            item[5]
                            if item[5]
                            else "-"
                        ),
                        "status": item[6],
                    }
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Receivables",
                exc,
            )

        return (
            columns,
            rows,
            "No receivables found",
        )

    def _liabilities_summary(self):
        columns = [
            {
                "key": "description",
                "label": "DESCRIPTION",
                "weight": 3,
                "minsize": 180,
            },
            {
                "key": "original_amount",
                "label": "ORIGINAL AMOUNT",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
            {
                "key": "balance",
                "label": "OUTSTANDING",
                "weight": 1,
                "minsize": 140,
                "anchor": "e",
            },
            {
                "key": "due_date",
                "label": "DUE DATE",
                "weight": 1,
                "minsize": 120,
            },
            {
                "key": "status",
                "label": "STATUS",
                "weight": 1,
                "minsize": 110,
            },
        ]

        rows = []

        try:
            liabilities = liability_service.get_liabilities()

            for item in liabilities:
                balance = (
                    liability_service.get_liability_balance_as_of(
                        item[0],
                        self.end_date,
                    )
                )

                if balance is None:
                    balance = 0

                rows.append(
                    {
                        "id": item[0],
                        "description": item[3] or "",
                        "original_amount": format_currency(
                            item[4]
                        ),
                        "balance": format_currency(
                            balance
                        ),
                        "due_date": (
                            item[6]
                            if item[6]
                            else "-"
                        ),
                        "status": item[7],
                    }
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Liabilities",
                exc,
            )

        return (
            columns,
            rows,
            "No liabilities found",
        )


class ReportPeriodForm(FormWindow):
    def __init__(
        self,
        master,
        start_date,
        end_date,
        on_generate,
    ):
        self.on_generate = on_generate

        super().__init__(
            master,
            "Report Period",
            width=560,
            height=430,
        )

        self._build(
            start_date,
            end_date,
        )

    def _build(
        self,
        start_date,
        end_date,
    ):
        self.add_description(
            "Select the period to use for the financial report."
        )

        self.start_entry = self.add_date_field(
            "Start Date",
            value=start_date,
            placeholder_text="MM/DD/YYYY",
        )

        self.end_entry = self.add_date_field(
            "End Date",
            value=end_date,
            placeholder_text="MM/DD/YYYY",
        )

        self.add_buttons(
            save_text="Generate Report",
            save_command=self._generate,
        )

    def _generate(self):
        try:
            start_date = self.get_date_value(
                self.start_entry
            )

            end_date = self.get_date_value(
                self.end_entry
            )

            if start_date > end_date:
                raise ValueError(
                    "Start date cannot be after the end date."
                )

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )
            return

        self.on_generate(
            start_date.isoformat(),
            end_date.isoformat(),
        )

        self.destroy()