import customtkinter as ctk

from services import category_service

from GUI.components.tables import Tables
from GUI.components.selectors import Selector
from GUI.components.forms import FormWindow
from GUI.components.buttons import Buttons

from GUI.styles.colors import (
    CONTENT,
    TEXT_DARK,
)

from GUI.styles.theme import (
    CONTENT_PAD_X,
    CONTENT_PAD_Y,
    FONT_PAGE_TITLE,
)

from GUI.utils.feedback import (
    show_warning,
    show_operation_error,
    show_save_success,
    show_update_success,
)

from GUI.utils.validation import (
    require_text,
    validate_length,
)


CATEGORY_TYPES = [
    "INCOME",
    "EXPENSE",
]


class CategoriesPage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.navigate = navigate

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build()
        self.refresh()

    def _build(self):
        self._build_header()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=CONTENT_PAD_X,
            pady=(CONTENT_PAD_Y, 12),
        )

        header.grid_columnconfigure(
            0,
            weight=1,
        )

        ctk.CTkLabel(
            header,
            text="Categories",
            font=FONT_PAGE_TITLE,
            text_color=TEXT_DARK,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.header_buttons = Buttons(
            header,
            actions=[
                {
                    "label": "Add Category",
                    "command": self._open_add,
                    "style": "primary",
                    "width": 140,
                    "height": 40,
                },
                {
                    "label": "Edit",
                    "command": self._open_edit,
                    "style": "default",
                    "width": 80,
                    "height": 40,
                },
                {
                    "label": "Refresh",
                    "command": self.refresh,
                    "style": "default",
                    "width": 90,
                    "height": 40,
                },
            ],
            columns=3,
            padx=3,
            pady=0,
        )

        self.header_buttons.grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _build_table(self):
        self.table = Tables(
            self,
            columns=[
                {
                    "key": "name",
                    "label": "NAME",
                    "weight": 3,
                    "minsize": 180,
                },
                {
                    "key": "type",
                    "label": "TYPE",
                    "weight": 2,
                    "minsize": 140,
                },
            ],
            empty_text="No categories yet",
            command=self._select_category,
        )

        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0, CONTENT_PAD_Y),
        )

    def refresh(self):
        try:
            categories = category_service.get_categories()

            rows = [
                {
                    "id": category[0],
                    "name": category[1],
                    "type": category[2],
                }
                for category in categories
            ]

            self.table.set_rows(rows)

        except Exception as exc:
            show_operation_error(
                self,
                "Load Categories",
                exc,
            )

    def _open_add(self):
        CategoryForm(
            self,
            on_saved=self.refresh,
        )

    def _open_edit(self):
        rows = self.table.get_rows()

        if not rows:
            show_warning(
                self,
                "No Categories",
                "There are no categories to edit.",
            )
            return

        Selector(
            self,
            title="Select Category",
            items=rows,
            display_key="name",
            value_key="id",
            description="Choose the category you want to edit.",
            select_button_text="Edit Category",
            on_selected=self._select_category,
        )

    def _select_category(self, category):
        if not category:
            return

        if isinstance(category, dict):
            category_id = category.get("id")
        else:
            category_id = category

        if category_id is None:
            return

        self._edit_selected(category_id)

    def _edit_selected(self, category_id):
        try:
            category = category_service.get_category_by_id(
                category_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Category",
                exc,
            )
            return

        if not category:
            show_warning(
                self,
                "Category Not Found",
                "The selected category no longer exists.",
            )
            self.refresh()
            return

        CategoryForm(
            self,
            category=category,
            on_saved=self.refresh,
        )


class CategoryForm(FormWindow):
    def __init__(
        self,
        master,
        category=None,
        on_saved=None,
    ):
        self.category = category
        self.on_saved = on_saved

        super().__init__(
            master,
            "Edit Category" if category else "Add Category",
            width=520,
            height=470,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Enter the category details below."
        )

        self.name_entry = self.add_field(
            "Name",
            (
                self.category[1]
                if self.category
                else ""
            ),
        )

        self.type_selector = self.add_selector(
            "Type",
            CATEGORY_TYPES,
            (
                self.category[2]
                if self.category
                else "EXPENSE"
            ),
        )

        self.add_buttons(
            save_text=(
                "Save Changes"
                if self.category
                else "Save Category"
            ),
            save_command=self._save,
        )

    def _validate(self):
        try:
            name = validate_length(
                require_text(
                    self.name_entry.get(),
                    "Category name",
                ),
                "Category name",
                min_length=1,
                max_length=100,
            )

            category_type = require_text(
                self.type_selector.get(),
                "Category type",
            )

            if category_type not in CATEGORY_TYPES:
                raise ValueError(
                    "Please select a valid category type."
                )

            return name, category_type

        except ValueError as exc:
            show_warning(
                self,
                "Validation Error",
                str(exc),
            )
            return None

    def _save(self):
        values = self._validate()

        if values is None:
            return

        name, category_type = values

        try:
            existing = category_service.get_category_by_name(
                name
            )

            if existing and (
                not self.category
                or existing[0] != self.category[0]
            ):
                show_warning(
                    self,
                    "Duplicate Category",
                    "A category with this name already exists.",
                )
                return

            if self.category:
                if (
                    name == self.category[1]
                    and category_type == self.category[2]
                ):
                    self.destroy()
                    return

                category_service.update_category(
                    self.category[0],
                    name,
                    category_type,
                )

                show_update_success(
                    self,
                    "Category",
                )

            else:
                category_service.create_category(
                    name,
                    category_type,
                )

                show_save_success(
                    self,
                    "Category",
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Category",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()