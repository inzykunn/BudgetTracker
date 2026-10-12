from tests.base_test import BaseDatabaseTest
from services import account_service, finance_service, transaction_service


class FinanceServiceTest(BaseDatabaseTest):
    def test_record_income(self):
        account = account_service.create_account("Cash", "CASH")
        finance_service.record_income("2026-10-01", "Pay", account, 5000)
        self.assertEqual(transaction_service.get_account_balance(account), 5000)

    def test_record_expense(self):
        account = account_service.create_account("Cash", "CASH")
        finance_service.record_expense("2026-10-01", "Food", account, 1200)
        self.assertEqual(transaction_service.get_account_balance(account), -1200)

    def test_transfer(self):
        cash = account_service.create_account("Cash", "CASH")
        bank = account_service.create_account("Bank", "BANK")
        finance_service.record_income("2026-10-01", "Starting cash", cash, 5000)
        finance_service.record_transfer("2026-10-02", "Move money", cash, bank, 2000)
        self.assertEqual(transaction_service.get_account_balance(cash), 3000)
        self.assertEqual(transaction_service.get_account_balance(bank), 2000)
