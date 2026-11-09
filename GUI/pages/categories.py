import customtkinter as ctk
from tkinter import messagebox
from services import category_service
from GUI.components.tables import Tables
from GUI.styles.colors import CONTENT,PANEL,PANEL_HOVER,TEXT_DARK,TEXT_LIGHT,INPUT_BG,INPUT_BORDER,SUCCESS,DANGER
from GUI.styles.theme import CONTENT_PAD_X,CONTENT_PAD_Y,PANEL_RADIUS,BUTTON_RADIUS,INPUT_RADIUS,FONT_SECTION,FONT_BODY,FONT_BODY_BOLD,FONT_FORM_LABEL,FONT_FORM_INPUT

class CategoriesPage(ctk.CTkFrame):
    def __init__(self,master,navigate=None):
        super().__init__(master,corner_radius=0,fg_color=CONTENT)
        self.navigate=navigate
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self._build_header()
        self._build_table()
        self.refresh()

    def _build_header(self):
        header=ctk.CTkFrame(self,fg_color="transparent")
        header.grid(row=0,column=0,sticky="ew",padx=CONTENT_PAD_X,pady=(CONTENT_PAD_Y,10))
        header.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(
            header,
            text="Categories",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).grid(row=0,column=0,sticky="w")
        ctk.CTkButton(
            header,
            text="Add Category",
            width=140,
            height=44,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL,
            hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self._open_add
        ).grid(row=0,column=1,sticky="e")

    def _build_table(self):
        panel=ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=PANEL_RADIUS
        )
        panel.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=CONTENT_PAD_X,
            pady=(0,CONTENT_PAD_Y)
        )
        panel.grid_columnconfigure(0,weight=1)
        panel.grid_rowconfigure(0,weight=1)

        self.table=Tables(
            panel,
            columns=[
                {"label":"NAME","weight":3,"minsize":180},
                {"label":"TYPE","weight":1,"minsize":130},
                {"label":"ACTIONS","weight":2,"minsize":180},
            ],
            empty_text="No categories yet"
        )
        self.table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=18
        )

    def refresh(self):
        try:
            categories=category_service.get_categories()
        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load categories.\n\n{exc}",
                parent=self
            )
            return

        self.table.clear()

        for category in categories:
            category_id,name,category_type=category
            type_color=SUCCESS if category_type.upper()=="INCOME" else DANGER
            self.table.add_row(
                values=(name,category_type,""),
                row_id=category_id,
                cell_styles={
                    1:{
                        "font":FONT_BODY_BOLD,
                        "text_color":type_color
                    }
                }
            )
            row=self.table.rows[-1]
            action_frame=ctk.CTkFrame(row,fg_color="transparent")
            action_frame.grid(row=0,column=2,sticky="e",padx=8,pady=5)
            ctk.CTkButton(
                action_frame,
                text="Edit",
                width=68,
                height=30,
                corner_radius=BUTTON_RADIUS,
                fg_color=PANEL_HOVER,
                hover_color=CONTENT,
                text_color=TEXT_DARK,
                font=FONT_BODY_BOLD,
                command=lambda category_id=category_id:self._open_edit(category_id)
            ).pack(side="left",padx=(0,5))
            ctk.CTkButton(
                action_frame,
                text="Delete",
                width=68,
                height=30,
                corner_radius=BUTTON_RADIUS,
                fg_color=DANGER,
                hover_color="#913E3E",
                text_color=TEXT_LIGHT,
                font=FONT_BODY_BOLD,
                command=lambda category_id=category_id:self._delete_category(category_id)
            ).pack(side="left")

    def _open_add(self):
        CategoryForm(
            self,
            on_saved=self.refresh
        )

    def _open_edit(self,category_id):
        try:
            category=category_service.get_category_by_id(category_id)
        except Exception as exc:
            messagebox.showerror(
                "Load Error",
                f"Unable to load the category.\n\n{exc}",
                parent=self
            )
            return

        if category:
            CategoryForm(
                self,
                category=category,
                on_saved=self.refresh
            )

class CategoryForm(ctk.CTkToplevel):
    def __init__(self,master,category=None,on_saved=None):
        super().__init__(master)
        self.category=category
        self.on_saved=on_saved
        self.title("Edit Category" if category else "Add Category")
        self.geometry("560x500")
        self.resizable(False,False)
        self.configure(fg_color=CONTENT)
        self.transient(master)
        self.grab_set()
        self._build()

    def _build(self):
        panel=ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=10
        )
        panel.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        ctk.CTkLabel(
            panel,
            text="Edit Category" if self.category else "Add Category",
            font=FONT_SECTION,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(24,4)
        )

        ctk.CTkLabel(
            panel,
            text="Enter the category details below.",
            font=FONT_BODY,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            padx=28,
            pady=(0,18)
        )

        self.name_entry=self._field(
            panel,
            "Name",
            self.category[1] if self.category else ""
        )

        type_wrapper=ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )
        type_wrapper.pack(
            fill="x",
            padx=28,
            pady=(0,14)
        )

        ctk.CTkLabel(
            type_wrapper,
            text="Type",
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0,5)
        )

        self.type_selector=ctk.CTkOptionMenu(
            type_wrapper,
            values=["INCOME","EXPENSE"],
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            button_color=INPUT_BORDER,
            button_hover_color=PANEL_HOVER,
            text_color=TEXT_DARK,
            dropdown_fg_color=PANEL,
            dropdown_hover_color=PANEL_HOVER,
            dropdown_text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )
        self.type_selector.pack(fill="x")

        if self.category:
            self.type_selector.set(self.category[2])
        else:
            self.type_selector.set("EXPENSE")

        button_row=ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )
        button_row.pack(
            fill="x",
            padx=28,
            pady=(20,24)
        )

        button_row.grid_columnconfigure(0,weight=1)
        button_row.grid_columnconfigure(1,weight=1)

        ctk.CTkButton(
            button_row,
            text="Cancel",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=PANEL_HOVER,
            hover_color=CONTENT,
            text_color=TEXT_DARK,
            font=FONT_BODY_BOLD,
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0,6)
        )

        ctk.CTkButton(
            button_row,
            text="Save Changes" if self.category else "Save Category",
            height=40,
            corner_radius=BUTTON_RADIUS,
            fg_color=TEXT_DARK,
            hover_color="#285B4B",
            text_color=TEXT_LIGHT,
            font=FONT_BODY_BOLD,
            command=self._save
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6,0)
        )

    def _field(self,parent,label,value):
        wrapper=ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        wrapper.pack(
            fill="x",
            padx=28,
            pady=(0,14)
        )

        ctk.CTkLabel(
            wrapper,
            text=label,
            font=FONT_FORM_LABEL,
            text_color=TEXT_DARK
        ).pack(
            anchor="w",
            pady=(0,5)
        )

        entry=ctk.CTkEntry(
            wrapper,
            height=36,
            corner_radius=INPUT_RADIUS,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=TEXT_DARK,
            font=FONT_FORM_INPUT
        )
        entry.pack(fill="x")

        if value:
            entry.insert(0,str(value))

        return entry

    def _save(self):
        name=self.name_entry.get().strip()
        category_type=self.type_selector.get().strip()

        if not name:
            messagebox.showwarning(
                "Missing Information",
                "Please enter a category name.",
                parent=self
            )
            return

        if category_type not in ("INCOME","EXPENSE"):
            messagebox.showwarning(
                "Invalid Type",
                "Please select a valid category type.",
                parent=self
            )
            return

        try:
            existing=category_service.get_category_by_name(name)

            if existing and (
                not self.category or existing[0]!=self.category[0]
            ):
                messagebox.showwarning(
                    "Duplicate Category",
                    "A category with this name already exists.",
                    parent=self
                )
                return

            if self.category:
                if name==self.category[1] and category_type==self.category[2]:
                    self.destroy()
                    return

                messagebox.showwarning(
                    "Edit Not Available",
                    "The category service does not provide an update operation.",
                    parent=self
                )
                return

            category_service.create_category(
                name,
                category_type
            )
        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Unable to save the category.\n\n{exc}",
                parent=self
            )
            return

        if self.on_saved:
            self.on_saved()

        self.destroy()