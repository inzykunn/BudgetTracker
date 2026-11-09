import customtkinter as ctk
from database.connection import get_connection
from GUI.components.cards import Cards
from GUI.components.quick_action_buttons import QuickActionButtons
from GUI.components.tables import Tables
from GUI.styles.colors import CONTENT,TEXT_DARK,SUCCESS,DANGER,PANEL,PANEL_HOVER
from GUI.styles.theme import CONTENT_PAD_X,CONTENT_PAD_Y,PANEL_RADIUS,BUTTON_RADIUS,FONT_SECTION,FONT_BODY_BOLD

class DashboardPage(ctk.CTkFrame):
    def __init__(self,master,navigate):
        super().__init__(master,corner_radius=0,fg_color=CONTENT)
        self.navigate=navigate
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        self._build_summary()
        self._build_recent_transactions()
        self._build_quick_actions()
        self.refresh()

    def _build_summary(self):
        self.summary=Cards(self,[{"key":"income","title":"TOTAL INCOME","value":"₱0.00"},{"key":"expenses","title":"TOTAL EXPENSES","value":"₱0.00"},{"key":"balance","title":"NET BALANCE","value":"₱0.00"}])
        self.summary.grid(row=0,column=0,sticky="ew",padx=CONTENT_PAD_X,pady=(CONTENT_PAD_Y,10))

    def _build_recent_transactions(self):
        self.activity=ctk.CTkFrame(self,fg_color=PANEL,corner_radius=PANEL_RADIUS)
        self.activity.grid(row=1,column=0,sticky="nsew",padx=CONTENT_PAD_X,pady=(0,10))
        self.activity.grid_columnconfigure(0,weight=1)
        self.activity.grid_rowconfigure(1,weight=1)
        heading=ctk.CTkFrame(self.activity,fg_color="transparent")
        heading.grid(row=0,column=0,sticky="ew",padx=20,pady=(15,10))
        heading.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(heading,text="Recent Transactions",font=FONT_SECTION,text_color=TEXT_DARK).grid(row=0,column=0,sticky="w")
        ctk.CTkButton(heading,text="Refresh",width=90,height=30,corner_radius=BUTTON_RADIUS,fg_color=PANEL_HOVER,hover_color=CONTENT,text_color=TEXT_DARK,font=FONT_BODY_BOLD,command=self.refresh).grid(row=0,column=1,sticky="e")
        self.transaction_table=Tables(self.activity,columns=[{"label":"DATE","weight":1,"minsize":110},{"label":"DESCRIPTION","weight":3,"minsize":180},{"label":"TYPE","weight":1,"minsize":120},{"label":"AMOUNT","weight":1,"minsize":130,"anchor":"e"}],empty_text="No recent transactions")
        self.transaction_table.grid(row=1,column=0,sticky="nsew",padx=18,pady=(0,18))

    def _build_quick_actions(self):
        actions=QuickActionButtons(self,[("Add Income",lambda:self.navigate("Add Income")),("Add Expense",lambda:self.navigate("Add Expense")),("Transfer",lambda:self.navigate("Transfer")),("Manage Accounts",lambda:self.navigate("Accounts")),("View Reports",lambda:self.navigate("Reports"))])
        actions.grid(row=2,column=0,sticky="ew",padx=CONTENT_PAD_X-5,pady=(0,CONTENT_PAD_Y))

    def refresh(self):
        income,expenses,balance,transactions=self._get_dashboard_data()
        self.summary.set_values({"income":self._money(income),"expenses":self._money(expenses),"balance":self._money(balance)})
        self.transaction_table.clear()
        for transaction in transactions:
            transaction_date,description,transaction_type,amount=transaction
            amount_text=self._signed_money(transaction_type,amount)
            cell_styles={2:{"font":FONT_BODY_BOLD,"text_color":self._type_color(transaction_type)},3:{"font":FONT_BODY_BOLD,"text_color":self._amount_color(transaction_type)}}
            self.transaction_table.add_row(values=(transaction_date,description,transaction_type.replace("_"," "),amount_text),cell_styles=cell_styles)

    @staticmethod
    def _type_color(transaction_type):
        if transaction_type=="INCOME":
            return SUCCESS
        if transaction_type in {"EXPENSE","RECEIVABLE","LIABILITY_PAYMENT"}:
            return DANGER
        return TEXT_DARK

    @staticmethod
    def _amount_color(transaction_type):
        if transaction_type=="INCOME":
            return SUCCESS
        if transaction_type in {"EXPENSE","RECEIVABLE","LIABILITY_PAYMENT"}:
            return DANGER
        return TEXT_DARK

    @staticmethod
    def _money(amount):
        return f"₱{(amount or 0)/100:,.2f}"

    @classmethod
    def _signed_money(cls,transaction_type,amount):
        value=cls._money(abs(amount or 0))
        if transaction_type in {"EXPENSE","RECEIVABLE","LIABILITY_PAYMENT"}:
            return f"- {value}"
        return f"+ {value}"

    @staticmethod
    def _get_dashboard_data():
        connection=get_connection()
        try:
            income=connection.execute("""SELECT COALESCE(SUM(te.amount),0) FROM transactions AS t JOIN transaction_entries AS te ON te.transaction_id=t.id WHERE t.type='INCOME'""").fetchone()[0]
            expenses=connection.execute("""SELECT COALESCE(SUM(ABS(te.amount)),0) FROM transactions AS t JOIN transaction_entries AS te ON te.transaction_id=t.id WHERE t.type='EXPENSE'""").fetchone()[0]
            balance=connection.execute("""SELECT COALESCE(SUM(amount),0) FROM transaction_entries""").fetchone()[0]
            recent=connection.execute("""SELECT t.date,t.description,t.type,CASE WHEN t.type='TRANSFER' THEN MAX(ABS(te.amount)) ELSE SUM(ABS(te.amount)) END AS display_amount FROM transactions AS t LEFT JOIN transaction_entries AS te ON te.transaction_id=t.id GROUP BY t.id ORDER BY t.date DESC,t.id DESC LIMIT 8""").fetchall()
            return income,expenses,balance,recent
        finally:
            connection.close()
