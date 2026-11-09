import customtkinter as ctk

from GUI.components.header import Header
from GUI.components.sidebar import Sidebar
from GUI.pages.dashboard import DashboardPage
from GUI.pages.placeholder import PlaceholderPage
from GUI.pages.transactions import TransactionsPage
from GUI.pages.accounts import AccountsPage
from GUI.pages.categories import CategoriesPage
from GUI.pages.assets import AssetsPage
from GUI.pages.inventory import InventoryPage
from GUI.pages.receivables import ReceivablesPage
from GUI.pages.liabilities import LiabilitiesPage
from GUI.pages.transfer import TransferPage
from GUI.pages.reports import ReportsPage
from GUI.styles.colors import BG, CONTENT



class BudgetTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Budget Tracker")
        self.geometry("1180x820")
        self.minsize(900, 650)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_container()
        self.navigate("Dashboard")

    def create_sidebar(self):
        self.sidebar = Sidebar(self, self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

    def create_main_container(self):
        self.main_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=CONTENT,
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.header = Header(self.main_area)
        self.header.grid(row=0, column=0, sticky="ew")

        self.page_container = ctk.CTkFrame(
            self.main_area,
            corner_radius=0,
            fg_color=CONTENT,
        )
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def navigate(self, page_name):
        for widget in self.page_container.winfo_children():
            widget.destroy()

        self.header.set_title(page_name)

        if page_name == "Dashboard":
            page = DashboardPage(self.page_container, self.navigate)
        elif page_name == "Transactions":
            page = TransactionsPage(self.page_container, self.navigate)
        elif page_name == "Add Income":
            page = TransactionsPage(self.page_container, self.navigate)
            page.after(50, lambda: page._open_form("INCOME"))
        elif page_name == "Add Expense":
            page = TransactionsPage(self.page_container, self.navigate)
            page.after(50, lambda: page._open_form("EXPENSE"))
        elif page_name == "Accounts":
            page = AccountsPage(self.page_container, self.navigate)
        elif page_name == "Categories":
            page = CategoriesPage(self.page_container, self.navigate)
        elif page_name == "Assets":
            page = AssetsPage(self.page_container, self.navigate)
        elif page_name == "Inventory":
            page = InventoryPage(self.page_container, self.navigate)
        elif page_name == "Receivables":
            page = ReceivablesPage(self.page_container, self.navigate)
        elif page_name == "Liabilities":
            page = LiabilitiesPage(self.page_container, self.navigate)
        elif page_name == "Transfer":
            page = TransferPage(self.page_container, self.navigate)
        elif page_name == "Reports":
            page = ReportsPage(self.page_container, self.navigate)
        else:
            page = PlaceholderPage(self.page_container, page_name)

        page.grid(row=0, column=0, sticky="nsew")


def run():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    app = BudgetTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    run()