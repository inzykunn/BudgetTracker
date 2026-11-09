from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from services import liability_service, account_service, people_service

from GUI.components.quick_action_buttons import QuickActionButtons
from GUI.components.tables import Tables

from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    SUCCESS,
    DANGER,
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


class LiabilitiesPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)

        self.navigate = navigate
        self.selected_liability_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
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
            text="Liabilities",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        actions = QuickActionButtons(
            header,
            [
                ("Add Liability", self._open_add_form),
                ("Make Payment", self._open_payment_form),
                ("Edit Liability", self._open_edit_form),
                ("Refresh", self.refresh),
            ],
            columns=4,
        )

        actions.grid(row=0, column=1, sticky="e")

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

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        table_frame = ctk.CTkFrame(
            panel,
            fg_color=CONTENT,
            corner_radius=8,
        )

        table_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18,
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            table_frame,
            columns=[
                {"label": "PERSON", "weight": 2, "minsize": 150},
                {"label": "DESCRIPTION", "weight": 3, "minsize": 200},
                {
                    "label": "ORIGINAL",
                    "weight": 1,
                    "minsize": 120,
                    "anchor": "e",
                },
                {
                    "label": "BALANCE",
                    "weight": 1,
                    "minsize": 120,
                    "anchor": "e",
                },
                {
                    "label": "CREATED",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "label": "DUE",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 100,
                    "anchor": "center",
                },
            ],
            empty_text="No liabilities yet",
            on_double_click=self._show_liability,
        )

        self.table.grid(row=0, column=0, sticky="nsew")

    def refresh(self):
        try:
            liabilities = liability_service.get_liabilities()
            people = people_service.get_people()

        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load liabilities.\n\n{exc}",
                parent=self,
            )
            return

        people_map = {
            person[0]: person[1]
            for person in people
        }

        self.table.clear()

        for liability in liabilities:
            (
                liability_id,
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status,
            ) = liability

            try:
                balance = liability_service.get_liability_balance(
                    liability_id
                )
            except Exception:
                balance = original_amount

            person_name = (
                people_map.get(person_id, "-")
                if person_id is not None
                else "-"
            )

            self.table.add_row(
                values=(
                    person_name,
                    description,
                    self._money(original_amount),
                    self._money(balance),
                    date_created,
                    due_date or "-",
                    status,
                ),
                row_id=liability_id,
                cell_styles={
                    2: {
                        "font": FONT_BODY_BOLD,
                        "text_color": TEXT_DARK,
                    },
                    3: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if balance == 0
                            else DANGER
                        ),
                    },
                    6: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if status == "PAID"
                            else DANGER
                        ),
                    },
                },
            )

    def _selected_liability(self):
        if self.selected_liability_id is None:
            messagebox.showinfo(
                "Select Liability",
                "Double-click a liability first, then use the action buttons to manage it.",
                parent=self,
            )
            return None

        try:
            return liability_service.get_liability_by_id(
                self.selected_liability_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Liability Error",
                f"Unable to load the liability.\n\n{exc}",
                parent=self,
            )
            return None

    def _open_add_form(self):
        LiabilityForm(
            self,
            mode="add",
            on_saved=self.refresh,
        )

    def _open_edit_form(self):
        liability = self._selected_liability()

        if liability is None:
            return

        if liability[7] == "PAID":
            messagebox.showwarning(
                "Unavailable",
                "A paid liability cannot be edited.",
                parent=self,
            )
            return

        LiabilityForm(
            self,
            mode="edit",
            liability=liability,
            on_saved=self.refresh,
        )

    def _open_payment_form(self):
        liability = self._selected_liability()

        if liability is None:
            return

        if liability[7] == "PAID":
            messagebox.showwarning(
                "Unavailable",
                "This liability has already been fully paid.",
                parent=self,
            )
            return

        PaymentForm(
            self,
            liability=liability,
            on_saved=self.refresh,
        )

    def _show_liability(self, liability_id):
        self.selected_liability_id = liability_id

        try:
            liability = liability_service.get_liability_by_id(
                liability_id
            )
            balance = liability_service.get_liability_balance(
                liability_id
            )

            person = None

            if liability[1] is not None:
                person = people_service.get_person_by_id(
                    liability[1]
                )

        except Exception as exc:
            messagebox.showerror(
                "Liability Error",
                f"Unable to load liability details.\n\n{exc}",
                parent=self,
            )
            return

        if not liability:
            return

        person_name = (
            person[1]
            if person
            else "-"
        )

        details = (
            f"Person: {person_name}\n"
            f"Description: {liability[3]}\n"
            f"Original Amount: {self._money(liability[4])}\n"
            f"Balance: {self._money(balance)}\n"
            f"Date Created: {liability[5]}\n"
            f"Due Date: {liability[6] or 'None'}\n"
            f"Status: {liability[7]}"
        )

        messagebox.showinfo(
            "Liability",
            details,
            parent=self,
        )

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"


class LiabilityForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        mode="add",
        liability=None,
        on_saved=None,
    ):
        super().__init__(master)

        self.master_page = master
        self.mode = mode
        self.liability = liability
        self.on_saved = on_saved

        self.title(
            "Add Liability"
            if mode == "add"
            else "Edit Liability"
        )

        self.geometry("560x700")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        ctk.CTkLabel(
            panel,
            text=(
                "Add Liability"
                if self.mode == "add"
                else "Edit Liability"
            ),
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        ctk.CTkLabel(
            panel,
            text="Record the liability details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        people = people_service.get_people()

        self.person_map = {
            person[1]: person[0]
            for person in people
        }

        person_names = list(self.person_map.keys())

        selected_person = ""

        if self.liability and self.liability[1] is not None:
            selected_person = next(
                (
                    name
                    for name, person_id in self.person_map.items()
                    if person_id == self.liability[1]
                ),
                "",
            )

        self.person_combo = self._combo(
            panel,
            "Person",
            ["None"] + person_names,
            selected_person or "None",
        )

        self.description_entry = self._field(
            panel,
            "Description",
            self.liability[3]
            if self.liability
            else "",
        )

        self.amount_entry = self._field(
            panel,
            "Original Amount",
            self._amount(self.liability[4])
            if self.liability
            else "",
        )

        self.created_entry = self._field(
            panel,
            "Date Created",
            self.liability[5]
            if self.liability
            else date.today().isoformat(),
        )

        self.due_entry = self._field(
            panel,
            "Due Date",
            self.liability[6]
            if self.liability and self.liability[6]
            else "",
        )

        if self.mode == "add":
            self.transaction_date_entry = self._field(
                panel,
                "Transaction Date",
                date.today().isoformat(),
            )

            self.transaction_description_entry = self._field(
                panel,
                "Transaction Description",
                "",
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

            self.account_combo = self._combo(
                panel,
                "Credit Account",
                account_names or ["No accounts available"],
                (
                    account_names[0]
                    if account_names
                    else "No accounts available"
                ),
            )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        ctk.CTkButton(
            buttons,
            text="Cancel",
            height=40,
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

        ctk.CTkButton(
            buttons,
            text="Save Liability",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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
            entry.insert(0, str(value))

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected,
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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
            values=values,
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    @staticmethod
    def _amount(value):
        return f"{value / 100:.2f}"

    def _save(self):
        person_name = self.person_combo.get().strip()
        description = self.description_entry.get().strip()

        amount_text = (
            self.amount_entry.get()
            .strip()
            .replace(",", "")
        )

        created_date = self.created_entry.get().strip()
        due_date = self.due_entry.get().strip() or None

        if (
            not description
            or not amount_text
            or not created_date
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self,
            )
            return

        person_id = self.person_map.get(person_name)

        if person_name == "None":
            person_id = None

        try:
            date.fromisoformat(created_date)

            if due_date:
                date.fromisoformat(due_date)

            original_amount = int(
                round(float(amount_text) * 100)
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for dates and a valid numeric amount.",
                parent=self,
            )
            return

        if original_amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Original amount must be greater than zero.",
                parent=self,
            )
            return

        try:
            if self.mode == "add":
                transaction_date = (
                    self.transaction_date_entry
                    .get()
                    .strip()
                )

                transaction_description = (
                    self.transaction_description_entry
                    .get()
                    .strip()
                )

                account_name = (
                    self.account_combo
                    .get()
                    .strip()
                )

                if (
                    not transaction_date
                    or not transaction_description
                ):
                    messagebox.showwarning(
                        "Missing Information",
                        "Please complete the transaction fields.",
                        parent=self,
                    )
                    return

                date.fromisoformat(transaction_date)

                account_id = self.account_map.get(
                    account_name
                )

                if account_id is None:
                    messagebox.showwarning(
                        "Account Required",
                        "Please select an active account.",
                        parent=self,
                    )
                    return

                liability_service.record_liability(
                    transaction_date,
                    transaction_description,
                    account_id,
                    original_amount,
                    person_id,
                    None,
                    due_date,
                )

            else:
                liability_service.update_liability(
                    self.liability[0],
                    description,
                    original_amount,
                    created_date,
                    person_id,
                    self.liability[2],
                    due_date,
                    self.liability[7],
                )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the liability.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class PaymentForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        liability,
        on_saved=None,
    ):
        super().__init__(master)

        self.liability = liability
        self.on_saved = on_saved

        self.title("Make Liability Payment")
        self.geometry("560x560")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        balance = liability_service.get_liability_balance(
            self.liability[0]
        )

        ctk.CTkLabel(
            panel,
            text="Make Payment",
            font=FONT_SECTION,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4),
        )

        ctk.CTkLabel(
            panel,
            text=(
                f"{self.liability[3]} · "
                f"Balance: ₱{balance / 100:,.2f}"
            ),
            font=FONT_BODY,
            text_color=TEXT_DARK,
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18),
        )

        self.date_entry = self._field(
            panel,
            "Payment Date",
            date.today().isoformat(),
        )

        self.description_entry = self._field(
            panel,
            "Payment Description",
            f"Payment for {self.liability[3]}",
        )

        self.amount_entry = self._field(
            panel,
            "Payment Amount",
            "",
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

        self.account_combo = self._combo(
            panel,
            "Payment Account",
            account_names or ["No accounts available"],
            (
                account_names[0]
                if account_names
                else "No accounts available"
            ),
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24),
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1,
        )

        ctk.CTkButton(
            buttons,
            text="Cancel",
            height=40,
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

        ctk.CTkButton(
            buttons,
            text="Make Payment",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=DANGER,
            hover_color="#8B3A3A",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0),
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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
            entry.insert(0, str(value))

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected,
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12),
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
            values=values,
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    def _save(self):
        payment_date = self.date_entry.get().strip()
        description = self.description_entry.get().strip()

        amount_text = (
            self.amount_entry.get()
            .strip()
            .replace(",", "")
        )

        account_name = self.account_combo.get().strip()

        if (
            not payment_date
            or not description
            or not amount_text
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self,
            )
            return

        if not self.account_map:
            messagebox.showwarning(
                "Account Required",
                "An active account is required to make the payment.",
                parent=self,
            )
            return

        try:
            date.fromisoformat(payment_date)

            amount = int(
                round(float(amount_text) * 100)
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and a valid numeric amount.",
                parent=self,
            )
            return

        if amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Payment amount must be greater than zero.",
                parent=self,
            )
            return

        try:
            balance = liability_service.get_liability_balance(
                self.liability[0]
            )

        except Exception as exc:
            messagebox.showerror(
                "Payment Error",
                f"Unable to check the liability balance.\n\n{exc}",
                parent=self,
            )
            return

        if amount > balance:
            messagebox.showwarning(
                "Invalid Payment",
                "Payment cannot be greater than the outstanding liability.",
                parent=self,
            )
            return

        account_id = self.account_map.get(
            account_name
        )

        if account_id is None:
            messagebox.showwarning(
                "Account Required",
                "Please select an active account.",
                parent=self,
            )
            return

        try:
            liability_service.record_liability_payment(
                payment_date,
                description,
                account_id,
                self.liability[0],
                amount,
            )

        except Exception as exc:
            messagebox.showerror(
                "Payment Error",
                f"Unable to record the payment.\n\n{exc}",
                parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()