import customtkinter as ctk
from GUI.styles.colors import PANEL,TEXT_DARK
from GUI.styles.theme import PANEL_RADIUS,FONT_STAT_LABEL,FONT_STAT_VALUE

class Cards(ctk.CTkFrame):
    def __init__(self,master,cards):
        super().__init__(master,fg_color="transparent",corner_radius=0)
        self.values={}
        for column in range(len(cards)):
            self.grid_columnconfigure(column,weight=1)
        for column,card in enumerate(cards):
            frame=ctk.CTkFrame(self,fg_color=PANEL,corner_radius=PANEL_RADIUS,height=88)
            frame.grid(row=0,column=column,sticky="ew",padx=5)
            frame.grid_propagate(False)
            frame.grid_columnconfigure(0,weight=1)
            frame.grid_rowconfigure((0,1),weight=1)
            ctk.CTkLabel(frame,text=card["title"],text_color=TEXT_DARK,font=FONT_STAT_LABEL,anchor="center").grid(row=0,column=0,sticky="ew",padx=20,pady=(8,0))
            value=ctk.CTkLabel(frame,text=card.get("value","₱0.00"),text_color=TEXT_DARK,font=FONT_STAT_VALUE,anchor="center")
            value.grid(row=1,column=0,sticky="ew",padx=20,pady=(0,8))
            self.values[card.get("key",card["title"])] = value

    def set_value(self,key,value):
        if key in self.values:
            self.values[key].configure(text=value)

    def set_values(self,values):
        for key,value in values.items():
            self.set_value(key,value)
