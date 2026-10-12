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
