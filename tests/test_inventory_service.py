from tests.base_test import BaseDatabaseTest
from services import account_service, inventory_service, transaction_service


class InventoryServiceTest(BaseDatabaseTest):

    def test_create_inventory_item(self):
        item_id = inventory_service.create_inventory_item(
            "Headphones",
            10000,
            "2026-10-01",
            # Add any other required arguments from your service signature.
        )

        row = inventory_service.get_inventory_item_by_id(item_id)

        self.assertEqual(row[1], "Headphones")
        self.assertEqual(row[2], 10000)
        self.assertEqual(row[6], "AVAILABLE")

    def test_buy_and_sell_inventory(self):
        account = account_service.create_account("Cash", "CASH")

        _, item_id = inventory_service.buy_inventory(
            "2026-10-01",
            "Buy item",
            account,
            "Headphones",
            10000,
            "2026-10-01",
        )

        self.assertEqual(
            transaction_service.get_account_balance(account),
            -10000,
        )

        tid, profit = inventory_service.sell_inventory(
            "2026-10-03",
            "Sell item",
            account,
            item_id,
            15000,
            "2026-10-03",
        )

        self.assertEqual(profit, 5000)
        self.assertEqual(
            inventory_service.get_inventory_item_by_id(item_id)[6],
            "SOLD",
        )
        self.assertIsNotNone(tid)

        with self.assertRaises(ValueError):
            inventory_service.sell_inventory(
                "2026-10-04",
                "Sell again",
                account,
                item_id,
                15000,
                "2026-10-04",
            )

    def test_invalid_sale_price(self):
        account = account_service.create_account("Cash", "CASH")

        _, item_id = inventory_service.buy_inventory(
            "2026-10-01",
            "Buy item",
            account,
            "Headphones",
            10000,
            "2026-10-01",
        )

        with self.assertRaises(ValueError):
            inventory_service.sell_inventory(
                "2026-10-03",
                "Invalid sale",
                account,
                item_id,
                0,
                "2026-10-03",
            )