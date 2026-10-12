from tests.base_test import BaseDatabaseTest
from services import account_service, transaction_service


class AccountServiceTest(BaseDatabaseTest):
    def test_create_and_get_account(self):
        account_id = account_service.create_account("Cash", "CASH")
        row = account_service.get_account_by_id(account_id)
        self.assertEqual((row[1], row[2], row[3]), ("Cash", "CASH", 1))

    def test_duplicate_name_returns_existing_id(self):
        first = account_service.create_account("Cash", "CASH")
        self.assertEqual(account_service.create_account("Cash", "BANK"), first)

    def test_update_and_deactivate(self):
        account_id = account_service.create_account("Cash", "CASH")
        account_service.update_account(account_id, "Wallet", "CASH")
        self.assertEqual(account_service.get_account_by_id(account_id)[1], "Wallet")
        account_service.deactivate_account(account_id)
        self.assertEqual(account_service.get_account_by_id(account_id)[3], 0)

    def test_creation_records_opening_balance_once(self):
        account_id = account_service.create_account(
            "Cash",
            "CASH",
            15000,
            "2026-10-01"
        )

        self.assertEqual(transaction_service.get_account_balance(account_id), 15000)
        transactions = transaction_service.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][3], "OPENING_BALANCE")

    def test_opening_balance_then_increases_and_decreases(self):
        account_id = account_service.create_account(
            "Cash",
            "CASH",
            15000,
            "2026-10-01"
        )

        transaction_service.create_transaction(
            "2026-10-02",
            "Payday",
            "INCOME",
            None,
            [(account_id, 5000)]
        )
        transaction_service.create_transaction(
            "2026-10-03",
            "Groceries",
            "EXPENSE",
            None,
            [(account_id, -1200)]
        )

        self.assertEqual(transaction_service.get_account_balance(account_id), 18800)

    def test_duplicate_account_does_not_record_opening_balance_again(self):
        account_id = account_service.create_account(
            "Cash",
            "CASH",
            15000,
            "2026-10-01"
        )

        duplicate_id = account_service.create_account(
            "Cash",
            "BANK",
            5000,
            "2026-10-02"
        )

        self.assertEqual(duplicate_id, account_id)
        self.assertEqual(transaction_service.get_account_balance(account_id), 15000)
        self.assertEqual(len(transaction_service.get_transactions()), 1)

    def test_invalid_opening_balance_is_rejected(self):
        with self.assertRaises(ValueError):
            account_service.create_account("Cash", "CASH", -100)

        self.assertIsNone(account_service.get_account_by_name("Cash"))

    def test_opening_transaction_failure_rolls_back_account(self):
        with self.assertRaises(ValueError):
            account_service.create_account(
                "Cash",
                "CASH",
                15000,
                ""
            )

        self.assertIsNone(account_service.get_account_by_name("Cash"))
        self.assertEqual(transaction_service.get_transactions(), [])

    def test_deactivating_account_preserves_balance_and_transactions(self):
        account_id = account_service.create_account(
            "Cash",
            "CASH",
            15000,
            "2026-10-01"
        )

        transaction_service.create_transaction(
            "2026-10-02",
            "Groceries",
            "EXPENSE",
            None,
            [(account_id, -2000)]
        )

        account_service.deactivate_account(account_id)

        account = account_service.get_account_by_id(account_id)
        balance = transaction_service.get_account_balance(account_id)
        transactions = transaction_service.get_transactions()

        self.assertEqual(account[3], 0)
        self.assertEqual(balance, 13000)
        self.assertEqual(len(transactions), 2)
        self.assertEqual(
            {transaction[3] for transaction in transactions},
            {"OPENING_BALANCE", "EXPENSE"}
        )