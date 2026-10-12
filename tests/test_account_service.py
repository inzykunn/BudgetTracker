from tests.base_test import BaseDatabaseTest
from services import account_service


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
