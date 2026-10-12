from tests.base_test import BaseDatabaseTest
from services import category_service


class CategoryServiceTest(BaseDatabaseTest):
    def test_create_and_get_category(self):
        category_id = category_service.create_category("Food", "EXPENSE")
        self.assertEqual(category_service.get_category_by_id(category_id)[1:], ("Food", "EXPENSE"))

    def test_duplicate_name_returns_existing_id(self):
        first = category_service.create_category("Food", "EXPENSE")
        self.assertEqual(category_service.create_category("Food", "INCOME"), first)
