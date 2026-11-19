from datetime import date

import customtkinter as ctk

from GUI.components.buttons import Buttons
from GUI.components.forms import FormWindow
from GUI.components.selectors import Selector
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
    show_update_success,
    show_info,
)
from GUI.utils.formatters import (
    format_currency,
    format_date,
)
from GUI.utils.validation import (
    require_text,
    validate_length,
)
from services import receivable_service, account_service, people_service


class ReceivablesPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate
        self.accounts = []
        self.account_options = []
        self.people = []
        self.person_options = []
        self.selected_receivable_id = None

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
            text="Receivables",
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
                    "label": "Add Receivable",
                    "command": self._open_add,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Payment",
                    "command": self._open_payment,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "Edit",
                    "command": self._open_edit,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "View",
                    "command": self._open_view,
                    "style": "default",
                    "width": 80,
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
            columns=5,
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
                    "key": "person_name",
                    "label": "PERSON",
                    "weight": 2,
                    "minsize": 140,
                },
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
                    "key": "paid_amount",
                    "label": "PAID AMOUNT",
                    "weight": 1,
                    "minsize": 130,
                    "anchor": "e",
                },
                {
                    "key": "balance",
                    "label": "BALANCE",
                    "weight": 1,
                    "minsize": 130,
                    "anchor": "e",
                },
                {
                    "key": "created",
                    "label": "CREATED",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "due",
                    "label": "DUE",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "status",
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 100,
                    "anchor": "center",
                },
            ],
            empty_text="No receivables yet",
            command=self._select_receivable,
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
            self.accounts = [
                account
                for account in account_service.get_accounts()
                if account[3]
            ]

            self.account_options = [
                f"{account[0]} - {account[1]}"
                for account in self.accounts
            ]

            self.people = people_service.get_people()

            self.person_options = [
                f"{person[0]} - {person[1]}"
                for person in self.people
            ]

            receivables = receivable_service.get_receivables()

            rows = []

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

                balance = receivable_service.get_receivable_balance(
                    receivable_id
                )

                paid_amount = original_amount - balance

                rows.append(
                    {
                        "id": receivable_id,
                        "person_name": self._get_person_name(person_id),
                        "description": description,
                        "original_amount": format_currency(
                            original_amount
                        ),
                        "paid_amount": format_currency(
                            paid_amount
                        ),
                        "balance": format_currency(
                            balance
                        ),
                        "created": format_date(
                            date_created
                        ),
                        "due": (
                            format_date(due_date)
                            if due_date
                            else "-"
                        ),
                        "status": status,
                    }
                )

            self.table.set_rows(rows)

            if self.selected_receivable_id is not None:
                if not any(
                    row["id"] == self.selected_receivable_id
                    for row in rows
                ):
                    self.selected_receivable_id = None

        except Exception as exc:
            show_operation_error(
                self,
                "Load Receivables",
                exc,
            )

    def _get_person_name(self, person_id):
        if person_id is None:
            return "-"
        for person in self.people:
            if person[0] == person_id:
                return person[1]
        return "-"

    def _select_receivable(self, receivable):
        if not receivable:
            return

        if isinstance(receivable, dict):
            self.selected_receivable_id = receivable.get("id")
        else:
            self.selected_receivable_id = receivable

    def _get_selected_receivable(self):
        if self.selected_receivable_id is None:
            return None

        try:
            receivable = receivable_service.get_receivable_by_id(
                self.selected_receivable_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Receivable",
                exc,
            )
            return None

        if not receivable:
            show_warning(
                self,
                "Receivable Not Found",
                "The selected receivable no longer exists.",
            )
            self.selected_receivable_id = None
            self.refresh()
            return None

        return receivable

    def _get_rows(self):
        rows = self.table.get_rows()

        if not rows:
            show_warning(
                self,
                "No Receivables",
                "There are no receivables available.",
            )
            return None

        return rows

    def _open_add(self):
        if not self.account_options:
            show_warning(
                self,
                "No Accounts",
                "There are no active accounts available.",
            )
            return

        if not self.person_options:
            show_warning(
                self,
                "No People",
                "There are no people available.",
            )
            return

        ReceivableForm(
            self,
            account_options=self.account_options,
            person_options=self.person_options,
            on_saved=self.refresh,
        )

    def _open_edit(self):
        selected = self._get_selected_receivable()

        if selected is not None:
            self._edit_selected(selected)
            return

        rows = self._get_rows()

        if rows is None:
            return

        Selector(
            self,
            title="Select Receivable",
            items=rows,
            display_key="description",
            value_key="id",
            description="Choose the receivable you want to edit.",
            select_button_text="Edit Receivable",
            on_selected=self._edit_selected,
        )

    def _edit_selected(self, receivable):
        if not receivable:
            return

        if isinstance(receivable, dict):
            receivable_id = receivable.get("id")

            try:
                selected = receivable_service.get_receivable_by_id(
                    receivable_id
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Receivable",
                    exc,
                )
                return

        else:
            selected = receivable

        if not selected:
            show_warning(
                self,
                "Receivable Not Found",
                "The selected receivable no longer exists.",
            )
            self.selected_receivable_id = None
            self.refresh()
            return

        self.selected_receivable_id = selected[0]

        if selected[6] == "PAID":
            show_warning(
                self,
                "Unavailable",
                "A paid receivable cannot be edited.",
            )
            return

        if not self.person_options:
            show_warning(
                self,
                "No People",
                "There are no people available.",
            )
            return

        ReceivableForm(
            self,
            receivable=selected,
            account_options=self.account_options,
            person_options=self.person_options,
            on_saved=self.refresh,
        )

    def _open_payment(self):
        selected = self._get_selected_receivable()

        if selected is not None:
            self._payment_selected(selected)
            return

        rows = self._get_rows()

        if rows is None:
            return

        if not self.account_options:
            show_warning(
                self,
                "No Accounts",
                "There are no active accounts available.",
            )
            return

        Selector(
            self,
            title="Select Receivable",
            items=rows,
            display_key="description",
            value_key="id",
            description="Choose the receivable for the payment.",
            select_button_text="Receive Payment",
            on_selected=self._payment_selected,
        )

    def _payment_selected(self, receivable):
        if not receivable:
            return

        if isinstance(receivable, dict):
            receivable_id = receivable.get("id")

            try:
                selected = receivable_service.get_receivable_by_id(
                    receivable_id
                )

                balance = receivable_service.get_receivable_balance(
                    receivable_id
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Receivable Balance",
                    exc,
                )
                return

        else:
            selected = receivable

            try:
                balance = receivable_service.get_receivable_balance(
                    selected[0]
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Receivable Balance",
                    exc,
                )
                return

        if not selected:
            show_warning(
                self,
                "Receivable Not Found",
                "The selected receivable no longer exists.",
            )
            self.selected_receivable_id = None
            self.refresh()
            return

        self.selected_receivable_id = selected[0]

        if selected[6] == "PAID":
            show_warning(
                self,
                "Already Paid",
                "This receivable has already been fully paid.",
            )
            return

        if balance <= 0:
            show_warning(
                self,
                "No Balance",
                "This receivable has no remaining balance.",
            )
            return

        if not self.account_options:
            show_warning(
                self,
                "No Accounts",
                "There are no active accounts available.",
            )
            return

        PaymentForm(
            self,
            receivable=selected,
            balance=balance,
            account_options=self.account_options,
            on_saved=self.refresh,
        )

    def _open_view(self):
        selected = self._get_selected_receivable()

        if selected is not None:
            self._view_selected(selected)
            return

        rows = self._get_rows()

        if rows is None:
            return

        Selector(
            self,
            title="Select Receivable",
            items=rows,
            display_key="description",
            value_key="id",
            description="Choose the receivable you want to view.",
            select_button_text="View Receivable",
            on_selected=self._view_selected,
        )

    def _view_selected(self, receivable):
        if not receivable:
            return

        if isinstance(receivable, dict):
            receivable_id = receivable.get("id")

            try:
                selected = receivable_service.get_receivable_by_id(
                    receivable_id
                )

                balance = receivable_service.get_receivable_balance(
                    receivable_id
                )

                history = receivable_service.get_receivable_balance_history(
                    receivable_id
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Receivable Details",
                    exc,
                )
                return

        else:
            selected = receivable

            try:
                balance = receivable_service.get_receivable_balance(
                    selected[0]
                )

                history = receivable_service.get_receivable_balance_history(
                    selected[0]
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Receivable Details",
                    exc,
                )
                return

        if not selected:
            show_warning(
                self,
                "Receivable Not Found",
                "The selected receivable no longer exists.",
            )
            self.selected_receivable_id = None
            self.refresh()
            return

        self.selected_receivable_id = selected[0]

        (
            _,
            person_id,
            description,
            original_amount,
            date_created,
            due_date,
            status,
        ) = selected

        paid_amount = original_amount - balance

        history_text = "\n".join(
            (
                f"{format_date(row[2])}  -  "
                f"{format_currency(row[3])}  -  "
                f"{row[4]}"
            )
            for row in history
        )

        if not history_text:
            history_text = "No balance history"

        details = (
            f"Person ID: {person_id}\n"
            f"Description: {description}\n"
            f"Original Amount: {format_currency(original_amount)}\n"
            f"Paid Amount: {format_currency(paid_amount)}\n"
            f"Remaining Balance: {format_currency(balance)}\n"
            f"Created: {format_date(date_created)}\n"
            f"Due Date: "
            f"{format_date(due_date) if due_date else 'None'}\n"
            f"Status: {status}\n\n"
            f"Balance History:\n"
            f"{history_text}"
        )

        show_info(
            self,
            "Receivable Details",
            details,
        )


class ReceivableForm(FormWindow):
    def __init__(
        self,
        master,
        receivable=None,
        account_options=None,
        person_options=None,
        on_saved=None,
    ):
        self.receivable = receivable
        self.account_options = account_options or []
        self.person_options = person_options or []
        self.on_saved = on_saved

        super().__init__(
            master,
            "Edit Receivable"
            if receivable
            else "Add Receivable",
            width=560,
            height=720 if not receivable else 680,
        )

        self._build()

    def _get_person_value(self):
        if not self.receivable:
            return None

        person_id = self.receivable[1]

        for option in self.person_options:
            if option.startswith(f"{person_id} - "):
                return option

        return None

    def _build(self):
        self.add_description(
            "Enter the receivable details below."
        )

        self.person_selector = self.add_selector(
            "Person",
            self.person_options,
            value=self._get_person_value(),
        )

        self.description_entry = self.add_field(
            "Description",
            (
                self.receivable[2]
                if self.receivable
                else ""
            ),
        )

        self.amount_entry = self.add_currency_field(
            "Original Amount",
            (
                self.receivable[3]
                if self.receivable
                else ""
            ),
        )

        self.created_entry = self.add_date_field(
            "Date Created",
            (
                self.receivable[4]
                if self.receivable
                else date.today()
            ),
        )

        self.due_entry = self.add_date_field(
            "Due Date",
            (
                self.receivable[5]
                if self.receivable and self.receivable[5]
                else ""
            ),
        )

        if not self.receivable:
            self.account_selector = self.add_selector(
                "Account",
                self.account_options,
            )

        self.add_buttons(
            save_text=(
                "Save Changes"
                if self.receivable
                else "Save Receivable"
            ),
            save_command=self._save,
        )

    def _validate(self):
        try:
            person = self.person_selector.get()

            if not person or person == "No options available":
                raise ValueError(
                    "Person is required."
                )

            person_id = int(
                person.split(" - ", 1)[0]
            )

            description = validate_length(
                require_text(
                    self.description_entry.get(),
                    "Description",
                ),
                "Description",
                min_length=1,
                max_length=200,
            )

            original_amount = self.get_currency_value(
                self.amount_entry
            )

            if original_amount <= 0:
                raise ValueError(
                    "Original amount must be greater than zero."
                )

            created_date = self.get_date_value(
                self.created_entry
            )

            due_text = self.due_entry.get().strip()

            due_date = (
                self.get_date_value(
                    self.due_entry
                )
                if due_text
                else None
            )

            if due_date and due_date < created_date:
                raise ValueError(
                    "Due date cannot be before the creation date."
                )

            account_id = None

            if not self.receivable:
                account = self.account_selector.get()

                if not account or account == "No options available":
                    raise ValueError(
                        "Account is required."
                    )

                account_id = int(
                    account.split(" - ", 1)[0]
                )

            return (
                person_id,
                description,
                original_amount,
                created_date,
                due_date,
                account_id,
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
            person_id,
            description,
            original_amount,
            created_date,
            due_date,
            account_id,
        ) = values

        try:
            if self.receivable:
                receivable_service.update_receivable(
                    self.receivable[0],
                    description,
                    original_amount,
                    created_date.isoformat(),
                    (
                        due_date.isoformat()
                        if due_date
                        else None
                    ),
                    self.receivable[6],
                )

                show_update_success(
                    self,
                    "Receivable",
                )

            else:
                receivable_service.record_receivable(
                    created_date.isoformat(),
                    description,
                    account_id,
                    person_id,
                    original_amount,
                    (
                        due_date.isoformat()
                        if due_date
                        else None
                    ),
                )

                show_save_success(
                    self,
                    "Receivable",
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Receivable",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()


class PaymentForm(FormWindow):
    def __init__(
        self,
        master,
        receivable,
        balance,
        account_options=None,
        on_saved=None,
    ):
        self.receivable = receivable
        self.balance = balance
        self.account_options = account_options or []
        self.on_saved = on_saved

        super().__init__(
            master,
            "Receive Payment",
            width=560,
            height=620,
        )

        self._build()

    def _build(self):
        self.add_description(
            (
                f"{self.receivable[2]}\n"
                f"Remaining Balance: "
                f"{format_currency(self.balance)}"
            ),
        )

        self.date_entry = self.add_date_field(
            "Payment Date",
            date.today(),
        )

        self.description_entry = self.add_field(
            "Description",
            f"Payment for {self.receivable[2]}",
        )

        self.amount_entry = self.add_currency_field(
            "Payment Amount",
            self.balance,
        )

        self.account_selector = self.add_selector(
            "Deposit Account",
            self.account_options,
        )

        self.add_buttons(
            save_text="Receive Payment",
            save_command=self._save,
        )

    def _validate(self):
        try:
            payment_date = self.get_date_value(
                self.date_entry
            )

            description = validate_length(
                require_text(
                    self.description_entry.get(),
                    "Description",
                ),
                "Description",
                min_length=1,
                max_length=200,
            )

            payment_amount = self.get_currency_value(
                self.amount_entry
            )

            if payment_amount <= 0:
                raise ValueError(
                    "Payment amount must be greater than zero."
                )

            if payment_amount > self.balance:
                raise ValueError(
                    "Payment cannot exceed the remaining balance."
                )

            created_date = self.receivable[4]

            if created_date:
                created_date_text = str(
                    created_date
                )[:10]

                if payment_date.isoformat() < created_date_text:
                    raise ValueError(
                        "Payment date cannot be before the receivable creation date."
                    )

            account = self.account_selector.get()

            if not account or account == "No options available":
                raise ValueError(
                    "Deposit account is required."
                )

            account_id = int(
                account.split(" - ", 1)[0]
            )

            return (
                payment_date,
                description,
                payment_amount,
                account_id,
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
            payment_date,
            description,
            payment_amount,
            account_id,
        ) = values

        try:
            receivable_service.record_receivable_payment(
                payment_date.isoformat(),
                description,
                account_id,
                self.receivable[0],
                payment_amount,
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Receive Payment",
                exc,
            )
            return

        show_save_success(
            self,
            "Receivable payment",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()