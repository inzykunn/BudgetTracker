from tests.base_test import BaseDatabaseTest
from services import account_service, liability_service, transaction_service


class LiabilityServiceTest(BaseDatabaseTest):
    def test_record_partial_and_final_payments(self):
        account = account_service.create_account("Cash", "CASH")

        tid, lid = liability_service.record_liability(
            "2026-10-01",
            "Debt",
            account,
            10000,
        )

        self.assertEqual(liability_service.get_liability_balance(lid), 10000)

        liability_service.record_liability_payment(
            "2026-10-05", "Partial", account, lid, 4000
        )

        self.assertEqual(liability_service.get_liability_balance(lid), 6000)

        liability_service.record_liability_payment(
            "2026-10-10", "Final", account, lid, 6000
        )

        self.assertEqual(liability_service.get_liability_balance(lid), 0)
        self.assertEqual(liability_service.get_liability_by_id(lid)[7], "PAID")
        self.assertIsNotNone(
            transaction_service.get_transaction_by_id(tid)[0]
        )

    def test_reject_overpayment(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 1000
        )

        with self.assertRaises(ValueError):
            liability_service.record_liability_payment(
                "2026-10-02", "Too much", account, lid, 1001
            )

        self.assertEqual(liability_service.get_liability_balance(lid), 1000)

    def test_historical_balance_after_payments(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 10000
        )

        liability_service.record_liability_payment(
            "2026-10-05", "Partial", account, lid, 4000
        )

        liability_service.record_liability_payment(
            "2026-10-10", "Final", account, lid, 6000
        )

        self.assertEqual(
            liability_service.get_liability_balance_as_of(
                lid, "2026-09-30"
            ),
            None,
        )

        self.assertEqual(
            liability_service.get_liability_balance_as_of(
                lid, "2026-10-01"
            ),
            10000,
        )

        self.assertEqual(
            liability_service.get_liability_balance_as_of(
                lid, "2026-10-07"
            ),
            6000,
        )

        self.assertEqual(
            liability_service.get_liability_balance_as_of(
                lid, "2026-10-10"
            ),
            0,
        )

    def test_liability_history_records_each_payment(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 10000
        )

        liability_service.record_liability_payment(
            "2026-10-05", "Partial", account, lid, 4000
        )

        liability_service.record_liability_payment(
            "2026-10-10", "Final", account, lid, 6000
        )

        history = liability_service.get_liability_balance_history(lid)

        self.assertEqual(len(history), 3)
        self.assertEqual(
            [
                (row[2], row[3], row[4])
                for row in reversed(history)
            ],
            [
                ("2026-10-01", 10000, "OPEN"),
                ("2026-10-05", 6000, "OPEN"),
                ("2026-10-10", 0, "PAID"),
            ],
        )

    def test_invalid_liability_amount_is_rejected(self):
        account = account_service.create_account("Cash", "CASH")

        for amount in (0, -100):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    liability_service.record_liability(
                        "2026-10-01", "Invalid debt", account, amount
                    )

        self.assertEqual(len(liability_service.get_liabilities()), 0)
        self.assertEqual(len(transaction_service.get_transactions()), 0)

    def test_invalid_payment_amount_is_rejected(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 1000
        )

        for amount in (0, -100):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    liability_service.record_liability_payment(
                        "2026-10-02", "Invalid payment", account, lid, amount
                    )

        self.assertEqual(liability_service.get_liability_balance(lid), 1000)
        self.assertEqual(len(transaction_service.get_transactions()), 1)

    def test_payment_before_creation_date_is_rejected(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-05", "Debt", account, 1000
        )

        with self.assertRaises(ValueError):
            liability_service.record_liability_payment(
                "2026-10-04", "Early payment", account, lid, 500
            )

        self.assertEqual(liability_service.get_liability_balance(lid), 1000)

    def test_invalid_account_rolls_back_liability_creation(self):
        initial_liabilities = len(liability_service.get_liabilities())
        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            liability_service.record_liability(
                "2026-10-01",
                "Invalid account debt",
                999999,
                1000,
            )

        self.assertEqual(
            len(liability_service.get_liabilities()),
            initial_liabilities,
        )
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )

    def test_invalid_account_rolls_back_payment(self):
        account = account_service.create_account("Cash", "CASH")

        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 1000
        )

        initial_transactions = len(transaction_service.get_transactions())
        initial_history = liability_service.get_liability_balance_history(lid)

        with self.assertRaises(Exception):
            liability_service.record_liability_payment(
                "2026-10-02", "Invalid account payment", 999999, lid, 500
            )

        self.assertEqual(liability_service.get_liability_balance(lid), 1000)
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )
        self.assertEqual(
            liability_service.get_liability_balance_history(lid),
            initial_history,
        )

    def test_missing_liability_raises_error(self):
        with self.assertRaises(ValueError):
            liability_service.get_liability_balance(999999)

        with self.assertRaises(ValueError):
            liability_service.get_liability_balance_as_of(
                999999, "2026-10-10"
            )

        with self.assertRaises(ValueError):
            liability_service.get_liability_balance_history(999999)

    def test_liability_operations_create_correct_transaction_entries(self):
        account = account_service.create_account("Cash", "CASH")

        tid, lid = liability_service.record_liability(
            "2026-10-01",
            "Debt",
            account,
            10000,
        )

        transaction, entries = transaction_service.get_transaction_by_id(tid)

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction[3], "LIABILITY")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in entries],
            [(account, 10000)],
        )

        payment_tid = liability_service.record_liability_payment(
            "2026-10-05",
            "Debt payment",
            account,
            lid,
            4000,
        )

        payment_transaction, payment_entries = (
            transaction_service.get_transaction_by_id(payment_tid)
        )

        self.assertIsNotNone(payment_transaction)
        self.assertEqual(payment_transaction[3], "LIABILITY_PAYMENT")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in payment_entries],
            [(account, -4000)],
        )
    def test_update_preserves_creation_date_and_past_balance(self):
        account = account_service.create_account("Cash", "CASH")
        _, lid = liability_service.record_liability(
            "2026-10-01", "Debt", account, 10000
        )
        with self.assertRaises(ValueError):
            liability_service.update_liability(
                lid, "Debt", 10000, "2026-10-05"
            )
        liability_service.update_liability(
            lid, "Updated debt", 12000, "2026-10-01"
        )
        self.assertEqual(liability_service.get_liability_balance_as_of(lid, "2026-10-01"), 10000)
        self.assertEqual(liability_service.get_liability_balance(lid), 12000)
