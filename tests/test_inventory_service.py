from tests.base_test import BaseDatabaseTest
from services import account_service, inventory_service, transaction_service


class InventoryServiceTest(BaseDatabaseTest):

    def test_create_inventory_item(self):
        item_id = inventory_service.create_inventory_item(
            "Headphones",
            10000,
            "2026-10-01",
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

    def test_inventory_operations_create_correct_transaction_entries(self):
        account = account_service.create_account("Cash", "CASH")

        purchase_tid, item_id = inventory_service.buy_inventory(
            "2026-10-01",
            "Buy item",
            account,
            "Headphones",
            10000,
            "2026-10-01",
        )

        purchase_transaction, purchase_entries = (
            transaction_service.get_transaction_by_id(purchase_tid)
        )

        self.assertIsNotNone(purchase_transaction)
        self.assertEqual(purchase_transaction[3], "EXPENSE")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in purchase_entries],
            [(account, -10000)],
        )

        sale_tid, profit = inventory_service.sell_inventory(
            "2026-10-03",
            "Sell item",
            account,
            item_id,
            15000,
            "2026-10-03",
        )

        sale_transaction, sale_entries = (
            transaction_service.get_transaction_by_id(sale_tid)
        )

        self.assertIsNotNone(sale_transaction)
        self.assertEqual(sale_transaction[3], "INCOME")
        self.assertEqual(
            [(entry[1], entry[2]) for entry in sale_entries],
            [(account, 15000)],
        )
        self.assertEqual(profit, 5000)

    def test_invalid_account_rolls_back_inventory_purchase(self):
        initial_items = len(inventory_service.get_inventory_items())
        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            inventory_service.buy_inventory(
                "2026-10-01",
                "Invalid purchase",
                999999,
                "Headphones",
                10000,
                "2026-10-01",
            )

        self.assertEqual(
            len(inventory_service.get_inventory_items()),
            initial_items,
        )
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )

    def test_invalid_account_rolls_back_inventory_sale(self):
        account = account_service.create_account("Cash", "CASH")

        _, item_id = inventory_service.buy_inventory(
            "2026-10-01",
            "Buy item",
            account,
            "Headphones",
            10000,
            "2026-10-01",
        )

        initial_transactions = len(transaction_service.get_transactions())
        initial_item = inventory_service.get_inventory_item_by_id(item_id)

        with self.assertRaises(Exception):
            inventory_service.sell_inventory(
                "2026-10-03",
                "Invalid sale",
                999999,
                item_id,
                15000,
                "2026-10-03",
            )

        self.assertEqual(
            inventory_service.get_inventory_item_by_id(item_id),
            initial_item,
        )
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )
        self.assertEqual(
            transaction_service.get_account_balance(account),
            -10000,
        )