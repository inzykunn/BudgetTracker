from tests.base_test import BaseDatabaseTest
from services import account_service, finance_service, transaction_service


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