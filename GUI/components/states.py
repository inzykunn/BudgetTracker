import tkinter as tk
from tkinter import ttk


class LoadingState(ttk.Frame):
    def __init__(self, parent, message="Loading...", **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = ttk.Label(
            self,
            text=message,
            anchor="center"
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

    def set_message(self, message):
        self.label.configure(text=message)


class EmptyState(ttk.Frame):
    def __init__(self, parent, message="No records found.", **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = ttk.Label(
            self,
            text=message,
            anchor="center"
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

    def set_message(self, message):
        self.label.configure(text=message)


class ErrorState(ttk.Frame):
    def __init__(self, parent, message="Unable to load data.", retry_command=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self)
        container.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

        container.columnconfigure(0, weight=1)

        self.label = ttk.Label(
            container,
            text=message,
            anchor="center",
            wraplength=400
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )

        self.retry_button = None

        if retry_command:
            self.retry_button = ttk.Button(
                container,
                text="Retry",
                command=retry_command
            )
            self.retry_button.grid(
                row=1,
                column=0
            )

    def set_message(self, message):
        self.label.configure(text=message)


class SuccessState(ttk.Frame):
    def __init__(self, parent, message="Operation completed successfully.", **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = ttk.Label(
            self,
            text=message,
            anchor="center"
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20
        )

    def set_message(self, message):
        self.label.configure(text=message)


class StateContainer(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.current_state = None

    def show(self, widget):
        if self.current_state is not None:
            self.current_state.grid_forget()

        self.current_state = widget
        self.current_state.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def clear(self):
        if self.current_state is not None:
            self.current_state.grid_forget()
            self.current_state = None