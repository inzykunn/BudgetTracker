import customtkinter as ctk

from GUI.styles.colors import SIDEBAR, PANEL_HOVER, TEXT_LIGHT, TEXT_MUTED
from GUI.styles.theme import (
    SIDEBAR_WIDTH,
    SIDEBAR_BRAND_PAD_X,
    SIDEBAR_BRAND_PAD_Y,
    SIDEBAR_BRAND_BOTTOM,
    SIDEBAR_BUTTON_HEIGHT,
    SIDEBAR_BUTTON_PAD_X,
    SIDEBAR_BUTTON_PAD_Y,
    SIDEBAR_BOTTOM_PAD_X,
    SIDEBAR_BOTTOM_PAD_Y,
    FONT_TITLE,
    FONT_NAV,
    FONT_SMALL_BOLD,
    BUTTON_RADIUS,
)


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, navigate):
        super().__init__(
            master,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=SIDEBAR,
        )
        self.grid_propagate(False)

        ctk.CTkLabel(
            self,
            text="BUDGET\nTRACKER",
            font=FONT_TITLE,
            text_color=TEXT_LIGHT,
            justify="left",
        ).pack(
            anchor="w",
            padx=SIDEBAR_BRAND_PAD_X,
            pady=(SIDEBAR_BRAND_PAD_Y, SIDEBAR_BRAND_BOTTOM),
        )

        pages = (
            "Dashboard",
            "Transactions",
            "Accounts",
            "Categories",
            "Assets",
            "Inventory",
            "Receivables",
            "Liabilities",
        )

        for page in pages:
            ctk.CTkButton(
                self,
                text=page,
                anchor="w",
                height=SIDEBAR_BUTTON_HEIGHT,
                corner_radius=BUTTON_RADIUS,
                fg_color="transparent",
                hover_color=PANEL_HOVER,
                text_color=TEXT_LIGHT,
                font=FONT_NAV,
                command=lambda name=page: navigate(name),
            ).pack(
                fill="x",
                padx=SIDEBAR_BUTTON_PAD_X,
                pady=SIDEBAR_BUTTON_PAD_Y,
            )

        ctk.CTkLabel(
            self,
            text="PERSONAL FINANCE",
            text_color=TEXT_MUTED,
            font=FONT_SMALL_BOLD,
        ).pack(
            side="bottom",
            anchor="w",
            padx=SIDEBAR_BOTTOM_PAD_X,
            pady=SIDEBAR_BOTTOM_PAD_Y,
        )
