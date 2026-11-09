from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from services import finance_service, account_service

from GUI.components.quick_action_buttons import QuickActionButtons
from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    SUCCESS,
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
from GUI.styles.colors import INPUT_BG, INPUT_BORDER


class TransferPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)

        self.navigate = navigate

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_panel()

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

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Transfer",
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
                ("Transfer", self._save_transfer),
                ("Refresh", self._reset_form),
            ],
            columns=2,
        )

        actions.grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _build_panel(self):
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

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(
            panel,
            fg_color=CONTENT,
            corner_radius=8,
        )

        form.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18,
        )

        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form,
            text="Transfer Between Accounts",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=28,
            pady=(28, 4),
        )

        ctk.CTkLabel(
            form,
            text="Move money from one account to another.",
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=28,
            pady=(0, 22),
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

        account_names = list(self.account_map.keys())

        self.date_entry = self._field(
            form,
            2,
            "Transfer Date",
            date.today().isoformat(),
        )

        self.description_entry = self._field(
            form,
            3,
            "Description",
            "",
        )

        self.amount_entry = self._field(
            form,
            4,
            "Amount",
            "",
        )

        self.from_combo = self._combo(
            form,
            5,
            "From Account",
            account_names or ["No accounts available"],
            account_names[0] if account_names else "No accounts available",
        )

        self.to_combo = self._combo(
            form,
            6,
            "To Account",
            account_names or ["No accounts available"],
            account_names[1]
            if len(account_names) > 1
            else (
                account_names[0]
                if account_names
                else "No accounts available"
            ),
        )

        ctk.CTkButton(
            form,
            text="Transfer Money",
            height=42,
            corner_radius=BUTTON_RADIUS,
            fg_color=SUCCESS,
            hover_color="#416B58",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save_transfer,
        ).grid(
            row=7,
            column=0,
            sticky="ew",
            padx=28,
            pady=(18, 28),
        )

    def _field(self, parent, row, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=28,
            pady=(0, 14),
        )

        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5),
        )

        entry = ctk.CTkEntry(
            wrapper,
            height=38,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        entry.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        if value:
            entry.insert(0, str(value))

        return entry

    def _combo(
        self,
        parent,
        row,
        label,
        values,
        selected,
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=28,
            pady=(0, 14),
        )

        wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5),
        )

        combo = ctk.CTkComboBox(
            wrapper,
            height=38,
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
            values=values,
        )

        combo.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        combo.set(selected)

        return combo

    def _save_transfer(self):
        transfer_date = self.date_entry.get().strip()
        description = self.description_entry.get().strip()
        amount_text = (
            self.amount_entry.get()
            .strip()
            .replace(",", "")
        )

        from_account_name = self.from_combo.get().strip()
        to_account_name = self.to_combo.get().strip()

        if (
            not transfer_date
            or not description
            or not amount_text
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete all fields.",
                parent=self,
            )
            return

        try:
            date.fromisoformat(transfer_date)
            amount = int(round(float(amount_text) * 100))
        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and enter a valid amount.",
                parent=self,
            )
            return

        if amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Transfer amount must be greater than zero.",
                parent=self,
            )
            return

        from_account_id = self.account_map.get(
            from_account_name
        )
        to_account_id = self.account_map.get(
            to_account_name
        )

        if from_account_id is None or to_account_id is None:
            messagebox.showwarning(
                "Account Required",
                "Please select both accounts.",
                parent=self,
            )
            return

        if from_account_id == to_account_id:
            messagebox.showwarning(
                "Invalid Transfer",
                "Source and destination accounts must be different.",
                parent=self,
            )
            return

        try:
            finance_service.record_transfer(
                transfer_date,
                description,
                from_account_id,
                to_account_id,
                amount,
            )

        except Exception as exc:
            messagebox.showerror(
                "Transfer Error",
                f"Unable to record the transfer.\n\n{exc}",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Transfer Complete",
            "The transfer was recorded successfully.",
            parent=self,
        )

        self._reset_form()

    def _reset_form(self):
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())

        self.description_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")