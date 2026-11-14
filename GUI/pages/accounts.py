import customtkinter as ctk

from services import account_service

from GUI.components.tables import Tables
from GUI.components.selectors import Selector
from GUI.components.forms import FormWindow
from GUI.components.buttons import Buttons

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
    show_save_success,
    show_update_success,
    confirm_action,
)

from GUI.utils.validation import (
    require_text,
    validate_length,
)


class AccountsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate

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
            text="Accounts",
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
                    "label": "Add Account",
                    "command": self._open_add,
                    "style": "primary",
                    "width": 140,
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
                    "label": "Refresh",
                    "command": self.refresh,
                    "style": "default",
                    "width": 90,
                    "height": 40,
                },
            ],
            columns=3,
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
                    "key": "id",
                    "label": "ID",
                    "weight": 1,
                    "minsize": 60,
                },
                {
                    "key": "name",
                    "label": "NAME",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "key": "type",
                    "label": "TYPE",
                    "weight": 2,
                    "minsize": 140,
                },
                {
                    "key": "status",
                    "label": "STATUS",
                    "weight": 1,
                    "minsize": 110,
                },
                {
                    "key": "created",
                    "label": "CREATED",
                    "weight": 2,
                    "minsize": 130,
                },
            ],
            empty_text="No accounts yet",
            command=self._select_account,
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
            accounts = account_service.get_accounts()

            rows = [
                {
                    "id": account[0],
                    "name": account[1],
                    "type": account[2],
                    "status": (
                        "Active"
                        if account[3]
                        else "Inactive"
                    ),
                    "created": str(
                        account[4] or ""
                    )[:10],
                }
                for account in accounts
            ]

            self.table.set_rows(rows)

        except Exception as exc:
            show_operation_error(
                self,
                "Load Accounts",
                exc,
            )

    def _open_add(self):
        AccountForm(
            self,
            on_saved=self.refresh,
        )

    def _open_edit(self):
        rows = self.table.get_rows()

        if not rows:
            show_warning(
                self,
                "No Accounts",
                "There are no accounts to edit.",
            )
            return

        Selector(
            self,
            title="Select Account",
            items=rows,
            display_key="name",
            value_key="id",
            description="Choose the account you want to edit.",
            select_button_text="Edit Account",
            on_selected=self._select_account,
        )

    def _select_account(self, account):
        if not account:
            return

        if isinstance(account, dict):
            account_id = account.get("id")
        else:
            account_id = account

        if account_id is None:
            return

        self._edit_selected(account_id)

    def _edit_selected(self, account_id):
        try:
            selected = account_service.get_account_by_id(
                account_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Account",
                exc,
            )
            return

        if not selected:
            show_warning(
                self,
                "Account Not Found",
                "The selected account no longer exists.",
            )
            self.refresh()
            return

        AccountForm(
            self,
            account=selected,
            on_saved=self.refresh,
        )


class AccountForm(FormWindow):
    def __init__(
        self,
        master,
        account=None,
        on_saved=None,
    ):
        self.account = account
        self.on_saved = on_saved

        super().__init__(
            master,
            "Edit Account" if account else "Add Account",
            width=520,
            height=500 if account else 430,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Enter the account details below."
        )

        self.name_entry = self.add_field(
            "Name",
            (
                self.account[1]
                if self.account
                else ""
            ),
        )

        self.type_entry = self.add_field(
            "Type",
            (
                self.account[2]
                if self.account
                else ""
            ),
        )

        if self.account:
            status = (
                "Active"
                if self.account[3]
                else "Inactive"
            )

            ctk.CTkLabel(
                self.body,
                text=f"Status: {status}",
                font=FONT_BODY_BOLD,
                text_color=(
                    SUCCESS
                    if self.account[3]
                    else DANGER
                ),
            ).pack(
                anchor="w",
                pady=(0, 18),
            )

            self._build_edit_buttons()

        else:
            self.add_buttons(
                save_text="Save Account",
                save_command=self._save,
            )

    def _build_edit_buttons(self):
        self.add_buttons(
            save_text="Save Changes",
            save_command=self._save,
        )

        status_action = (
            {
                "label": "Deactivate",
                "command": self._deactivate,
                "style": "danger",
                "height": 40,
            }
            if self.account[3]
            else {
                "label": "Reactivate",
                "command": self._reactivate,
                "style": "success",
                "height": 40,
            }
        )

        self.status_buttons = Buttons(
            self.body,
            actions=[status_action],
            columns=1,
            padx=0,
            pady=0,
        )

        self.status_buttons.pack(
            fill="x",
            pady=(10, 0),
        )

    def _validate(self):
        try:
            name = validate_length(
                require_text(
                    self.name_entry.get(),
                    "Account name",
                ),
                "Account name",
                min_length=1,
                max_length=100,
            )

            account_type = validate_length(
                require_text(
                    self.type_entry.get(),
                    "Account type",
                ),
                "Account type",
                min_length=1,
                max_length=50,
            )

            return name, account_type

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

        name, account_type = values

        try:
            if self.account:
                account_service.update_account(
                    self.account[0],
                    name,
                    account_type,
                )

                show_update_success(
                    self,
                    "Account",
                )

            else:
                account_service.create_account(
                    name,
                    account_type,
                )

                show_save_success(
                    self,
                    "Account",
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Account",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()

    def _deactivate(self):
        if not confirm_action(
            self,
            "Deactivate",
            "this account",
        ):
            return

        try:
            account_service.deactivate_account(
                self.account[0],
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Deactivate Account",
                exc,
            )
            return

        show_save_success(
            self,
            "Account deactivated",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()

    def _reactivate(self):
        if not confirm_action(
            self,
            "Reactivate",
            "this account",
        ):
            return

        try:
            account_service.activate_account(
                self.account[0],
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Reactivate Account",
                exc,
            )
            return

        show_save_success(
            self,
            "Account reactivated",
        )

        if self.on_saved:
            self.on_saved()

        self.destroy()