from tests.base_test import BaseDatabaseTest
from services import account_service, category_service, transaction_service


class TransactionServiceTest(BaseDatabaseTest):
    def test_create_and_retrieve_transaction(self):
        account = account_service.create_account("Cash", "CASH")
        category = category_service.create_category("Food", "EXPENSE")
        tid = transaction_service.create_transaction("2026-10-01", "Groceries", "EXPENSE", category, [(account, -1500)])
        transaction, entries = transaction_service.get_transaction_by_id(tid)
        self.assertEqual(transaction[2:4], ("Groceries", "EXPENSE"))
        self.assertEqual(entries[0][2], -1500)

    def test_balance_and_transfer(self):
        cash = account_service.create_account("Cash", "CASH")
        bank = account_service.create_account("Bank", "BANK")
        transaction_service.create_transaction("2026-10-01", "Income", "INCOME", None, [(cash, 5000)])
        transaction_service.create_transaction("2026-10-02", "Transfer", "TRANSFER", None, [(cash, -2000), (bank, 2000)])
        self.assertEqual(transaction_service.get_account_balance(cash), 3000)
        self.assertEqual(transaction_service.get_account_balance(bank), 2000)

    def test_invalid_account_rolls_back_transaction(self):
        account = account_service.create_account("Cash", "CASH")
        before = len(transaction_service.get_transactions())
        with self.assertRaises(Exception):
            transaction_service.create_transaction("2026-10-01", "Invalid", "EXPENSE", None, [(account, -100), (999999, 100)])
        self.assertEqual(len(transaction_service.get_transactions()), before)
        self.assertEqual(transaction_service.get_account_balance(account), 0)
