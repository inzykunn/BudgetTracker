from tests.base_test import BaseDatabaseTest
from services import account_service, liability_service, transaction_service


class LiabilityServiceTest(BaseDatabaseTest):
    def test_record_partial_and_final_payments(self):
        account = account_service.create_account("Cash", "CASH")
        tid, lid = liability_service.record_liability("2026-10-01", "Debt", account, 10000)
        self.assertEqual(liability_service.get_liability_balance(lid), 10000)
        liability_service.record_liability_payment("2026-10-05", "Partial", account, lid, 4000)
        self.assertEqual(liability_service.get_liability_balance(lid), 6000)
        liability_service.record_liability_payment("2026-10-10", "Final", account, lid, 6000)
        self.assertEqual(liability_service.get_liability_balance(lid), 0)
        self.assertEqual(liability_service.get_liability_by_id(lid)[7], "PAID")
        self.assertIsNotNone(transaction_service.get_transaction_by_id(tid)[0])

    def test_reject_overpayment(self):
        account = account_service.create_account("Cash", "CASH")
        _, lid = liability_service.record_liability("2026-10-01", "Debt", account, 1000)
        with self.assertRaises(ValueError):
            liability_service.record_liability_payment("2026-10-02", "Too much", account, lid, 1001)
