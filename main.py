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
    account_service,
    asset_service,
    category_service,
    credit_service,
    finance_service,
    inventory_service,
    liability_service,
    people_service,
    receivable_service,
    transaction_service,
]


class BudgetServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "budget.db"
        schema_path = Path(db_connection.BASE_DIR) / "database" / "schema.sql"

        if not schema_path.exists():
            self.tmp.cleanup()
            raise FileNotFoundError(f"Database schema not found: {schema_path}")

        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            conn.commit()
        except Exception:
            conn.close()
            self.tmp.cleanup()
            raise
        else:
            conn.close()

        def test_connection():
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

        self.patches = [
            patch.object(module, "get_connection", side_effect=test_connection)
            for module in SERVICE_MODULES
            if hasattr(module, "get_connection")
        ]

        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.tmp.cleanup()

    def test_accounts_people_categories_and_credit(self):
        account_id = account_service.create_account("Test Cash", "CASH")
        self.assertEqual(
            account_id,
            account_service.get_account_by_name("Test Cash")[0],
        )
        self.assertEqual(
            account_id,
            account_service.create_account("Test Cash", "CASH"),
        )

        account_service.update_account(account_id, "Test Wallet", "CASH")
        self.assertEqual(
            "Test Wallet",
            account_service.get_account_by_id(account_id)[1],
        )

        account_service.deactivate_account(account_id)
        self.assertEqual(0, account_service.get_account_by_id(account_id)[3])

        person_id = people_service.create_person(
            "Test Person",
            "CUSTOMER",
            "notes",
        )
        self.assertEqual(
            person_id,
            people_service.get_person_by_name("Test Person")[0],
        )
        self.assertEqual(
            person_id,
            people_service.create_person("Test Person", "CUSTOMER"),
        )

        people_service.update_person(person_id, "Updated Person", "CUSTOMER")
        self.assertEqual(
            "Updated Person",
            people_service.get_person_by_id(person_id)[1],
        )

        category_id = category_service.create_category("Food", "EXPENSE")
        self.assertEqual(
            category_id,
            category_service.get_category_by_name("Food")[0],
        )
        self.assertEqual(
            category_id,
            category_service.create_category("Food", "EXPENSE"),
        )

        credit_id = credit_service.create_credit_account("Test Card", 100000)
        self.assertEqual(
            credit_id,
            credit_service.create_credit_account("Test Card", 100000),
        )

        credit_service.update_credit_account(
            credit_id,
            "Updated Card",
            120000,
        )
        self.assertEqual(
            "Updated Card",
            credit_service.get_credit_account_by_id(credit_id)[1],
        )

        credit_service.deactivate_credit_account(credit_id)
        self.assertEqual(
            0,
            credit_service.get_credit_account_by_id(credit_id)[3],
        )

    def test_transactions_and_finance_balance(self):
        account_id = account_service.create_account("Cash", "CASH")
        income_category = category_service.create_category("Salary", "INCOME")

        transaction_id = finance_service.record_income(
            "2026-10-01",
            "Salary",
            account_id,
            50000,
            income_category,
        )

        self.assertEqual(
            50000,
            transaction_service.get_account_balance(account_id),
        )

        transaction, entries = transaction_service.get_transaction_by_id(
            transaction_id
        )
        self.assertEqual("INCOME", transaction[3])
        self.assertEqual(
            [(account_id, 50000)],
            [(entry[1], entry[2]) for entry in entries],
        )

        bank_id = account_service.create_account("Bank", "CASH")
        transfer_id = finance_service.record_transfer(
            "2026-10-02",
            "Move",
            account_id,
            bank_id,
            10000,
        )

        self.assertEqual(
            40000,
            transaction_service.get_account_balance(account_id),
        )
        self.assertEqual(
            10000,
            transaction_service.get_account_balance(bank_id),
        )
        self.assertTrue(
            transaction_service.get_transaction_by_id(transfer_id)[0]
        )

        expense_category = category_service.create_category("Food", "EXPENSE")
        finance_service.record_expense(
            "2026-10-03",
            "Food",
            account_id,
            2500,
            expense_category,
        )

        self.assertEqual(
            37500,
            transaction_service.get_account_balance(account_id),
        )

    def test_asset_lifecycle(self):
        account_id = account_service.create_account("Cash", "CASH")

        _, asset_id = asset_service.buy_asset(
            "2026-10-01",
            "Laptop",
            account_id,
            "Laptop",
            "Electronics",
            30000,
            "2026-10-01",
        )

        self.assertEqual(
            -30000,
            transaction_service.get_account_balance(account_id),
        )
        self.assertEqual("ACTIVE", asset_service.get_asset_by_id(asset_id)[6])

        asset_service.update_asset_value(asset_id, 28000, "2026-10-02")
        self.assertEqual(28000, asset_service.get_asset_by_id(asset_id)[4])

        _, profit = asset_service.sell_asset(
            "2026-10-05",
            "Sell Laptop",
            account_id,
            asset_id,
            32000,
            "2026-10-05",
        )

        self.assertEqual(4000, profit)
        self.assertEqual(
            2000,
            transaction_service.get_account_balance(account_id),
        )

        with self.assertRaises(ValueError):
            asset_service.sell_asset(
                "2026-10-06",
                "Again",
                account_id,
                asset_id,
                1,
                "2026-10-06",
            )

        disposable_id = asset_service.create_asset(
            "Old Phone",
            "Electronics",
            5000,
            5000,
            "2026-10-01",
        )
        asset_service.dispose_asset(disposable_id)
        self.assertEqual(
            "DISPOSED",
            asset_service.get_asset_by_id(disposable_id)[6],
        )

        with self.assertRaises(ValueError):
            asset_service.dispose_asset(disposable_id)

    def test_inventory_lifecycle(self):
        account_id = account_service.create_account("Cash", "CASH")

        _, item_id = inventory_service.buy_inventory(
            "2026-10-01",
            "Buy Item",
            account_id,
            "Item",
            10000,
            "2026-10-01",
        )

        self.assertEqual(
            -10000,
            transaction_service.get_account_balance(account_id),
        )

        _, profit = inventory_service.sell_inventory(
            "2026-10-03",
            "Sell Item",
            account_id,
            item_id,
            15000,
            "2026-10-03",
        )

        self.assertEqual(5000, profit)
        self.assertEqual(
            5000,
            transaction_service.get_account_balance(account_id),
        )
        self.assertEqual(5000, inventory_service.calculate_inventory_profit(item_id))

        with self.assertRaises(ValueError):
            inventory_service.sell_inventory(
                "2026-10-04",
                "Again",
                account_id,
                item_id,
                1,
                "2026-10-04",
            )

        with self.assertRaises(ValueError):
            inventory_service.sell_inventory(
                "2026-10-04",
                "Bad",
                account_id,
                999999,
                1,
                "2026-10-04",
            )

    def test_receivable_lifecycle_and_overpayment(self):
        account_id = account_service.create_account("Cash", "CASH")
        person_id = people_service.create_person("Customer", "CUSTOMER")

        _, receivable_id = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account_id,
            person_id,
            10000,
            "2026-10-15",
        )

        self.assertEqual(
            -10000,
            transaction_service.get_account_balance(account_id),
        )
        self.assertEqual(
            10000,
            receivable_service.get_receivable_balance(receivable_id),
        )

        receivable_service.record_receivable_payment(
            "2026-10-05",
            "Payment",
            account_id,
            receivable_id,
            4000,
        )
        self.assertEqual(
            6000,
            receivable_service.get_receivable_balance(receivable_id),
        )

        receivable_service.record_receivable_payment(
            "2026-10-10",
            "Final",
            account_id,
            receivable_id,
            6000,
        )

        self.assertEqual(
            0,
            receivable_service.get_receivable_balance(receivable_id),
        )
        self.assertEqual(
            "PAID",
            receivable_service.get_receivable_by_id(receivable_id)[6],
        )

        with self.assertRaises(ValueError):
            receivable_service.record_receivable_payment(
                "2026-10-11",
                "Over",
                account_id,
                receivable_id,
                1,
            )

    def test_liability_lifecycle_and_overpayment(self):
        account_id = account_service.create_account("Cash", "CASH")

        _, liability_id = liability_service.record_liability(
            "2026-10-01",
            "Debt",
            account_id,
            10000,
        )

        self.assertEqual(
            10000,
            transaction_service.get_account_balance(account_id),
        )
        self.assertEqual(
            10000,
            liability_service.get_liability_balance(liability_id),
        )

        liability_service.record_liability_payment(
            "2026-10-05",
            "Payment",
            account_id,
            liability_id,
            4000,
        )
        self.assertEqual(
            6000,
            liability_service.get_liability_balance(liability_id),
        )

        liability_service.record_liability_payment(
            "2026-10-10",
            "Final",
            account_id,
            liability_id,
            6000,
        )

        self.assertEqual(
            0,
            liability_service.get_liability_balance(liability_id),
        )
        self.assertEqual(
            "PAID",
            liability_service.get_liability_by_id(liability_id)[7],
        )

        with self.assertRaises(ValueError):
            liability_service.record_liability_payment(
                "2026-10-11",
                "Over",
                account_id,
                liability_id,
                1,
            )

    def test_transaction_rollback(self):
        account_id = account_service.create_account("Cash", "CASH")
        before = len(transaction_service.get_transactions())

        with self.assertRaises(sqlite3.IntegrityError):
            transaction_service.create_transaction(
                "2026-10-01",
                "Broken",
                "EXPENSE",
                None,
                [(999999, -100)],
            )

        self.assertEqual(before, len(transaction_service.get_transactions()))
        self.assertEqual(
            0,
            transaction_service.get_account_balance(account_id),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)