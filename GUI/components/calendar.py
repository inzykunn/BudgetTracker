import calendar
import ctypes
import sys
from datetime import date, datetime

import customtkinter as ctk

from GUI.styles.colors import (
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
)

from GUI.styles.theme import (
    PANEL_RADIUS,
    INPUT_RADIUS,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL_BOLD,
)


class CalendarPicker(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        initial_date=None,
        on_selected=None,
    ):
        super().__init__(master)

        self.on_selected = on_selected

        self.title("Select Date")
        self.geometry("360x430")
        self.resizable(False, False)
        self.configure(fg_color=PANEL)
        self.transient(master)
        self.grab_set()

        self._set_dark_titlebar()

        self.current_date = self._normalize_date(
            initial_date
        )

        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        self.selected_date = self.current_date

        self.view = "calendar"
        self.year_page_start = (
            (self.current_year // 10) * 10
        )

        self._build()

    def _set_dark_titlebar(self):
        if sys.platform != "win32":
            return

        try:
            hwnd = self.winfo_id()
            value = ctypes.c_int(1)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                20,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
        except Exception:
            pass

    def _normalize_date(self, value):
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            for fmt in (
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
            ):
                try:
                    return datetime.strptime(
                        value.strip(),
                        fmt,
                    ).date()
                except ValueError:
                    pass

        return date.today()

    def _build(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS,
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=14,
        )

        header = ctk.CTkFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
        )

        header.pack(
            fill="x",
            padx=18,
            pady=(18, 8),
        )

        header.grid_columnconfigure(
            1,
            weight=1,
        )

        self.previous_button = ctk.CTkButton(
            header,
            text="‹",
            width=38,
            height=34,
            corner_radius=INPUT_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=PANEL,
            text_color=TEXT_DARK,
            font=(FONT_BODY[0], 18, "bold"),
            command=self._previous,
        )

        self.previous_button.grid(
            row=0,
            column=0,
        )

        self.title_button = ctk.CTkButton(
            header,
            text="",
            height=34,
            corner_radius=INPUT_RADIUS,
            fg_color="transparent",
            hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self._title_clicked,
        )

        self.title_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=8,
        )

        self.next_button = ctk.CTkButton(
            header,
            text="›",
            width=38,
            height=34,
            corner_radius=INPUT_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=PANEL,
            text_color=TEXT_DARK,
            font=(FONT_BODY[0], 18, "bold"),
            command=self._next,
        )

        self.next_button.grid(
            row=0,
            column=2,
        )

        self.content_frame = ctk.CTkFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
        )

        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=4,
        )

        self._render()

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _render(self):
        self._clear_content()

        if self.view == "calendar":
            self._render_calendar()
        elif self.view == "months":
            self._render_months()
        else:
            self._render_years()

    def _render_calendar(self):
        self.title_button.configure(
            text=(
                f"{calendar.month_name[self.current_month]} "
                f"{self.current_year}"
            )
        )

        weekdays = (
            "Mo",
            "Tu",
            "We",
            "Th",
            "Fr",
            "Sa",
            "Su",
        )

        for column, name in enumerate(weekdays):
            self.content_frame.grid_columnconfigure(
                column,
                weight=1,
            )

            ctk.CTkLabel(
                self.content_frame,
                text=name,
                font=FONT_SMALL_BOLD,
                text_color=TEXT_DARK,
            ).grid(
                row=0,
                column=column,
                sticky="ew",
                pady=(6, 8),
            )

        weeks = calendar.monthcalendar(
            self.current_year,
            self.current_month,
        )

        today = date.today()

        for row_index, week in enumerate(
            weeks,
            start=1,
        ):
            self.content_frame.grid_rowconfigure(
                row_index,
                weight=1,
            )

            for column, day in enumerate(week):
                if day == 0:
                    continue

                day_date = date(
                    self.current_year,
                    self.current_month,
                    day,
                )

                if day_date == self.selected_date:
                    fg_color = PANEL_HOVER
                    hover_color = PANEL
                    text_color = TEXT_DARK

                elif day_date == today:
                    fg_color = PANEL_HOVER
                    hover_color = PANEL
                    text_color = TEXT_DARK

                else:
                    fg_color = PANEL
                    hover_color = PANEL_HOVER
                    text_color = TEXT_DARK

                ctk.CTkButton(
                    self.content_frame,
                    text=str(day),
                    height=36,
                    corner_radius=INPUT_RADIUS,
                    fg_color=fg_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    font=FONT_BODY,
                    command=lambda selected_day=day: (
                        self._select_date(selected_day)
                    ),
                ).grid(
                    row=row_index,
                    column=column,
                    sticky="ew",
                    padx=2,
                    pady=2,
                )

    def _render_months(self):
        self.title_button.configure(
            text=str(self.current_year)
        )

        months = (
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )

        for column in range(4):
            self.content_frame.grid_columnconfigure(
                column,
                weight=1,
            )

        for row in range(3):
            self.content_frame.grid_rowconfigure(
                row,
                weight=1,
            )

        for index, month_name in enumerate(months):
            month = index + 1

            if month == self.current_month:
                fg_color = PANEL_HOVER
                hover_color = PANEL
            else:
                fg_color = PANEL
                hover_color = PANEL_HOVER

            ctk.CTkButton(
                self.content_frame,
                text=month_name,
                height=46,
                corner_radius=INPUT_RADIUS,
                fg_color=fg_color,
                hover_color=hover_color,
                text_color=TEXT_DARK,
                font=FONT_BODY,
                command=lambda selected_month=month: (
                    self._select_month(selected_month)
                ),
            ).grid(
                row=index // 4,
                column=index % 4,
                sticky="ew",
                padx=4,
                pady=4,
            )

    def _render_years(self):
        start_year = self.year_page_start
        end_year = start_year + 9

        self.title_button.configure(
            text=f"{start_year} – {end_year}"
        )

        for column in range(4):
            self.content_frame.grid_columnconfigure(
                column,
                weight=1,
            )

        for row in range(3):
            self.content_frame.grid_rowconfigure(
                row,
                weight=1,
            )

        for index in range(12):
            year = start_year - 2 + index

            if year < 1:
                continue

            row = index // 4
            column = index % 4

            if year == self.current_year:
                fg_color = PANEL_HOVER
                hover_color = PANEL
                text_color = TEXT_DARK
            else:
                fg_color = PANEL
                hover_color = PANEL_HOVER
                text_color = TEXT_DARK

            ctk.CTkButton(
                self.content_frame,
                text=str(year),
                height=46,
                corner_radius=INPUT_RADIUS,
                fg_color=fg_color,
                hover_color=hover_color,
                text_color=text_color,
                font=FONT_BODY,
                command=lambda selected_year=year: (
                    self._select_year(selected_year)
                ),
            ).grid(
                row=row,
                column=column,
                sticky="ew",
                padx=4,
                pady=4,
            )

    def _title_clicked(self):
        if self.view == "calendar":
            self.view = "months"
            self._render()
            return

        if self.view == "months":
            self.year_page_start = (
                (self.current_year // 10) * 10
            )
            self.view = "years"
            self._render()
            return

        self.view = "months"
        self._render()

    def _previous(self):
        if self.view == "calendar":
            self._previous_month()
            return

        if self.view == "months":
            self.current_year -= 1
            self._render()
            return

        self.year_page_start -= 10
        self._render()

    def _next(self):
        if self.view == "calendar":
            self._next_month()
            return

        if self.view == "months":
            self.current_year += 1
            self._render()
            return

        self.year_page_start += 10
        self._render()

    def _previous_month(self):
        self.current_month -= 1

        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self._render()

    def _next_month(self):
        self.current_month += 1

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        self._render()

    def _select_year(self, year):
        self.current_year = year
        self.year_page_start = (
            (year // 10) * 10
        )
        self.view = "months"
        self._render()

    def _select_month(self, month):
        self.current_month = month
        self.view = "calendar"
        self._render()

    def _select_date(self, day):
        selected_date = date(
            self.current_year,
            self.current_month,
            day,
        )

        self.selected_date = selected_date

        if self.on_selected:
            self.on_selected(selected_date)

        self.destroy()