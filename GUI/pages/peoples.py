import customtkinter as ctk

from GUI.components.buttons import Buttons
from GUI.components.forms import FormWindow
from GUI.components.selectors import Selector
from GUI.components.tables import Tables
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
from services import people_service


class PeoplePage(ctk.CTkFrame):
    def __init__(self, master, navigate=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=CONTENT,
        )

        self.people = []
        self.selected_person_id = None

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
            text="People",
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
                    "label": "Add Person",
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
            height=40,
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
                {
                    "key": "notes",
                    "label": "NOTES",
                    "weight": 4,
                    "minsize": 220,
                },
            ],
            empty_text="No people yet",
            command=self._select_person,
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
            people = people_service.get_people()

            self.people = people

            rows = []

            for person in people:
                (
                    person_id,
                    name,
                    person_type,
                    notes,
                ) = person

                rows.append(
                    {
                        "id": person_id,
                        "name": name,
                        "type": person_type,
                        "notes": notes or "",
                    }
                )

            self.table.set_rows(rows)

            if self.selected_person_id is not None:
                if not any(
                    row["id"] == self.selected_person_id
                    for row in rows
                ):
                    self.selected_person_id = None

        except Exception as exc:
            show_operation_error(
                self,
                "Load People",
                exc,
            )

    def _select_person(self, person):
        if not person:
            return

        if isinstance(person, dict):
            self.selected_person_id = person.get("id")
        else:
            self.selected_person_id = person

    def _get_selected_person(self):
        if self.selected_person_id is None:
            return None

        try:
            person = people_service.get_person_by_id(
                self.selected_person_id
            )

        except Exception as exc:
            show_operation_error(
                self,
                "Load Person",
                exc,
            )
            return None

        if not person:
            show_warning(
                self,
                "Person Not Found",
                "The selected person no longer exists.",
            )
            self.selected_person_id = None
            self.refresh()
            return None

        return person

    def _get_rows(self):
        rows = self.table.get_rows()

        if not rows:
            show_warning(
                self,
                "No People",
                "There are no people available.",
            )
            return None

        return rows

    def _open_add(self):
        PersonForm(
            self,
            on_saved=self.refresh,
        )

    def _open_edit(self):
        selected = self._get_selected_person()

        if selected is not None:
            self._edit_selected(selected)
            return

        rows = self._get_rows()

        if rows is None:
            return

        Selector(
            self,
            title="Select Person",
            items=rows,
            display_key="name",
            value_key="id",
            description="Choose the person you want to edit.",
            select_button_text="Edit Person",
            on_selected=self._edit_selected,
        )

    def _edit_selected(self, person):
        if not person:
            return

        if isinstance(person, dict):
            person_id = person.get("id")

            try:
                selected = people_service.get_person_by_id(
                    person_id
                )

            except Exception as exc:
                show_operation_error(
                    self,
                    "Load Person",
                    exc,
                )
                return

        else:
            selected = person

        if not selected:
            show_warning(
                self,
                "Person Not Found",
                "The selected person no longer exists.",
            )
            self.selected_person_id = None
            self.refresh()
            return

        self.selected_person_id = selected[0]

        PersonForm(
            self,
            person=selected,
            on_saved=self.refresh,
        )


class PersonForm(FormWindow):
    def __init__(
        self,
        master,
        person=None,
        on_saved=None,
    ):
        self.person = person
        self.on_saved = on_saved

        super().__init__(
            master,
            "Edit Person"
            if person
            else "Add Person",
            width=560,
            height=560,
        )

        self._build()

    def _build(self):
        self.add_description(
            "Enter the person details below."
        )

        self.name_entry = self.add_field(
            "Name",
            (
                self.person[1]
                if self.person
                else ""
            ),
        )

        type_values = [
            "Individual",
            "Business",
            "Organization",
        ]

        self.type_selector = self.add_selector(
            "Type",
            type_values,
            value=(
                self.person[2]
                if self.person
                else "Individual"
            ),
        )

        self.notes_entry = self.add_field(
            "Notes",
            (
                self.person[3]
                if self.person and self.person[3]
                else ""
            ),
        )

        self.add_buttons(
            save_text=(
                "Save Changes"
                if self.person
                else "Save Person"
            ),
            save_command=self._save,
        )

    def _validate(self):
        try:
            name = validate_length(
                require_text(
                    self.name_entry.get(),
                    "Name",
                ),
                "Name",
                min_length=1,
                max_length=100,
            )

            person_type = validate_length(
                require_text(
                    self.type_selector.get(),
                    "Type",
                ),
                "Type",
                min_length=1,
                max_length=50,
            )

            notes = self.notes_entry.get().strip()

            if notes:
                notes = validate_length(
                    notes,
                    "Notes",
                    max_length=500,
                )
            else:
                notes = None

            return (
                name,
                person_type,
                notes,
            )

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

        (
            name,
            person_type,
            notes,
        ) = values

        try:
            if self.person:
                people_service.update_person(
                    self.person[0],
                    name,
                    person_type,
                    notes,
                )

                show_update_success(
                    self,
                    "Person",
                )

            else:
                people_service.create_person(
                    name,
                    person_type,
                    notes,
                )

                show_save_success(
                    self,
                    "Person",
                )

        except Exception as exc:
            show_operation_error(
                self,
                "Save Person",
                exc,
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()