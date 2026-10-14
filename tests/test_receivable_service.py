from tests.base_test import BaseDatabaseTest
from services import account_service, people_service, receivable_service, transaction_service


class ReceivableServiceTest(BaseDatabaseTest):
    def test_record_partial_and_final_payments(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")
        tid, rid = receivable_service.record_receivable("2026-10-01", "Loan", account, person, 10000, "2026-10-15")
        self.assertEqual(receivable_service.get_receivable_balance(rid), 10000)
        receivable_service.record_receivable_payment("2026-10-05", "Partial", account, rid, 4000)
        self.assertEqual(receivable_service.get_receivable_balance(rid), 6000)
        receivable_service.record_receivable_payment("2026-10-10", "Final", account, rid, 6000)
        self.assertEqual(receivable_service.get_receivable_balance(rid), 0)
        self.assertEqual(receivable_service.get_receivable_by_id(rid)[6], "PAID")
        self.assertIsNotNone(transaction_service.get_transaction_by_id(tid)[0])

    def test_reject_overpayment(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")
        _, rid = receivable_service.record_receivable("2026-10-01", "Loan", account, person, 1000)
        with self.assertRaises(ValueError):
            receivable_service.record_receivable_payment("2026-10-02", "Too much", account, rid, 1001)

    def test_receivable_balance_history(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        _, rid = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account,
            person,
            10000
        )

        receivable_service.record_receivable_payment(
            "2026-10-05",
            "Partial",
            account,
            rid,
            4000
        )

        receivable_service.record_receivable_payment(
            "2026-10-10",
            "Final",
            account,
            rid,
            6000
        )

        self.assertEqual(
            receivable_service.get_receivable_balance_as_of(
                rid,
                "2026-10-01"
            ),
            10000
        )

        self.assertEqual(
            receivable_service.get_receivable_balance_as_of(
                rid,
                "2026-10-05"
            ),
            6000
        )

        self.assertEqual(
            receivable_service.get_receivable_balance_as_of(
                rid,
                "2026-10-10"
            ),
            0
        )

    def test_reject_payment_before_receivable_creation(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        _, rid = receivable_service.record_receivable(
            "2026-10-10",
            "Loan",
            account,
            person,
            10000
        )

        with self.assertRaises(ValueError):
            receivable_service.record_receivable_payment(
                "2026-10-09",
                "Early payment",
                account,
                rid,
                1000
            )

        self.assertEqual(
            receivable_service.get_receivable_balance(rid),
            10000
        )

    def test_cannot_close_receivable_with_remaining_balance(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        _, rid = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account,
            person,
            10000
        )

        with self.assertRaises(ValueError):
            receivable_service.close_receivable(rid)

        self.assertEqual(
            receivable_service.get_receivable_by_id(rid)[6],
            "OPEN"
        )

    def test_reject_payment_after_receivable_is_paid(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        _, rid = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account,
            person,
            1000
        )

        receivable_service.record_receivable_payment(
            "2026-10-02",
            "Final payment",
            account,
            rid,
            1000
        )

        with self.assertRaises(ValueError):
            receivable_service.record_receivable_payment(
                "2026-10-03",
                "Extra payment",
                account,
                rid,
                100
            )

    def test_invalid_account_rolls_back_receivable_creation(self):
        person = people_service.create_person("Alex", "PERSON")

        initial_receivables = len(receivable_service.get_receivables())
        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            receivable_service.record_receivable(
                "2026-10-01",
                "Invalid account loan",
                999999,
                person,
                1000
            )

        self.assertEqual(
            len(receivable_service.get_receivables()),
            initial_receivables
        )
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions
        )

    def test_invalid_account_rolls_back_receivable_payment(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        _, rid = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account,
            person,
            1000
        )

        initial_transactions = len(transaction_service.get_transactions())
        initial_history = receivable_service.get_receivable_balance_history(rid)

        with self.assertRaises(Exception):
            receivable_service.record_receivable_payment(
                "2026-10-02",
                "Invalid account payment",
                999999,
                rid,
                400
            )

        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions
        )
        self.assertEqual(
            receivable_service.get_receivable_balance(rid),
            1000
        )
        self.assertEqual(
            receivable_service.get_receivable_balance_history(rid),
            initial_history
        )
        self.assertEqual(
            receivable_service.get_receivable_by_id(rid)[6],
            "OPEN"
        )

    def test_receivable_operations_create_correct_transaction_entries(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Alex", "PERSON")

        tid, rid = receivable_service.record_receivable(
            "2026-10-01",
            "Loan",
            account,
            person,
            10000
        )

        transaction, entries = transaction_service.get_transaction_by_id(tid)

        self.assertIsNotNone(transaction)
        self.assertEqual(transaction[3], "RECEIVABLE")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in entries],
            [(account, -10000)]
        )

        payment_tid = receivable_service.record_receivable_payment(
            "2026-10-05",
            "Loan repayment",
            account,
            rid,
            4000
        )

        payment_transaction, payment_entries = (
            transaction_service.get_transaction_by_id(payment_tid)
        )

        self.assertIsNotNone(payment_transaction)
        self.assertEqual(payment_transaction[3], "RECEIVABLE_PAYMENT")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in payment_entries],
            [(account, 4000)]
        )
    def test_update_preserves_creation_date_and_past_balance(self):
        account = account_service.create_account("Cash", "CASH")
        person = people_service.create_person("Jordan", "PERSON")
        _, rid = receivable_service.record_receivable(
            "2026-10-01", "Loan", account, person, 10000
        )
        with self.assertRaises(ValueError):
            receivable_service.update_receivable(
                rid, "Loan", 10000, "2026-10-05", None, "OPEN"
            )
        receivable_service.update_receivable(
            rid, "Updated loan", 12000, "2026-10-01", None, "OPEN"
        )
        self.assertEqual(receivable_service.get_receivable_balance_as_of(rid, "2026-10-01"), 10000)
        self.assertEqual(receivable_service.get_receivable_balance(rid), 12000)
