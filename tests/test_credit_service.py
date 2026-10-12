from tests.base_test import BaseDatabaseTest
from services import credit_service


class CreditServiceTest(BaseDatabaseTest):
    def test_create_update_deactivate(self):
        credit_id = credit_service.create_credit_account("Card", 50000)
        self.assertEqual(credit_service.get_credit_account_by_id(credit_id)[2], 50000)
        credit_service.update_credit_account(credit_id, "Card Plus", 70000)
        row = credit_service.get_credit_account_by_id(credit_id)
        self.assertEqual((row[1], row[2]), ("Card Plus", 70000))
        credit_service.deactivate_credit_account(credit_id)
        self.assertEqual(credit_service.get_credit_account_by_id(credit_id)[3], 0)

    def test_duplicate_name_returns_existing_id(self):
        first = credit_service.create_credit_account("Card", 50000)
        self.assertEqual(credit_service.create_credit_account("Card", 90000), first)
