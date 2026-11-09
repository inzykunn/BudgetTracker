import customtkinter as ctk

from GUI.styles.colors import CONTENT, PANEL, TEXT_DARK
from GUI.styles.theme import CONTENT_PAD_X, CONTENT_PAD_Y, PANEL_RADIUS, FONT_PAGE_TITLE, FONT_BODY


class PlaceholderPage(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, corner_radius=0, fg_color=CONTENT)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=PANEL_RADIUS)
        panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=CONTENT_PAD_Y,
        )

        ctk.CTkLabel(
            panel,
            text=title,
            text_color=TEXT_DARK,
            font=FONT_PAGE_TITLE,
        ).pack(anchor="w", padx=24, pady=(22, 8))

        ctk.CTkLabel(
            panel,
            text="This screen will be built in its own page module.",
            text_color=TEXT_DARK,
            font=FONT_BODY,
        ).pack(anchor="w", padx=24, pady=12)
