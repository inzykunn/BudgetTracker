import tkinter as tk
from tkinter import messagebox


def show_success(parent, title="Success", message="Operation completed successfully."):
    messagebox.showinfo(title, message, parent=parent)


def show_error(parent, title="Error", message="An error occurred."):
    messagebox.showerror(title, message, parent=parent)


def show_warning(parent, title="Warning", message="Please check the information provided."):
    messagebox.showwarning(title, message, parent=parent)


def show_info(parent, title="Information", message=""):
    messagebox.showinfo(title, message, parent=parent)


def confirm(parent, title="Confirm", message="Are you sure?"):
    return messagebox.askyesno(title, message, parent=parent)


def confirm_delete(parent, item_name="this item"):
    return messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete {item_name}?",
        parent=parent
    )


def confirm_action(parent, action, item_name="this item"):
    return messagebox.askyesno(
        f"Confirm {action}",
        f"Are you sure you want to {action.lower()} {item_name}?",
        parent=parent
    )


def show_validation_error(parent, message):
    messagebox.showerror("Validation Error", message, parent=parent)


def show_operation_error(parent, operation, error):
    messagebox.showerror(
        f"{operation} Failed",
        f"Unable to {operation.lower()}.\n\n{error}",
        parent=parent
    )


def show_save_success(parent, item_name="item"):
    show_success(
        parent,
        "Saved",
        f"{item_name} has been saved successfully."
    )


def show_update_success(parent, item_name="item"):
    show_success(
        parent,
        "Updated",
        f"{item_name} has been updated successfully."
    )


def show_delete_success(parent, item_name="item"):
    show_success(
        parent,
        "Deleted",
        f"{item_name} has been deleted successfully."
    )


def show_create_success(parent, item_name="item"):
    show_success(
        parent,
        "Created",
        f"{item_name} has been created successfully."
    )


def show_empty(parent, item_name="records"):
    show_info(
        parent,
        "No Records",
        f"No {item_name} found."
    )