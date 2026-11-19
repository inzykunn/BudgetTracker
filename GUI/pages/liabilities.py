from datetime import date

import customtkinter as ctk

from GUI.components.buttons import Buttons
from GUI.components.forms import FormWindow
from GUI.components.selectors import Selector
from GUI.components.tables import Tables
from GUI.styles.colors import CONTENT, TEXT_DARK
from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    FONT_PAGE_TITLE,
    FORM_HEIGHT,
    FORM_WIDTH,
)
from GUI.utils.feedback import (
    show_info,
    show_operation_error,
    show_update_success,
    show_save_success,
    show_warning,
)
from GUI.utils.formatters import format_currency, format_date
from GUI.utils.validation import (
    validate_currency,
    validate_length,
)
from services import account_service, liability_service, people_service


class LiabilitiesPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate
        self.accounts = []
        self.account_map = {}
        self.people = []
        self.selected_liability_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

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

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Liabilities",
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
                    "label": "Add Liability",
                    "command": self._open_add_form,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Payment",
                    "command": self._open_payment_form,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "Edit",
                    "command": self._open_edit_form,
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
        ).grid(
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
                    "minsize": 140,
                    "anchor": "e",
                },
                {
                    "key": "balance",
                    "label": "BALANCE",
                    "weight": 1,
                    "minsize": 140,
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
            empty_text="No liabilities yet",
            command=self._select_liability,
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

            self.account_map = {
                account[1]: account[0]
                for account in self.accounts
            }

            self.people = people_service.get_people()

            liabilities = liability_service.get_liabilities()

        except Exception as exc:
            show_operation_error(
                self,
                "Load liabilities",
                exc,
            )
            return

        rows = []
        balance_error = None

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
                paid_amount = original_amount - balance
                formatted_balance = format_currency(balance)
                formatted_paid = format_currency(paid_amount)

            except Exception as exc:
                if balance_error is None:
                    balance_error = exc

                formatted_balance = "Unavailable"
                formatted_paid = "Unavailable"

            rows.append(
                {
                    "id": liability_id,
                    "person_name": self._get_person_name(person_id),
                    "description": description,
                    "original_amount": format_currency(
                        original_amount
                    ),
                    "paid_amount": formatted_paid,
                    "balance": formatted_balance,
                    "created": format_date(date_created),
                    "due": (
                        format_date(due_date)
                        if due_date
                        else "-"
                    ),
                    "status": status,
                }
            )

        self.table.set_rows(rows)

        if self.selected_liability_id is not None:
            selected_exists = any(
                row["id"] == self.selected_liability_id
                for row in rows
            )

            if not selected_exists:
                self.selected_liability_id = None

        if balance_error is not None:
            show_operation_error(
                self,
                "Load liability balance",
                balance_error,
            )

    def _get_person_name(self, person_id):
        if person_id is None:
            return "-"

        for person in self.people:
            if person[0] == person_id:
                return person[1]

        return "-"

    def _select_liability(self, row):
        if not isinstance(row, dict):
            return

        self.selected_liability_id = row.get("id")

    def _get_selected_liability(self):
        if self.selected_liability_id is None:
            show_warning(
                self,
                "Select Liability",
                "Select a liability row first, then use the action buttons.",
            )
            return None

        try:
            liability = liability_service.get_liability_by_id(
                self.selected_liability_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load liability",
                exc,
            )
            return None

        if not liability:
            self.selected_liability_id = None
            self.refresh()
            show_warning(
                self,
                "Liability Not Found",
                "The selected liability no longer exists.",
            )
            return None

        return liability

    def _get_liabilities_for_selector(self):
        try:
            liabilities = liability_service.get_liabilities()

        except Exception as exc:
            show_operation_error(
                self,
                "Load liabilities",
                exc,
            )
            return []

        return [
            {
                "id": liability[0],
                "description": liability[3],
                "status": liability[7],
            }
            for liability in liabilities
        ]

    def _open_add_form(self):
        LiabilityForm(
            self,
            mode="add",
            people=self.people,
            account_map=self.account_map,
            on_saved=self.refresh,
        )

    def _open_edit_form(self):
        if self.selected_liability_id is not None:
            liability = self._get_selected_liability()

            if liability is None:
                return

            self._edit_selected(liability)
            return

        liabilities = self._get_liabilities_for_selector()

        if not liabilities:
            show_info(
                self,
                "No Liabilities",
                "No liabilities are available to edit.",
            )
            return

        Selector(
            self,
            title="Select Liability",
            items=liabilities,
            display_key="description",
            value_key="id",
            description="Select the liability you want to edit.",
            select_button_text="Edit",
            on_selected=self._edit_selected,
        )

    def _edit_selected(self, selected):
        liability_id = self._get_item_id(selected)

        if liability_id is None:
            return

        try:
            liability = liability_service.get_liability_by_id(
                liability_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load liability",
                exc,
            )
            return

        if not liability:
            self.selected_liability_id = None
            self.refresh()
            show_warning(
                self,
                "Liability Not Found",
                "The selected liability no longer exists.",
            )
            return

        if liability[7] == "PAID":
            show_warning(
                self,
                "Unavailable",
                "A paid liability cannot be edited.",
            )
            return

        self.selected_liability_id = liability_id

        LiabilityForm(
            self,
            mode="edit",
            liability=liability,
            people=self.people,
            account_map=self.account_map,
            on_saved=self.refresh,
        )

    def _open_payment_form(self):
        if self.selected_liability_id is not None:
            liability = self._get_selected_liability()

            if liability is None:
                return

            self._payment_selected(liability)
            return

        liabilities = self._get_liabilities_for_selector()

        if not liabilities:
            show_info(
                self,
                "No Liabilities",
                "No liabilities are available for payment.",
            )
            return

        Selector(
            self,
            title="Select Liability",
            items=liabilities,
            display_key="description",
            value_key="id",
            description="Select the liability you want to make a payment for.",
            select_button_text="Payment",
            on_selected=self._payment_selected,
        )

    def _payment_selected(self, selected):
        liability_id = self._get_item_id(selected)

        if liability_id is None:
            return

        try:
            liability = liability_service.get_liability_by_id(
                liability_id
            )

            if not liability:
                show_warning(
                    self,
                    "Liability Not Found",
                    "The selected liability no longer exists.",
                )
                self.selected_liability_id = None
                self.refresh()
                return

            balance = liability_service.get_liability_balance(
                liability_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load liability balance",
                exc,
            )
            return

        self.selected_liability_id = liability_id

        if liability[7] == "PAID":
            show_warning(
                self,
                "Already Paid",
                "This liability has already been fully paid.",
            )
            return

        if balance <= 0:
            show_warning(
                self,
                "No Balance",
                "This liability has no remaining balance.",
            )
            return

        PaymentForm(
            self,
            liability,
            balance,
            self.account_map,
            on_saved=self.refresh,
        )

    def _open_view(self):
        if self.selected_liability_id is not None:
            liability = self._get_selected_liability()

            if liability is None:
                return

            self._view_selected(liability)
            return

        liabilities = self._get_liabilities_for_selector()

        if not liabilities:
            show_info(
                self,
                "No Liabilities",
                "No liabilities are available to view.",
            )
            return

        Selector(
            self,
            title="Select Liability",
            items=liabilities,
            display_key="description",
            value_key="id",
            description="Select the liability you want to view.",
            select_button_text="View",
            on_selected=self._view_selected,
        )

    def _view_selected(self, selected):
        liability_id = self._get_item_id(selected)

        if liability_id is None:
            return

        try:
            liability = liability_service.get_liability_by_id(
                liability_id
            )

            balance = liability_service.get_liability_balance(
                liability_id
            )

            history = liability_service.get_liability_balance_history(
                liability_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load liability details",
                exc,
            )
            return

        if not liability:
            self.selected_liability_id = None
            self.refresh()
            show_warning(
                self,
                "Liability Not Found",
                "The selected liability no longer exists.",
            )
            return

        self.selected_liability_id = liability_id

        (
            _,
            person_id,
            credit_account_id,
            description,
            original_amount,
            date_created,
            due_date,
            status,
        ) = liability

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
            f"Person ID: "
            f"{person_id if person_id is not None else 'None'}\n"
            f"Credit Account ID: "
            f"{credit_account_id if credit_account_id is not None else 'None'}\n"
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
            "Liability Details",
            details,
        )

    @staticmethod
    def _get_item_id(item):
        if isinstance(item, dict):
            return item.get("id")

        if isinstance(item, (tuple, list)):
            return item[0] if item else None

        return getattr(item, "id", None)


class LiabilityForm(FormWindow):
    def __init__(
        self,
        master,
        mode="add",
        liability=None,
        people=None,
        account_map=None,
        on_saved=None,
    ):
        self.mode = mode
        self.liability = liability
        self.people = people or []
        self.account_map = account_map or {}
        self.on_saved = on_saved

        super().__init__(
            master,
            "Add Liability" if mode == "add" else "Edit Liability",
            width=FORM_WIDTH,
            height=730,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Record the liability details below."
        )

        person_values = [
            f"{person[0]} - {person[1]}"
            for person in self.people
        ]

        selected_person = None

        if self.liability and self.liability[1] is not None:
            for person in self.people:
                if person[0] == self.liability[1]:
                    selected_person = f"{person[0]} - {person[1]}"
                    break

        self.person_selector = self.add_selector(
            "Person",
            person_values,
            value=selected_person,
        )

        self.description_entry = self.add_field(
            "Description",
            value=(
                self.liability[3]
                if self.liability
                else ""
            ),
            placeholder_text="Liability description",
        )

        self.amount_entry = self.add_currency_field(
            "Original Amount",
            value=(
                self.liability[4]
                if self.liability
                else ""
            ),
        )

        self.created_entry = self.add_date_field(
            "Date Created",
            value=(
                self.liability[5]
                if self.liability
                else date.today()
            ),
        )

        self.due_entry = self.add_date_field(
            "Due Date",
            value=(
                self.liability[6]
                if self.liability and self.liability[6]
                else ""
            ),
        )

        account_values = [
            f"{account_id} - {account_name}"
            for account_name, account_id in self.account_map.items()
        ]

        selected_account = None

        if self.liability and self.liability[2] is not None:
            for account_name, account_id in self.account_map.items():
                if account_id == self.liability[2]:
                    selected_account = (
                        f"{account_id} - {account_name}"
                    )
                    break

        self.credit_account_selector = self.add_selector(
            "Credit Account",
            account_values,
            value=selected_account,
        )

        self.add_buttons(
            save_text=(
                "Save Liability"
                if self.mode == "add"
                else "Save Changes"
            ),
            save_command=self._save,
        )

    def _save(self):
        try:
            person_value = self.person_selector.get()

            person_id = None

            if (
                person_value
                and person_value != "No options available"
            ):
                person_id = int(
                    person_value.split(" - ", 1)[0]
                )

            description = validate_length(
                self.description_entry.get(),
                "Description",
                min_length=1,
                max_length=255,
            )

            validate_currency(
                self.amount_entry.get(),
                "Original Amount",
            )

            amount = self.get_currency_value(
                self.amount_entry
            )

            created_date = self.get_date_value(
                self.created_entry
            ).isoformat()

            due_date = None

            if self.due_entry.get().strip():
                due_date = self.get_date_value(
                    self.due_entry
                ).isoformat()

            account_value = self.credit_account_selector.get()

            if (
                not account_value
                or account_value == "No options available"
            ):
                raise ValueError(
                    "Credit Account is required."
                )

            credit_account_id = int(
                account_value.split(" - ", 1)[0]
            )

        except ValueError as exc:
            show_warning(
                self,
                "Invalid Information",
                str(exc),
            )
            return

        try:
            if self.mode == "add":
                liability_service.record_liability(
                    created_date,
                    description,
                    credit_account_id,
                    amount,
                    person_id,
                    credit_account_id,
                    due_date,
                )

            else:
                liability_service.update_liability(
                    self.liability[0],
                    description,
                    amount,
                    created_date,
                    person_id,
                    credit_account_id,
                    due_date,
                    self.liability[7],
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save liability",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        if self.mode == "add":
            show_save_success(
                self,
                "Liability",
            )
        else:
            show_update_success(
                self,
                "Liability",
            )

        self.destroy()


class PaymentForm(FormWindow):
    def __init__(
        self,
        master,
        liability,
        balance,
        account_map,
        on_saved=None,
    ):
        self.liability = liability
        self.balance = balance
        self.account_map = account_map or {}
        self.on_saved = on_saved

        super().__init__(
            master,
            "Record Liability Payment",
            width=FORM_WIDTH,
            height=FORM_HEIGHT,
        )

        self._build()

    def _build(self):
        self.add_description(
            (
                f"{self.liability[3]}\n"
                f"Remaining Balance: "
                f"{format_currency(self.balance)}"
            )
        )

        self.date_entry = self.add_date_field(
            "Payment Date",
            value=date.today(),
        )

        self.description_entry = self.add_field(
            "Description",
            value=f"Payment for {self.liability[3]}",
        )

        self.amount_entry = self.add_currency_field(
            "Payment Amount",
            value=self.balance,
        )

        account_values = [
            f"{account_id} - {account_name}"
            for account_name, account_id in self.account_map.items()
        ]

        self.account_selector = self.add_selector(
            "Payment Account",
            account_values,
        )

        self.add_buttons(
            save_text="Record Payment",
            save_command=self._save,
        )

    def _save(self):
        try:
            payment_date = self.get_date_value(
                self.date_entry
            ).isoformat()

            description = validate_length(
                self.description_entry.get(),
                "Description",
                min_length=1,
                max_length=255,
            )

            validate_currency(
                self.amount_entry.get(),
                "Payment Amount",
            )

            amount = self.get_currency_value(
                self.amount_entry
            )

            if amount > self.balance:
                raise ValueError(
                    "Payment cannot exceed the remaining balance of "
                    f"{format_currency(self.balance)}."
                )

            account_value = self.account_selector.get()

            if (
                not account_value
                or account_value == "No options available"
            ):
                raise ValueError(
                    "Payment Account is required."
                )

            account_id = int(
                account_value.split(" - ", 1)[0]
            )

        except ValueError as exc:
            show_warning(
                self,
                "Invalid Payment",
                str(exc),
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
            show_operation_error(
                self,
                "Record liability payment",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        show_save_success(
            self,
            "Liability payment",
        )

        self.destroy()