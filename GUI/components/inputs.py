import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
from datetime import datetime


class CurrencyEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        self.variable = kwargs.pop("textvariable", tk.StringVar())
        super().__init__(parent, textvariable=self.variable, **kwargs)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event=None):
        value = self.variable.get()
        if value.startswith("₱"):
            self.variable.set(value.replace("₱", "").replace(",", "").strip())

    def _on_focus_out(self, event=None):
        value = self.variable.get().strip()

        if not value:
            return

        try:
            amount = Decimal(value.replace("₱", "").replace(",", ""))
            if amount < 0:
                return

            self.variable.set(f"₱{amount:,.2f}")
        except (InvalidOperation, ValueError):
            pass

    def get_value(self):
        value = self.variable.get().strip()

        if not value:
            raise ValueError("Amount is required.")

        value = value.replace("₱", "").replace(",", "").strip()

        try:
            amount = Decimal(value)
        except InvalidOperation:
            raise ValueError("Invalid amount.")

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        return int(amount * 100)

    def set_value(self, cents):
        if cents is None:
            self.variable.set("")
            return

        amount = Decimal(str(cents)) / Decimal("100")
        self.variable.set(f"₱{amount:,.2f}")


class DateEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        self.variable = kwargs.pop("textvariable", tk.StringVar())
        super().__init__(parent, textvariable=self.variable, **kwargs)

        self.bind("<FocusOut>", self._validate_on_focus_out)

    def _validate_on_focus_out(self, event=None):
        value = self.variable.get().strip()

        if not value:
            return

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            self.configure(foreground="red")
            return

        self.configure(foreground="black")

    def get_value(self):
        value = self.variable.get().strip()

        if not value:
            raise ValueError("Date is required.")

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date. Use YYYY-MM-DD.")

    def set_value(self, value):
        if value is None:
            self.variable.set("")
            return

        if hasattr(value, "strftime"):
            self.variable.set(value.strftime("%Y-%m-%d"))
        else:
            self.variable.set(str(value))


class IDDropdown(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        self._items = []
        self._id_map = {}

        kwargs.setdefault("state", "readonly")

        super().__init__(parent, **kwargs)

        self.bind("<<ComboboxSelected>>", self._on_selected)

    def set_items(self, items, id_key=0, label_key=1):
        self._items = list(items)
        self._id_map.clear()

        labels = []

        for item in self._items:
            item_id = item[id_key]
            label = str(item[label_key])

            self._id_map[label] = item_id
            labels.append(label)

        self["values"] = labels

        if labels:
            self.current(0)
        else:
            self.set("")

    def _on_selected(self, event=None):
        return None

    def get_id(self):
        label = self.get().strip()

        if not label:
            raise ValueError("Selection is required.")

        if label not in self._id_map:
            raise ValueError("Invalid selection.")

        return self._id_map[label]

    def set_id(self, item_id):
        for label, value in self._id_map.items():
            if value == item_id:
                self.set(label)
                return

        self.set("")


class SearchEntry(ttk.Entry):
    def __init__(self, parent, command=None, delay=250, **kwargs):
        super().__init__(parent, **kwargs)

        self.command = command
        self.delay = delay
        self._after_id = None

        self.bind("<KeyRelease>", self._on_key_release)

    def _on_key_release(self, event=None):
        if self._after_id:
            self.after_cancel(self._after_id)

        if self.command:
            self._after_id = self.after(
                self.delay,
                self._run_command
            )

    def _run_command(self):
        self._after_id = None

        if self.command:
            self.command(self.get())


class NumericEntry(ttk.Entry):
    def __init__(self, parent, allow_decimal=False, **kwargs):
        self.allow_decimal = allow_decimal

        super().__init__(parent, **kwargs)

        self.variable = tk.StringVar()
        self.configure(textvariable=self.variable)

        self.variable.trace_add(
            "write",
            self._validate
        )

    def _validate(self, *args):
        value = self.variable.get()

        if value == "":
            return

        if self.allow_decimal:
            valid = value.replace(".", "", 1).isdigit()
        else:
            valid = value.isdigit()

        if not valid:
            self.variable.set(value[:-1])

    def get_value(self):
        value = self.variable.get().strip()

        if not value:
            raise ValueError("Value is required.")

        try:
            return float(value) if self.allow_decimal else int(value)
        except ValueError:
            raise ValueError("Invalid numeric value.")


class ReadOnlyEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, state="readonly", **kwargs)

    def set(self, value):
        self.configure(state="normal")
        self.delete(0, tk.END)
        self.insert(0, value)
        self.configure(state="readonly")