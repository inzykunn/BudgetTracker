import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database import connection as db_connection
from services import account_service, asset_service, category_service, credit_service
from services import finance_service, inventory_service, liability_service
from services import people_service, receivable_service, transaction_service

SERVICE_MODULES = [
    account_service, asset_service, category_service, credit_service,
    finance_service, inventory_service, liability_service,
    people_service, receivable_service, transaction_service,
]


class BudgetServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "budget.db"
        source = Path(db_connection.DATABASE_PATH)
        if not source.exists():
            raise FileNotFoundError(f"Database not found: {source}. Run this test from the project containing data/budget.db.")
        source_conn = sqlite3.connect(source)
        dest_conn = sqlite3.connect(self.db_path)
        source_conn.backup(dest_conn)
        source_conn.close()
        dest_conn.close()

        def test_connection():
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        self.patches = [patch.object(m, "get_connection", side_effect=test_connection) for m in SERVICE_MODULES if hasattr(m, "get_connection")]
        for p in self.patches:
            p.start()

        # Clean copied DB so every test is deterministic and does not depend on existing data.
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = OFF")
        for table in [
            "transaction_entries", "transactions", "receivable_payments", "receivables",
            "liability_payments", "liabilities", "inventory_items", "assets",
            "credit_accounts", "categories", "people", "accounts",
        ]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def test_accounts_people_categories_and_credit(self):
        a = account_service.create_account("Test Cash", "CASH")
        self.assertEqual(a, account_service.get_account_by_name("Test Cash")[0])
        self.assertEqual(a, account_service.create_account("Test Cash", "CASH"))
        account_service.update_account(a, "Test Wallet", "CASH")
        self.assertEqual("Test Wallet", account_service.get_account_by_id(a)[1])
        account_service.deactivate_account(a)
        self.assertEqual(0, account_service.get_account_by_id(a)[3])

        p = people_service.create_person("Test Person", "CUSTOMER", "notes")
        self.assertEqual(p, people_service.get_person_by_name("Test Person")[0])
        self.assertEqual(p, people_service.create_person("Test Person", "CUSTOMER"))
        people_service.update_person(p, "Updated Person", "CUSTOMER")
        self.assertEqual("Updated Person", people_service.get_person_by_id(p)[1])

        c = category_service.create_category("Food", "EXPENSE")
        self.assertEqual(c, category_service.get_category_by_name("Food")[0])
        self.assertEqual(c, category_service.create_category("Food", "EXPENSE"))

        cr = credit_service.create_credit_account("Test Card", 100000)
        self.assertEqual(cr, credit_service.create_credit_account("Test Card", 100000))
        credit_service.update_credit_account(cr, "Updated Card", 120000)
        self.assertEqual("Updated Card", credit_service.get_credit_account_by_id(cr)[1])
        credit_service.deactivate_credit_account(cr)
        self.assertEqual(0, credit_service.get_credit_account_by_id(cr)[3])

    def test_transactions_and_finance_balance(self):
        account = account_service.create_account("Cash", "CASH")
        cat = category_service.create_category("Salary", "INCOME")
        tid = finance_service.record_income("2026-10-01", "Salary", account, 50000, cat)
        self.assertEqual(50000, transaction_service.get_account_balance(account))
        transaction, entries = transaction_service.get_transaction_by_id(tid)
        self.assertEqual("INCOME", transaction[3])
        self.assertEqual([(entries[0][1], entries[0][2])], [(account, 50000)])

        bank = account_service.create_account("Bank", "CASH")
        transfer_id = finance_service.record_transfer("2026-10-02", "Move", account, bank, 10000)
        self.assertEqual(40000, transaction_service.get_account_balance(account))
        self.assertEqual(10000, transaction_service.get_account_balance(bank))
        self.assertTrue(transaction_service.get_transaction_by_id(transfer_id)[0])

        finance_service.record_expense("2026-10-03", "Food", account, 2500, cat)
        self.assertEqual(37500, transaction_service.get_account_balance(account))

    def test_asset_lifecycle(self):
        account = account_service.create_account("Cash", "CASH")
        tid, asset = asset_service.buy_asset("2026-10-01", "Laptop", account, "Laptop", "Electronics", 30000, "2026-10-01")
        self.assertEqual(-30000, transaction_service.get_account_balance(account))
        self.assertEqual("ACTIVE", asset_service.get_asset_by_id(asset)[6])
        asset_service.update_asset_value(asset, 28000)
        self.assertEqual(28000, asset_service.get_asset_by_id(asset)[4])
        tid2, profit = asset_service.sell_asset("2026-10-05", "Sell Laptop", account, asset, 32000, "2026-10-05")
        self.assertEqual(4000, profit)
        self.assertEqual(2000, transaction_service.get_account_balance(account))
        with self.assertRaises(ValueError):
            asset_service.sell_asset("2026-10-06", "Again", account, asset, 1, "2026-10-06")

        disposable = asset_service.create_asset("Old Phone", "Electronics", 5000, 5000, "2026-10-01")
        asset_service.dispose_asset(disposable)
        self.assertEqual("DISPOSED", asset_service.get_asset_by_id(disposable)[6])
        with self.assertRaises(ValueError):
            asset_service.dispose_asset(disposable)

    def test_inventory_lifecycle(self):
        account = account_service.create_account("Cash", "CASH")
        tid, item = inventory_service.buy_inventory("2026-10-01", "Buy Item", account, "Item", 10000, "2026-10-01")
        self.assertEqual(-10000, transaction_service.get_account_balance(account))
        tid2, profit = inventory_service.sell_inventory("2026-10-03", "Sell Item", account, item, 15000, "2026-10-03")
        self.assertEqual(5000, profit)
        self.assertEqual(5000, transaction_service.get_account_balance(account))
        self.assertEqual(5000, inventory_service.calculate_inventory_profit(item))
        with self.assertRaises(ValueError):
            inventory_service.sell_inventory("2026-10-04", "Again", account, item, 1, "2026-10-04")
        with self.assertRaises(ValueError):
            inventory_service.sell_inventory("2026-10-04", "Bad", account, 999999, 1, "2026-10-04")

    def test_receivable_lifecycle_and_overpayment(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Customer", "CUSTOMER")
        tid, rid = receivable_service.record_receivable("2026-10-01", "Loan", account, person, 10000, "2026-10-15")
        self.assertEqual(-10000, transaction_service.get_account_balance(account))
        self.assertEqual(10000, receivable_service.get_receivable_balance(rid))
        pay_tid = receivable_service.record_receivable_payment("2026-10-05", "Payment", account, rid, 4000)
        self.assertEqual(6000, receivable_service.get_receivable_balance(rid))
        receivable_service.record_receivable_payment("2026-10-10", "Final", account, rid, 6000)
        self.assertEqual(0, receivable_service.get_receivable_balance(rid))
        self.assertEqual("PAID", receivable_service.get_receivable_by_id(rid)[6])
        with self.assertRaises(ValueError):
            receivable_service.record_receivable_payment("2026-10-11", "Over", account, rid, 1)

    def test_liability_lifecycle_and_overpayment(self):
        account = account_service.create_account("Cash", "CASH")
        tid, lid = liability_service.record_liability("2026-10-01", "Debt", account, 10000)
        self.assertEqual(10000, transaction_service.get_account_balance(account))
        self.assertEqual(10000, liability_service.get_liability_balance(lid))
        liability_service.record_liability_payment("2026-10-05", "Payment", account, lid, 4000)
        self.assertEqual(6000, liability_service.get_liability_balance(lid))
        liability_service.record_liability_payment("2026-10-10", "Final", account, lid, 6000)
        self.assertEqual(0, liability_service.get_liability_balance(lid))
        self.assertEqual("PAID", liability_service.get_liability_by_id(lid)[7])
        with self.assertRaises(ValueError):
            liability_service.record_liability_payment("2026-10-11", "Over", account, lid, 1)

    def test_transaction_rollback(self):
        account = account_service.create_account("Cash", "CASH")
        before = len(transaction_service.get_transactions())
        with self.assertRaises(sqlite3.IntegrityError):
            transaction_service.create_transaction("2026-10-01", "Broken", "EXPENSE", None, [(999999, -100)])
        self.assertEqual(before, len(transaction_service.get_transactions()))
        self.assertEqual(0, transaction_service.get_account_balance(account))


if __name__ == "__main__":
    unittest.main(verbosity=2)