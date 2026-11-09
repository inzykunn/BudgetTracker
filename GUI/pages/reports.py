from datetime import date
from tkinter import messagebox
import customtkinter as ctk

from services import financial_review_service

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


class ReportsPage(ctk.CTkFrame):
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
            text="Reports",
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
                ("Generate Report", self._generate_report),
                ("Refresh", self._generate_report),
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
        panel.grid_rowconfigure(1, weight=1)

        filters = ctk.CTkFrame(
            panel,
            fg_color=CONTENT,
            corner_radius=8,
        )

        filters.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=18,
        )

        filters.grid_columnconfigure(
            1,
            weight=1,
        )
        filters.grid_columnconfigure(
            3,
            weight=1,
        )

        ctk.CTkLabel(
            filters,
            text="Start Date",
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(20, 8),
            pady=18,
        )

        self.start_entry = ctk.CTkEntry(
            filters,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        self.start_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=18,
        )

        self.start_entry.insert(
            0,
            date.today().replace(
                day=1
            ).isoformat(),
        )

        ctk.CTkLabel(
            filters,
            text="End Date",
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=(0, 8),
            pady=18,
        )

        self.end_entry = ctk.CTkEntry(
            filters,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT,
        )

        self.end_entry.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(0, 20),
            pady=18,
        )

        self.end_entry.insert(
            0,
            date.today().isoformat(),
        )

        table_frame = ctk.CTkFrame(
            panel,
            fg_color=CONTENT,
            corner_radius=8,
        )

        table_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 18),
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.table = Tables(
            table_frame,
            columns=[
                {
                    "label": "METRIC",
                    "weight": 2,
                    "minsize": 220,
                },
                {
                    "label": "VALUE",
                    "weight": 1,
                    "minsize": 180,
                    "anchor": "e",
                },
            ],
            empty_text="Generate a report to view results",
        )

        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def _generate_report(self):
        start_date = self.start_entry.get().strip()
        end_date = self.end_entry.get().strip()

        try:
            report = financial_review_service.review_period(
                start_date,
                end_date,
            )

        except Exception as exc:
            messagebox.showerror(
                "Report Error",
                f"Unable to generate the report.\n\n{exc}",
                parent=self,
            )
            return

        self.table.clear()

        rows = [
            ("Income", report["income"]),
            ("Expenses", report["expenses"]),
            ("Net Cash Flow", report["net_cash_flow"]),
            (
                "Inventory Profit / Loss",
                report["inventory_profit_loss"],
            ),
            (
                "Outstanding Receivables",
                report["outstanding_receivables"],
            ),
            (
                "Outstanding Liabilities",
                report["outstanding_liabilities"],
            ),
            (
                "Estimated Net Worth",
                report["estimated_net_worth"],
            ),
        ]

        for metric, value in rows:
            color = TEXT_DARK

            if metric in {
                "Income",
                "Net Cash Flow",
            } and value >= 0:
                color = SUCCESS

            if metric in {
                "Expenses",
                "Outstanding Liabilities",
            }:
                color = DANGER

            self.table.add_row(
                values=(
                    metric,
                    self._money(value),
                ),
                cell_styles={
                    1: {
                        "font": FONT_BODY_BOLD,
                        "text_color": color,
                    }
                },
            )

    @staticmethod
    def _money(value):
        return f"₱{(value or 0) / 100:,.2f}"