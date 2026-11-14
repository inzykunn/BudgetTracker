from datetime import date
from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from services import account_service, category_service, finance_service
from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    INPUT_BG,
    INPUT_BORDER,
)
from GUI.styles.theme import (
    FORM_WIDTH,
    FORM_HEIGHT,
    FORM_PAD_X,
    FORM_PAD_Y,
    FORM_FIELD_GAP,
    FORM_BUTTON_HEIGHT,
    INPUT_RADIUS,
    BUTTON_RADIUS,
    FONT_SECTION,
    FONT_FORM_LABEL,
    FONT_FORM_INPUT,
    FONT_BODY,
    FONT_BODY_BOLD,
)
from GUI.utils.feedback import (
    show_error,
    show_warning,
    show_save_success,
)
from GUI.utils.formatters import parse_currency, parse_date


class TransactionForm(ctk.CTkToplevel):
    def __init__(self, master, transaction_type="EXPENSE", on_saved=None):
        super().__init__(master)

        self.on_saved = on_saved
        self.transaction_type = transaction_type.upper()

        self.accounts = []
        self.categories = []
        self.account_map = {}
        self.category_map = {}

        self.title(f"Add {self.transaction_type.title()}")
        self.geometry(f"{FORM_WIDTH}x{FORM_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()
        self._load_choices()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=10,
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        ctk.CTkLabel(
            panel,
            text=f"Add {self.transaction_type.title()}",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=FORM_PAD_X,
            pady=(FORM_PAD_Y, 4),
        )

        ctk.CTkLabel(
            panel,
            text="Enter the transaction details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=FORM_PAD_X,
            pady=(0, 18),
        )

        self.date_entry = self._field(
            panel,
            "Date",
            date.today().isoformat(),
        )

        self.description_entry = self._field(
            panel,
            "Description",
        )

        self.category_combo = self._combo(
            panel,
            "Category",
        )

        self.account_combo = self._combo(
            panel,
            "Account",
        )

        self.amount_entry = self._field(
            panel,
            "Amount",
        )

        button_row = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        button_row.pack(
            fill="x",
            padx=FORM_PAD_X,
            pady=(20, FORM_PAD_Y),
        )

        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_row,
            text="Cancel",
            height=FORM_BUTTON_HEIGHT,
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

        self.save_button = ctk.CTkButton(
            button_row,
            text="Save Transaction",
            height=FORM_BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        )

        self.save_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _field(self, parent, label, value=""):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=FORM_PAD_X,
            pady=(0, FORM_FIELD_GAP),
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
            entry.insert(0, value)

        return entry

    def _combo(self, parent, label):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=FORM_PAD_X,
            pady=(0, FORM_FIELD_GAP),
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
            values=["Loading..."],
        )

        combo.pack(fill="x")

        return combo

    def _load_choices(self):
        try:
            self.accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.categories = category_service.get_categories()

            self.account_map = {
                str(account[1]): account[0]
                for account in self.accounts
            }

            self.category_map = {
                str(category[1]): category[0]
                for category in self.categories
            }

            account_names = list(self.account_map.keys())

            category_names = [
                str(category[1])
                for category in self.categories
                if category[2] == self.transaction_type
            ]

            self.account_combo.configure(
                values=account_names or ["No accounts available"]
            )

            self.category_combo.configure(
                values=category_names or ["No categories available"]
            )

            if account_names:
                self.account_combo.set(account_names[0])
            else:
                self.account_combo.set("No accounts available")

            if category_names:
                self.category_combo.set(category_names[0])
            else:
                self.category_combo.set("No categories available")

        except Exception as exc:
            show_error(
                self,
                "Load Error",
                f"Unable to load accounts or categories.\n\n{exc}",
            )

    def _get_account_id(self):
        account_name = self.account_combo.get().strip()

        if not account_name or account_name not in self.account_map:
            raise ValueError("Please select an account.")

        return self.account_map[account_name]

    def _get_category_id(self):
        category_name = self.category_combo.get().strip()

        if not category_name or category_name not in self.category_map:
            raise ValueError("Please select a category.")

        return self.category_map[category_name]

    def _validate(self):
        transaction_date = parse_date(
            self.date_entry.get()
        )

        description = self.description_entry.get().strip()

        if not description:
            raise ValueError("Description is required.")

        account_id = self._get_account_id()
        category_id = self._get_category_id()

        amount = parse_currency(
            self.amount_entry.get()
        )

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        return (
            transaction_date,
            description,
            account_id,
            category_id,
            amount,
        )

    def _save(self):
        try:
            (
                transaction_date,
                description,
                account_id,
                category_id,
                amount,
            ) = self._validate()

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )
            return

        self.save_button.configure(state="disabled")

        try:
            transaction_date = transaction_date.isoformat()

            if self.transaction_type == "INCOME":
                finance_service.record_income(
                    transaction_date,
                    description,
                    account_id,
                    amount,
                    category_id,
                )

            elif self.transaction_type == "EXPENSE":
                finance_service.record_expense(
                    transaction_date,
                    description,
                    account_id,
                    amount,
                    category_id,
                )

            else:
                show_warning(
                    self,
                    "Unsupported Transaction",
                    f"The form does not support {self.transaction_type} yet.",
                )
                self.save_button.configure(state="normal")
                return

        except Exception as exc:
            self.save_button.configure(state="normal")

            show_error(
                self,
                "Save Error",
                f"Unable to save the transaction.\n\n{exc}",
            )
            return

        if self.on_saved:
            self.on_saved()

        show_save_success(
            self,
            "Transaction",
        )

        self.destroy()