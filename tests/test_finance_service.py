from tests.base_test import BaseDatabaseTest
from services import account_service, finance_service, transaction_service
from services import category_service


class FinanceServiceTest(BaseDatabaseTest):
    def test_record_income(self):
        account = account_service.create_account("Cash", "CASH")

        finance_service.record_income(
            "2026-10-01", "Pay", account, 5000
        )

        self.assertEqual(
            transaction_service.get_account_balance(account),
            5000,
        )

    def test_record_expense(self):
        account = account_service.create_account("Cash", "CASH")

        finance_service.record_expense(
            "2026-10-01", "Food", account, 1200
        )

        self.assertEqual(
            transaction_service.get_account_balance(account),
            -1200,
        )

    def test_transfer(self):
        cash = account_service.create_account("Cash", "CASH")
        bank = account_service.create_account("Bank", "BANK")

        finance_service.record_income(
            "2026-10-01", "Starting cash", cash, 5000
        )
        finance_service.record_transfer(
            "2026-10-02", "Move money", cash, bank, 2000
        )

        self.assertEqual(
            transaction_service.get_account_balance(cash),
            3000,
        )
        self.assertEqual(
            transaction_service.get_account_balance(bank),
            2000,
        )

    def test_income_rejects_nonpositive_amount(self):
        account = account_service.create_account("Cash", "CASH")

        for amount in (0, -100):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    finance_service.record_income(
                        "2026-10-01", "Invalid income", account, amount
                    )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_expense_rejects_nonpositive_amount(self):
        account = account_service.create_account("Cash", "CASH")

        for amount in (0, -100):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    finance_service.record_expense(
                        "2026-10-01", "Invalid expense", account, amount
                    )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_transfer_rejects_nonpositive_amount(self):
        cash = account_service.create_account("Cash", "CASH")
        bank = account_service.create_account("Bank", "BANK")

        for amount in (0, -100):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    finance_service.record_transfer(
                        "2026-10-01", "Invalid transfer",
                        cash, bank, amount
                    )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_transfer_rejects_same_account(self):
        account = account_service.create_account("Cash", "CASH")

        with self.assertRaises(ValueError):
            finance_service.record_transfer(
                "2026-10-01", "Invalid transfer",
                account, account, 1000
            )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_finance_operations_preserve_historical_balances(self):
        account = account_service.create_account("Cash", "CASH")

        finance_service.record_income(
            "2026-10-01", "Pay", account, 5000
        )
        finance_service.record_expense(
            "2026-10-05", "Food", account, 1200
        )
        finance_service.record_income(
            "2026-10-10", "Additional pay", account, 2000
        )

        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account, "2026-10-04"
            ),
            5000,
        )
        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account, "2026-10-05"
            ),
            3800,
        )
        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account, "2026-10-09"
            ),
            3800,
        )
        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account, "2026-10-10"
            ),
            5800,
        )

    def test_income_and_expense_transaction_types_and_signs(self):
        account = account_service.create_account("Cash", "CASH")

        income_id = finance_service.record_income(
            "2026-10-01", "Pay", account, 5000
        )
        expense_id = finance_service.record_expense(
            "2026-10-02", "Food", account, 1200
        )

        income, income_entries = transaction_service.get_transaction_by_id(
            income_id
        )
        expense, expense_entries = transaction_service.get_transaction_by_id(
            expense_id
        )

        self.assertEqual(income[3], "INCOME")
        self.assertEqual(income_entries[0][2], 5000)
        self.assertEqual(expense[3], "EXPENSE")
        self.assertEqual(expense_entries[0][2], -1200)

    def test_income_accepts_category(self):
        account = account_service.create_account("Cash", "CASH")
        category = category_service.create_category("Salary", "INCOME")

        transaction_id = finance_service.record_income(
            "2026-10-01", "Pay", account, 5000, category
        )

        transaction, _ = transaction_service.get_transaction_by_id(
            transaction_id
        )

        self.assertEqual(transaction[3], "INCOME")
        self.assertEqual(transaction[4], category)

    def test_expense_accepts_category(self):
        account = account_service.create_account("Cash", "CASH")
        category = category_service.create_category("Food", "EXPENSE")

        transaction_id = finance_service.record_expense(
            "2026-10-01", "Groceries", account, 1200, category
        )

        transaction, _ = transaction_service.get_transaction_by_id(
            transaction_id
        )

        self.assertEqual(transaction[3], "EXPENSE")
        self.assertEqual(transaction[4], category)