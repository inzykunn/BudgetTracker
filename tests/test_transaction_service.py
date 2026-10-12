from tests.base_test import BaseDatabaseTest
from services import account_service, category_service, transaction_service


class TransactionServiceTest(BaseDatabaseTest):
    def test_create_and_retrieve_transaction(self):
        account = account_service.create_account("Cash", "CASH")
        category = category_service.create_category("Food", "EXPENSE")

        transaction_id = transaction_service.create_transaction(
            "2026-10-01",
            "Groceries",
            "EXPENSE",
            category,
            [(account, -1500)],
        )

        transaction, entries = transaction_service.get_transaction_by_id(
            transaction_id
        )

        self.assertEqual(transaction[2:4], ("Groceries", "EXPENSE"))
        self.assertEqual(entries[0][2], -1500)

    def test_balance_and_transfer(self):
        cash = account_service.create_account("Cash", "CASH")
        bank = account_service.create_account("Bank", "BANK")

        transaction_service.create_transaction(
            "2026-10-01",
            "Income",
            "INCOME",
            None,
            [(cash, 5000)],
        )

        transaction_service.create_transaction(
            "2026-10-02",
            "Transfer",
            "TRANSFER",
            None,
            [(cash, -2000), (bank, 2000)],
        )

        self.assertEqual(
            transaction_service.get_account_balance(cash),
            3000,
        )
        self.assertEqual(
            transaction_service.get_account_balance(bank),
            2000,
        )

    def test_invalid_account_rolls_back_transaction(self):
        account = account_service.create_account("Cash", "CASH")
        before = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            transaction_service.create_transaction(
                "2026-10-01",
                "Invalid",
                "EXPENSE",
                None,
                [(account, -100), (999999, 100)],
            )

        self.assertEqual(
            len(transaction_service.get_transactions()),
            before,
        )
        self.assertEqual(
            transaction_service.get_account_balance(account),
            0,
        )
        self.assertEqual(
            len(transaction_service.get_transactions()),
            before,
        )

    def test_empty_entries_are_rejected(self):
        account_service.create_account("Cash", "CASH")

        with self.assertRaises(ValueError):
            transaction_service.create_transaction(
                "2026-10-01",
                "Empty transaction",
                "EXPENSE",
                None,
                [],
            )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_zero_amount_entry_is_rejected(self):
        account = account_service.create_account("Cash", "CASH")

        with self.assertRaises(ValueError):
            transaction_service.create_transaction(
                "2026-10-01",
                "Zero transaction",
                "INCOME",
                None,
                [(account, 0)],
            )

        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_historical_account_balance(self):
        account = account_service.create_account("Cash", "CASH")

        transaction_service.create_transaction(
            "2026-10-01",
            "Opening income",
            "INCOME",
            None,
            [(account, 5000)],
        )

        transaction_service.create_transaction(
            "2026-10-05",
            "Groceries",
            "EXPENSE",
            None,
            [(account, -1500)],
        )

        transaction_service.create_transaction(
            "2026-10-10",
            "Additional income",
            "INCOME",
            None,
            [(account, 3000)],
        )

        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account,
                "2026-10-04",
            ),
            5000,
        )

        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account,
                "2026-10-05",
            ),
            3500,
        )

        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account,
                "2026-10-09",
            ),
            3500,
        )

        self.assertEqual(
            transaction_service.get_account_balance_as_of(
                account,
                "2026-10-10",
            ),
            6500,
        )

    def test_historical_transactions_exclude_future_records(self):
        account = account_service.create_account("Cash", "CASH")

        transaction_service.create_transaction(
            "2026-10-01",
            "October income",
            "INCOME",
            None,
            [(account, 5000)],
        )

        transaction_service.create_transaction(
            "2026-11-01",
            "November income",
            "INCOME",
            None,
            [(account, 3000)],
        )

        transactions = transaction_service.get_transactions_as_of(
            "2026-10-31"
        )

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][2], "October income")

    def test_missing_transaction_date_is_rejected(self):
        account = account_service.create_account("Cash", "CASH")

        with self.assertRaises(ValueError):
            transaction_service.create_transaction(
                None,
                "Income",
                "INCOME",
                None,
                [(account, 1000)],
            )

        self.assertEqual(len(transaction_service.get_transactions()), 0)