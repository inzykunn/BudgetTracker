from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from services import receivable_service, account_service
from GUI.components.tables import Tables
from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TEXT_LIGHT,
    SUCCESS,
    DANGER,
    INPUT_BG,
    INPUT_BORDER,
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


class ReceivablesPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT
        )

        self.navigate = navigate
        self.accounts = []
        self.account_map = {}
        self.selected_receivable_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(CONTENT_PAD_Y, 10)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Receivables",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        actions = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        actions.grid(
            row=0,
            column=1,
            sticky="e"
        )

        buttons = [
            ("Add Receivable", self._open_add_form),
            ("Record Payment", self._open_payment_form),
            ("Edit Receivable", self._open_edit_form),
            ("Refresh", self.refresh),
        ]

        for index, (text, command) in enumerate(buttons):
            ctk.CTkButton(
                actions,
                text=text,
                width=140,
                height=44,
                corner_radius=BUTTON_RADIUS,
                fg_color=PANEL,
                hover_color=PANEL_HOVER,
                text_color=TEXT_DARK,
                font=FONT_BODY_BOLD,
                command=command
            ).grid(
                row=0,
                column=index,
                padx=4,
                pady=2
            )

    def _build_table(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y)
        )

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            panel,
            columns=[
                {
                    "label": "PERSON ID",
                    "weight": 1,
                    "minsize": 100
                },
                {
                    "label": "DESCRIPTION",
                    "weight": 3,
                    "minsize": 180
                },
                {
                    "label": "ORIGINAL AMOUNT",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e"
                },
                {
                    "label": "BALANCE",
                    "weight": 1,
                    "minsize": 140,
                    "anchor": "e"
                },
                {
                    "label": "CREATED",
                    "weight": 1,
                    "minsize": 110
                },
                {
                    "label": "DUE",
                    "weight": 1,
                    "minsize": 110
                },
                {
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 100,
                    "anchor": "center"
                },
            ],
            empty_text="No receivables yet",
            on_double_click=self._show_receivable
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18
        )

    def refresh(self):
        try:
            self.accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.account_map = {
                account[1]: account[0]
                for account in self.accounts
            }

            receivables = receivable_service.get_receivables()

        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load receivables.\n\n{exc}",
                parent=self
            )
            return

        self.table.clear()

        for receivable in receivables:
            (
                receivable_id,
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status,
            ) = receivable

            try:
                balance = receivable_service.get_receivable_balance(
                    receivable_id
                )
            except Exception:
                balance = original_amount

            self.table.add_row(
                values=(
                    person_id,
                    description,
                    self._money(original_amount),
                    self._money(balance),
                    date_created,
                    due_date or "-",
                    status,
                ),
                row_id=receivable_id,
                cell_styles={
                    2: {
                        "font": FONT_BODY_BOLD,
                        "text_color": TEXT_DARK
                    },
                    3: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if balance == 0
                            else DANGER
                        )
                    },
                    6: {
                        "font": FONT_BODY_BOLD,
                        "text_color": (
                            SUCCESS
                            if status == "PAID"
                            else TEXT_DARK
                        )
                    },
                }
            )

    def _selected_receivable(self):
        if self.selected_receivable_id is None:
            messagebox.showinfo(
                "Select Receivable",
                "Double-click a receivable row first, then use the action buttons.",
                parent=self
            )
            return None

        try:
            return receivable_service.get_receivable_by_id(
                self.selected_receivable_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Receivable Error",
                f"Unable to load the receivable.\n\n{exc}",
                parent=self
            )
            return None

    def _open_add_form(self):
        ReceivableForm(
            self,
            mode="add",
            account_map=self.account_map,
            on_saved=self.refresh
        )

    def _open_edit_form(self):
        receivable = self._selected_receivable()

        if receivable is None:
            return

        if receivable[6] == "PAID":
            messagebox.showwarning(
                "Unavailable",
                "A paid receivable cannot be edited.",
                parent=self
            )
            return

        ReceivableForm(
            self,
            mode="edit",
            receivable=receivable,
            account_map=self.account_map,
            on_saved=self.refresh
        )

    def _open_payment_form(self):
        receivable = self._selected_receivable()

        if receivable is None:
            return

        if receivable[6] == "PAID":
            messagebox.showwarning(
                "Already Paid",
                "This receivable has already been fully paid.",
                parent=self
            )
            return

        try:
            balance = receivable_service.get_receivable_balance(
                receivable[0]
            )

        except Exception as exc:
            messagebox.showerror(
                "Balance Error",
                f"Unable to load the receivable balance.\n\n{exc}",
                parent=self
            )
            return

        if balance <= 0:
            messagebox.showwarning(
                "No Balance",
                "This receivable has no remaining balance.",
                parent=self
            )
            return

        PaymentForm(
            self,
            receivable,
            balance,
            self.account_map,
            on_saved=self.refresh
        )

    def _show_receivable(self, receivable_id):
        self.selected_receivable_id = receivable_id

        try:
            receivable = receivable_service.get_receivable_by_id(
                receivable_id
            )

            balance = receivable_service.get_receivable_balance(
                receivable_id
            )

            history = receivable_service.get_receivable_balance_history(
                receivable_id
            )

        except Exception as exc:
            messagebox.showerror(
                "Receivable Error",
                f"Unable to load receivable details.\n\n{exc}",
                parent=self
            )
            return

        if not receivable:
            return

        (
            _,
            person_id,
            description,
            original_amount,
            date_created,
            due_date,
            status,
        ) = receivable

        history_text = "\n".join(
            (
                f"{row[2]}  -  "
                f"{self._money(row[3])}  -  "
                f"{row[4]}"
            )
            for row in history
        )

        if not history_text:
            history_text = "No balance history"

        details = (
            f"Person ID: {person_id}\n"
            f"Description: {description}\n"
            f"Original Amount: {self._money(original_amount)}\n"
            f"Current Balance: {self._money(balance)}\n"
            f"Created: {date_created}\n"
            f"Due Date: {due_date or 'None'}\n"
            f"Status: {status}\n\n"
            f"Balance History:\n"
            f"{history_text}"
        )

        messagebox.showinfo(
            "Receivable Details",
            details,
            parent=self
        )

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"


class ReceivableForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        mode="add",
        receivable=None,
        account_map=None,
        on_saved=None
    ):
        super().__init__(master)

        self.mode = mode
        self.receivable = receivable
        self.account_map = account_map or {}
        self.on_saved = on_saved

        self.title(
            "Add Receivable"
            if mode == "add"
            else "Edit Receivable"
        )

        self.geometry("580x700")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)

        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            panel,
            text=(
                "Add Receivable"
                if self.mode == "add"
                else "Edit Receivable"
            ),
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            panel,
            text="Record the receivable details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18)
        )

        self.person_entry = self._field(
            panel,
            "Person ID",
            self.receivable[1]
            if self.receivable
            else ""
        )

        self.description_entry = self._field(
            panel,
            "Description",
            self.receivable[2]
            if self.receivable
            else ""
        )

        self.amount_entry = self._field(
            panel,
            "Original Amount",
            self._amount_value(self.receivable[3])
            if self.receivable
            else ""
        )

        self.created_entry = self._field(
            panel,
            "Date Created",
            self.receivable[4]
            if self.receivable
            else date.today().isoformat()
        )

        self.due_entry = self._field(
            panel,
            "Due Date",
            self.receivable[5]
            if self.receivable and self.receivable[5]
            else ""
        )

        if self.mode == "add":
            account_names = list(
                self.account_map.keys()
            )

            self.account_combo = self._combo(
                panel,
                "Account",
                account_names or ["No accounts available"],
                (
                    account_names[0]
                    if account_names
                    else "No accounts available"
                )
            )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24)
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1
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
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        ctk.CTkButton(
            buttons,
            text=(
                "Save Receivable"
                if self.mode == "add"
                else "Save Changes"
            ),
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )

        entry.pack(fill="x")

        if value is not None and value != "":
            entry.insert(
                0,
                str(value)
            )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
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
            values=values
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    @staticmethod
    def _amount_value(cents):
        return f"{cents / 100:.2f}"

    def _save(self):
        person_text = (
            self.person_entry
            .get()
            .strip()
        )

        description = (
            self.description_entry
            .get()
            .strip()
        )

        amount_text = (
            self.amount_entry
            .get()
            .strip()
            .replace(",", "")
        )

        created_date = (
            self.created_entry
            .get()
            .strip()
        )

        due_date = (
            self.due_entry
            .get()
            .strip()
            or None
        )

        if (
            not person_text
            or not description
            or not amount_text
            or not created_date
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self
            )
            return

        try:
            person_id = int(person_text)

            amount = int(
                round(
                    float(amount_text) * 100
                )
            )

            date.fromisoformat(
                created_date
            )

            if due_date:
                date.fromisoformat(
                    due_date
                )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Person ID and amount must be valid. Dates must use YYYY-MM-DD.",
                parent=self
            )
            return

        if amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "The receivable amount must be greater than zero.",
                parent=self
            )
            return

        try:
            if self.mode == "add":
                account_name = (
                    self.account_combo
                    .get()
                    .strip()
                )

                account_id = self.account_map.get(
                    account_name
                )

                if account_id is None:
                    messagebox.showwarning(
                        "Account Required",
                        "Please select an active account.",
                        parent=self
                    )
                    return

                receivable_service.record_receivable(
                    created_date,
                    description,
                    account_id,
                    person_id,
                    amount,
                    due_date
                )

            else:
                receivable_service.update_receivable(
                    self.receivable[0],
                    description,
                    amount,
                    created_date,
                    due_date,
                    self.receivable[6]
                )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the receivable.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class PaymentForm(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        receivable,
        balance,
        account_map,
        on_saved=None
    ):
        super().__init__(master)

        self.receivable = receivable
        self.balance = balance
        self.account_map = account_map
        self.on_saved = on_saved

        self.title("Record Payment")
        self.geometry("580x620")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)

        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            panel,
            text="Record Payment",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            panel,
            text=(
                f"{self.receivable[2]}\n"
                f"Remaining Balance: {self._money(self.balance)}"
            ),
            font=FONT_BODY,
            text_color=TEXT_DARK,
            justify="left"
        ).pack(
            anchor="w",
            padx=28,
            pady=(0, 18)
        )

        self.date_entry = self._field(
            panel,
            "Payment Date",
            date.today().isoformat()
        )

        self.description_entry = self._field(
            panel,
            "Description",
            f"Payment for {self.receivable[2]}"
        )

        self.amount_entry = self._field(
            panel,
            "Payment Amount",
            self._amount_value(self.balance)
        )

        account_names = list(
            self.account_map.keys()
        )

        self.account_combo = self._combo(
            panel,
            "Deposit Account",
            account_names or ["No accounts available"],
            (
                account_names[0]
                if account_names
                else "No accounts available"
            )
        )

        buttons = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=28,
            pady=(20, 24)
        )

        buttons.grid_columnconfigure(
            (0, 1),
            weight=1
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
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        ctk.CTkButton(
            buttons,
            text="Record Payment",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=SUCCESS,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        entry = ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )

        entry.pack(fill="x")

        if value is not None:
            entry.insert(
                0,
                str(value)
            )

        return entry

    def _combo(
        self,
        parent,
        label,
        values,
        selected
    ):
        wrapper = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0, 5)
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
            values=values
        )

        combo.pack(fill="x")
        combo.set(selected)

        return combo

    @staticmethod
    def _money(value):
        return f"₱{value / 100:,.2f}"

    @staticmethod
    def _amount_value(cents):
        return f"{cents / 100:.2f}"

    def _save(self):
        payment_date = (
            self.date_entry
            .get()
            .strip()
        )

        description = (
            self.description_entry
            .get()
            .strip()
        )

        amount_text = (
            self.amount_entry
            .get()
            .strip()
            .replace(",", "")
        )

        account_name = (
            self.account_combo
            .get()
            .strip()
        )

        if (
            not payment_date
            or not description
            or not amount_text
        ):
            messagebox.showwarning(
                "Missing Information",
                "Please complete the required fields.",
                parent=self
            )
            return

        try:
            date.fromisoformat(
                payment_date
            )

            amount = int(
                round(
                    float(amount_text) * 100
                )
            )

        except ValueError:
            messagebox.showwarning(
                "Invalid Information",
                "Use YYYY-MM-DD for the date and a valid payment amount.",
                parent=self
            )
            return

        if amount <= 0:
            messagebox.showwarning(
                "Invalid Amount",
                "Payment amount must be greater than zero.",
                parent=self
            )
            return

        if amount > self.balance:
            messagebox.showwarning(
                "Payment Too Large",
                (
                    f"The payment cannot exceed the remaining "
                    f"balance of {self._money(self.balance)}."
                ),
                parent=self
            )
            return

        account_id = self.account_map.get(
            account_name
        )

        if account_id is None:
            messagebox.showwarning(
                "Account Required",
                "Please select an active account.",
                parent=self
            )
            return

        try:
            receivable_service.record_receivable_payment(
                payment_date,
                description,
                account_id,
                self.receivable[0],
                amount
            )

        except Exception as exc:
            messagebox.showerror(
                "Payment Error",
                f"Unable to record the payment.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()