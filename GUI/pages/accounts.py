import customtkinter as ctk
from datetime import date
from tkinter import messagebox
from services import account_service
from GUI.components.tables import Tables
from GUI.styles.colors import CONTENT, PANEL, PANEL_HOVER, TEXT_DARK, TEXT_LIGHT, INPUT_BG, INPUT_BORDER, SUCCESS, \
    DANGER
from GUI.styles.theme import CONTENT_PAD_X, CONTENT_PAD_Y, PANEL_RADIUS, BUTTON_RADIUS, INPUT_RADIUS, FONT_SECTION, \
    FONT_BODY, FONT_BODY_BOLD, FONT_FORM_LABEL, FONT_FORM_INPUT


class AccountsPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)
        self.navigate = navigate
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=CONTENT_PAD_X, pady=(CONTENT_PAD_Y, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Accounts",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Add Account",
            width=140,
            height=44,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL,
            hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self._open_add
        ).grid(row=0, column=1, sticky="e")

    def _build_table(self):
        panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=PANEL_RADIUS)
        panel.grid(row=1, column=0, sticky="nsew", padx=CONTENT_PAD_X, pady=(0, CONTENT_PAD_Y))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            panel,
            columns=[
                {"label": "NAME", "weight": 3, "minsize": 160},
                {"label": "TYPE", "weight": 2, "minsize": 140},
                {"label": "STATUS", "weight": 1, "minsize": 110},
                {"label": "CREATED", "weight": 2, "minsize": 140},
                {"label": "ACTIONS", "weight": 2, "minsize": 180},
            ],
            empty_text="No accounts yet"
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)

    def refresh(self):
        try:
            accounts = account_service.get_accounts()
        except Exception as exc:
            messagebox.showerror("Load Error", f"Unable to load accounts.\n\n{exc}", parent=self)
            return

        self.table.clear()

        for account in accounts:
            account_id, name, account_type, is_active, created_at = account
            status = "Active" if is_active else "Inactive"
            status_color = SUCCESS if is_active else DANGER
            self.table.add_row(
                values=(name, account_type, status, created_at, ""),
                row_id=account_id,
                cell_styles={
                    2: {
                        "font": FONT_BODY_BOLD,
                        "text_color": status_color
                    }
                }
            )
            row=self.table.rows[-1]
            action_frame=ctk.CTkFrame(row,fg_color="transparent")
            action_frame.grid(row=0,column=4,sticky="e",padx=8,pady=5)
            ctk.CTkButton(
                action_frame,
                text="Edit",
                width=68,
                height=30,
                corner_radius=BUTTON_RADIUS,
                fg_color=PANEL_HOVER,
                hover_color=CONTENT,
                text_color=TEXT_DARK,
                font=FONT_BODY_BOLD,
                command=lambda account_id=account_id:self._open_edit(account_id)
            ).pack(side="left",padx=(0,5))
            ctk.CTkButton(
                action_frame,
                text="Delete",
                width=68,
                height=30,
                corner_radius=BUTTON_RADIUS,
                fg_color=DANGER,
                hover_color="#913E3E",
                text_color=TEXT_LIGHT,
                font=FONT_BODY_BOLD,
                command=lambda account_id=account_id:self._delete_account(account_id)
            ).pack(side="left")

    def _open_add(self):
        AccountForm(self, on_saved=self.refresh)

    def _delete_account(self, account_id):
        if not messagebox.askyesno(
            "Delete Account",
            "Are you sure you want to delete this account?",
            parent=self
        ):
            return
        try:
            account_service.deactivate_account(account_id)
        except Exception as exc:
            messagebox.showerror(
                "Delete Error",
                f"Unable to delete the account.\n\n{exc}",
                parent=self
            )
            return
        self.refresh()

    def _open_edit(self, account_id):
        try:
            account = account_service.get_account_by_id(account_id)
        except Exception as exc:
            messagebox.showerror("Load Error", f"Unable to load the account.\n\n{exc}", parent=self)
            return

        if account:
            AccountForm(self, account=account, on_saved=self.refresh)


class AccountForm(ctk.CTkToplevel):
    def __init__(self, master, account=None, on_saved=None):
        super().__init__(master)
        self.account = account
        self.on_saved = on_saved
        self.title("Edit Account" if account else "Add Account")
        self.geometry("560x570" if account else "560x620")
        self.resizable(False, False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()

        self._build()

    def _build(self):
        panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=10)
        panel.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            panel,
            text="Edit Account" if self.account else "Add Account",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=28, pady=(24, 4))

        ctk.CTkLabel(
            panel,
            text="Enter the account details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=28, pady=(0, 18))

        self.name_entry = self._field(panel, "Name", self.account[1] if self.account else "")
        self.type_entry = self._field(panel, "Type", self.account[2] if self.account else "")

        if not self.account:
            self.opening_balance_entry = self._field(panel, "Opening Balance", "")
            self.opening_date_entry = self._field(panel, "Opening Date", date.today().isoformat())

        button_row = ctk.CTkFrame(panel, fg_color="transparent")
        button_row.pack(fill="x", padx=28, pady=(20, 24))
        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            button_row,
            text="Cancel",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self.destroy
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        if self.account:
            ctk.CTkButton(
                button_row,
                text="Deactivate",
                height=40,
                corner_radius=BUTTON_RADIUS,
                fg_color=DANGER,
                hover_color="#913E3E",
                text_color=TEXT_LIGHT,
                font=FONT_BODY_BOLD,
                command=self._deactivate
            ).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        else:
            ctk.CTkButton(
                button_row,
                text="Save Account",
                height=40,
                corner_radius=BUTTON_RADIUS,
                fg_color=TEXT_DARK,
                hover_color="#285B4B",
                text_color=TEXT_LIGHT,
                font=FONT_BODY_BOLD,
                command=self._save
            ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        if self.account:
            save_row = ctk.CTkFrame(panel, fg_color="transparent")
            save_row.pack(fill="x", padx=28, pady=(0, 24))
            ctk.CTkButton(
                save_row,
                text="Save Changes",
                height=40,
                corner_radius=BUTTON_RADIUS,
                fg_color=TEXT_DARK,
                hover_color="#285B4B",
                text_color=TEXT_LIGHT,
                font=FONT_BODY_BOLD,
                command=self._save
            ).pack(fill="x")

    def _field(self, parent, label, value):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(anchor="w", pady=(0, 5))

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

        if value:
            entry.insert(0, str(value))

        return entry

    def _save(self):
        name = self.name_entry.get().strip()
        account_type = self.type_entry.get().strip()

        if not name or not account_type:
            messagebox.showwarning("Missing Information", "Please complete the required fields.", parent=self)
            return

        try:
            if self.account:
                account_service.update_account(
                    self.account[0],
                    name,
                    account_type
                )
            else:
                amount_text = self.opening_balance_entry.get().strip().replace(",", "")
                opening_balance = None

                if amount_text:
                    try:
                        opening_balance = int(round(float(amount_text) * 100))
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid Amount",
                            "Enter a valid opening balance, for example 1250.00.",
                            parent=self
                        )
                        return

                    if opening_balance < 0:
                        messagebox.showwarning(
                            "Invalid Amount",
                            "Opening balance cannot be negative.",
                            parent=self
                        )
                        return

                opening_date = self.opening_date_entry.get().strip()

                if opening_balance not in (None, 0):
                    try:
                        date.fromisoformat(opening_date)
                    except ValueError:
                        messagebox.showwarning(
                            "Invalid Date",
                            "Use the date format YYYY-MM-DD.",
                            parent=self
                        )
                        return

                account_service.create_account(
                    name,
                    account_type,
                    opening_balance,
                    opening_date or None
                )

        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the account.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()

    def _deactivate(self):
        if not messagebox.askyesno(
                "Deactivate Account",
                "Are you sure you want to deactivate this account?",
                parent=self
        ):
            return

        try:
            account_service.deactivate_account(self.account[0])
        except Exception as exc:
            messagebox.showerror(
                "Deactivate Error",
                f"Unable to deactivate the account.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()