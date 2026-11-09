import customtkinter as ctk
from GUI.styles.colors import CONTENT,PANEL,PANEL_HOVER,TEXT_DARK,TEXT_MUTED
from GUI.styles.theme import PANEL_RADIUS,TABLE_ROW_HEIGHT,TABLE_CELL_PAD_X,FONT_BODY,FONT_SMALL_BOLD

class Tables(ctk.CTkFrame):
    def __init__(self,master,columns,empty_text="No data to display",on_double_click=None):
        super().__init__(master,fg_color=PANEL,corner_radius=PANEL_RADIUS)
        self.columns=columns
        self.empty_text=empty_text
        self.on_double_click=on_double_click
        self.rows=[]
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self._build_header()
        self._build_body()

    def _build_header(self):
        self.header=ctk.CTkFrame(self,fg_color=PANEL_HOVER,corner_radius=10,height=42)
        self.header.grid(row=0,column=0,sticky="ew",padx=1,pady=(1,6))
        self.header.grid_propagate(False)
        for index,column in enumerate(self.columns):
            self.header.grid_columnconfigure(index,weight=column.get("weight",1),minsize=column.get("minsize",0))
            ctk.CTkLabel(self.header,text=column["label"],font=FONT_SMALL_BOLD,text_color=TEXT_DARK,anchor=column.get("anchor","w")).grid(row=0,column=index,sticky="ew",padx=TABLE_CELL_PAD_X,pady=8)

    def _build_body(self):
        self.body_container=ctk.CTkFrame(self,fg_color=PANEL,corner_radius=12)
        self.body_container.grid(row=1,column=0,sticky="nsew",padx=1,pady=(0,1))
        self.body_container.grid_columnconfigure(0,weight=1)
        self.body_container.grid_rowconfigure(0,weight=1)
        self.body=ctk.CTkScrollableFrame(self.body_container,fg_color=CONTENT,corner_radius=10,scrollbar_button_color=PANEL_HOVER,scrollbar_button_hover_color=TEXT_DARK)
        self.body.grid(row=0,column=0,sticky="nsew",padx=4,pady=4)
        self.body.grid_columnconfigure(0,weight=1)
        self.empty_label=ctk.CTkLabel(self.body,text=self.empty_text,font=FONT_BODY,text_color=TEXT_MUTED)
        self.empty_label.pack(pady=55)

    def clear(self):
        for row in self.rows:
            row.destroy()
        self.rows.clear()
        self.empty_label.configure(text=self.empty_text)
        self.empty_label.pack(pady=55)

    def add_row(self,values,row_id=None,cell_styles=None):
        self.empty_label.pack_forget()
        row_index=len(self.rows)
        background=PANEL if row_index%2==0 else CONTENT
        row=ctk.CTkFrame(self.body,fg_color=background,corner_radius=8,height=TABLE_ROW_HEIGHT+10)
        row.pack(fill="x",padx=(2,18),pady=(0,5))
        row.pack_propagate(False)
        for index,column in enumerate(self.columns):
            row.grid_columnconfigure(index,weight=column.get("weight",1),minsize=column.get("minsize",0))
        for index,value in enumerate(values):
            column=self.columns[index]
            style=cell_styles.get(index,{}) if cell_styles else {}
            label=ctk.CTkLabel(row,text=str(value),font=style.get("font",FONT_BODY),text_color=style.get("text_color",TEXT_DARK),fg_color=style.get("fg_color","transparent"),corner_radius=style.get("corner_radius",0),anchor=column.get("anchor","w"))
            label.grid(row=0,column=index,sticky="ew",padx=TABLE_CELL_PAD_X,pady=7)
            self._bind_hover(label,row,background)
            if self.on_double_click and row_id is not None:
                label.bind("<Double-1>",lambda event,value=row_id:self.on_double_click(value))
        if self.on_double_click and row_id is not None:
            row.bind("<Double-1>",lambda event,value=row_id:self.on_double_click(value))
        self.rows.append(row)

    def _bind_hover(self,label,row,original_background):
        def enter(_event):
            row.configure(fg_color=PANEL_HOVER)
        def leave(_event):
            row.configure(fg_color=original_background)
        label.bind("<Enter>",enter,add="+")
        label.bind("<Leave>",leave,add="+")
        row.bind("<Enter>",enter,add="+")
        row.bind("<Leave>",leave,add="+")

    def set_rows(self,rows):
        self.clear()
        for row in rows:
            self.add_row(values=row.get("values",[]),row_id=row.get("id"),cell_styles=row.get("cell_styles"))

    def show_empty(self,text=None):
        self.clear()
        if text:
            self.empty_label.configure(text=text)
        self.empty_label.pack(pady=55)
