import tkinter as tk
from tkinter import ttk


class FormPanel(ttk.Frame):
    def __init__(self, parent, title=None, padding=16, **kwargs):
        super().__init__(parent, padding=padding, **kwargs)

        self.columnconfigure(1, weight=1)

        self.row_index = 0

        if title:
            title_label = ttk.Label(
                self,
                text=title,
                font=("TkDefaultFont", 12, "bold")
            )
            title_label.grid(
                row=self.row_index,
                column=0,
                columnspan=2,
                sticky="w",
                pady=(0, 12)
            )
            self.row_index += 1

    def add_field(self, label, widget, required=False, **grid_kwargs):
        label_text = f"{label} *" if required else label

        ttk.Label(
            self,
            text=label_text
        ).grid(
            row=self.row_index,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=6
        )

        widget.grid(
            row=self.row_index,
            column=1,
            sticky="ew",
            pady=6,
            **grid_kwargs
        )

        self.row_index += 1

        return widget

    def add_widget(self, widget, columnspan=2, **grid_kwargs):
        widget.grid(
            row=self.row_index,
            column=0,
            columnspan=columnspan,
            sticky="ew",
            pady=6,
            **grid_kwargs
        )

        self.row_index += 1

        return widget

    def add_separator(self, **grid_kwargs):
        separator = ttk.Separator(self, orient="horizontal")

        separator.grid(
            row=self.row_index,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=10,
            **grid_kwargs
        )

        self.row_index += 1

        return separator

    def add_spacer(self, height=8):
        spacer = ttk.Frame(self, height=height)

        spacer.grid(
            row=self.row_index,
            column=0,
            columnspan=2,
            sticky="ew"
        )

        spacer.grid_propagate(False)

        self.row_index += 1

        return spacer


class FormField(ttk.Frame):
    def __init__(self, parent, label, widget_class=ttk.Entry, required=False, **widget_kwargs):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)

        label_text = f"{label} *" if required else label

        self.label = ttk.Label(
            self,
            text=label_text
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4)
        )

        self.widget = widget_class(
            self,
            **widget_kwargs
        )
        self.widget.grid(
            row=1,
            column=0,
            sticky="ew"
        )

    def get(self):
        if hasattr(self.widget, "get"):
            return self.widget.get()

        return None

    def set(self, value):
        if hasattr(self.widget, "delete") and hasattr(self.widget, "insert"):
            self.widget.delete(0, tk.END)
            self.widget.insert(0, value)
        elif hasattr(self.widget, "set"):
            self.widget.set(value)


class FormActions(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(
            row=0,
            column=0,
            sticky="e"
        )

    def add_button(self, text, command, default=False, **kwargs):
        button = ttk.Button(
            self.button_frame,
            text=text,
            command=command,
            **kwargs
        )

        button.pack(
            side="left",
            padx=(8, 0)
        )

        if default:
            button.focus_set()

        return button


class FormDialog(tk.Toplevel):
    def __init__(self, parent, title, width=500, height=400, **kwargs):
        super().__init__(parent)

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.form = FormPanel(
            self,
            padding=20,
            **kwargs
        )
        self.form.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.actions = FormActions(self)
        self.actions.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 20)
        )

    def close(self):
        self.grab_release()
        self.destroy()


def create_entry(parent, width=30, **kwargs):
    return ttk.Entry(
        parent,
        width=width,
        **kwargs
    )


def create_combobox(parent, values=None, width=30, state="readonly", **kwargs):
    return ttk.Combobox(
        parent,
        values=values or [],
        width=width,
        state=state,
        **kwargs
    )


def create_text(parent, width=30, height=4, **kwargs):
    return tk.Text(
        parent,
        width=width,
        height=height,
        wrap="word",
        **kwargs
    )


def create_checkbutton(parent, text, variable, **kwargs):
    return ttk.Checkbutton(
        parent,
        text=text,
        variable=variable,
        **kwargs
    )


def create_radiobutton(parent, text, variable, value, **kwargs):
    return ttk.Radiobutton(
        parent,
        text=text,
        variable=variable,
        value=value,
        **kwargs
    )