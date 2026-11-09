from datetime import date
import customtkinter as ctk
from tkinter import messagebox

from services import account_service, category_service, finance_service
from GUI.styles.colors import CONTENT, PANEL, PANEL_HOVER, TEXT_DARK, TEXT_LIGHT, INPUT_BG, INPUT_BORDER
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


class TransactionForm(ctk.CTkToplevel):
    def __init__(self, master, transaction_type="EXPENSE", on_saved=None):
        super().__init__(master)
        self.on_saved = on_saved
        self.transaction_type = transaction_type.upper()
        self.title(f"Add {self.transaction_type.title()}")
        self.geometry(f"{FORM_WIDTH}x{FORM_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self.accounts = []
        self.categories = []
        self.account_map = {}
        self.category_map = {}

        self._build()
        self._load_choices()

    def _build(self):
        panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=10)
        panel.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            panel,
            text=f"Add {self.transaction_type.title()}",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(anchor="w", padx=FORM_PAD_X, pady=(FORM_PAD_Y, 4))

        ctk.CTkLabel(
            panel,
            text="Enter the transaction details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(anchor="w", padx=FORM_PAD_X, pady=(0, 18))

        self.date_entry = self._field(panel, "Date", date.today().isoformat())
        self.description_entry = self._field(panel, "Description", "")

        self.category_combo = self._combo(panel, "Category")
        self.account_combo = self._combo(panel, "Account")
        self.amount_entry = self._field(panel, "Amount", "")

        button_row = ctk.CTkFrame(panel, fg_color="transparent")
        button_row.pack(fill="x", padx=FORM_PAD_X, pady=(20, FORM_PAD_Y))
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
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            button_row,
            text="Save Transaction",
            height=FORM_BUTTON_HEIGHT,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=FORM_PAD_X, pady=(0, FORM_FIELD_GAP))

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).pack(anchor="w", pady=(0, 5))

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
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=FORM_PAD_X, pady=(0, FORM_FIELD_GAP))

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).pack(anchor="w", pady=(0, 5))

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
            self.accounts = [account for account in account_service.get_accounts() if account[3]]
            self.categories = category_service.get_categories()

            self.account_map = {account[1]: account[0] for account in self.accounts}
            self.category_map = {category[1]: category[0] for category in self.categories}

            account_names = list(self.account_map.keys())
            category_names = [category[1] for category in self.categories if category[2] == self.transaction_type]

            self.account_combo.configure(values=account_names or ["No accounts available"])
            self.category_combo.configure(values=category_names or ["No categories available"])

            if account_names:
                self.account_combo.set(account_names[0])
            if category_names:
                self.category_combo.set(category_names[0])
        except Exception as exc:
            messagebox.showerror("Load Error", f"Unable to load accounts or categories.\n\n{exc}", parent=self)

    def _save(self):
        transaction_date = self.date_entry.get().strip()
        description = self.description_entry.get().strip()
        account_name = self.account_combo.get().strip()
        category_name = self.category_combo.get().strip()
        amount_text = self.amount_entry.get().strip().replace(",", "")

        if not transaction_date or not description or not amount_text:
            messagebox.showwarning("Missing Information", "Please complete the required fields.", parent=self)
            return

        try:
            date.fromisoformat(transaction_date)
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use the date format YYYY-MM-DD.", parent=self)
            return

        try:
            amount = int(round(float(amount_text) * 100))
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Enter a valid amount, for example 1250.00.", parent=self)
            return

        if amount <= 0:
            messagebox.showwarning("Invalid Amount", "Amount must be greater than zero.", parent=self)
            return

        account_id = self.account_map.get(account_name)
        category_id = self.category_map.get(category_name)

        if account_id is None:
            messagebox.showwarning("Account Required", "Please select an account.", parent=self)
            return

        try:
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
                messagebox.showwarning(
                    "Unsupported Transaction",
                    f"The form does not support {self.transaction_type} yet.",
                    parent=self,
                )
                return
        except Exception as exc:
            messagebox.showerror("Save Error", f"Unable to save the transaction.\n\n{exc}", parent=self)
            return

        if self.on_saved:
            self.on_saved()
        self.destroy()
