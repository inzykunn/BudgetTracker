from datetime import date
import customtkinter as ctk

from GUI.styles.colors import HEADER, TEXT_LIGHT, TEXT_MUTED
from GUI.styles.theme import HEADER_HEIGHT, HEADER_PAD_X, HEADER_PAD_Y, FONT_TITLE, FONT_BODY


class Header(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=HEADER_HEIGHT, corner_radius=0, fg_color=HEADER)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=FONT_TITLE,
            text_color=TEXT_LIGHT,
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=HEADER_PAD_X,
            pady=HEADER_PAD_Y,
        )

        ctk.CTkLabel(
            self,
            text=date.today().strftime("%B %d, %Y"),
            font=FONT_BODY,
            text_color=TEXT_MUTED,
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=HEADER_PAD_X,
        )

    def set_title(self, title):
        self.title_label.configure(text=title)
