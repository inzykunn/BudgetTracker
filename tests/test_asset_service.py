from tests.base_test import BaseDatabaseTest
from services import account_service, asset_service, transaction_service


class AssetServiceTest(BaseDatabaseTest):
    def test_create_update_value(self):
        aid = asset_service.create_asset(
            "Laptop",
            "Electronics",
            30000,
            25000,
            "2026-10-01",
        )

        asset_service.update_asset_value(
            aid,
            22000,
            "2026-10-05",
        )

        self.assertEqual(
            asset_service.get_asset_by_id(aid)[3:5],
            (30000, 22000),
        )

        history = asset_service.get_asset_valuation_history(aid)

        self.assertEqual(len(history), 2)
        self.assertEqual(
            asset_service.get_asset_value_as_of(aid, "2026-10-01"),
            25000,
        )
        self.assertEqual(
            asset_service.get_asset_value_as_of(aid, "2026-10-04"),
            25000,
        )
        self.assertEqual(
            asset_service.get_asset_value_as_of(aid, "2026-10-05"),
            22000,
        )

    def test_buy_and_sell_asset(self):
        account = account_service.create_account("Cash", "CASH")

        tid, aid = asset_service.buy_asset(
            "2026-10-01",
            "Buy laptop",
            account,
            "Laptop",
            "Electronics",
            30000,
            "2026-10-01",
            current_value=25000,
        )

        self.assertIsNotNone(
            transaction_service.get_transaction_by_id(tid)[0]
        )
        self.assertEqual(
            transaction_service.get_account_balance(account),
            -30000,
        )
        self.assertEqual(
            asset_service.get_asset_value_as_of(aid, "2026-10-01"),
            25000,
        )

        sale_tid, profit = asset_service.sell_asset(
            "2026-10-05",
            "Sell laptop",
            account,
            aid,
            28000,
            "2026-10-05",
        )

        self.assertEqual(profit, 3000)
        self.assertIsNotNone(
            transaction_service.get_transaction_by_id(sale_tid)[0]
        )
        self.assertEqual(
            transaction_service.get_account_balance(account),
            -2000,
        )

        with self.assertRaises(ValueError):
            asset_service.sell_asset(
                "2026-10-06",
                "Sell again",
                account,
                aid,
                28000,
                "2026-10-06",
            )

    def test_dispose_asset(self):
        aid = asset_service.create_asset(
            "Chair",
            "Furniture",
            2000,
            1500,
            "2026-10-01",
        )

        asset_service.dispose_asset(aid)

        self.assertEqual(
            asset_service.get_asset_by_id(aid)[6],
            "DISPOSED",
        )

    def test_create_asset_records_initial_valuation(self):
        aid = asset_service.create_asset(
            "Phone",
            "Electronics",
            15000,
            14000,
            "2026-10-01",
        )

        history = asset_service.get_asset_valuation_history(aid)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][2], "2026-10-01")
        self.assertEqual(history[0][3], 14000)

    def test_asset_value_before_acquisition_returns_none(self):
        aid = asset_service.create_asset(
            "Tablet",
            "Electronics",
            10000,
            9000,
            "2026-10-10",
        )

        self.assertIsNone(
            asset_service.get_asset_value_as_of(aid, "2026-10-09")
        )

    def test_missing_asset_valuation_lookup_raises(self):
        with self.assertRaises(ValueError):
            asset_service.get_asset_value_as_of(
                999999,
                "2026-10-10",
            )

    def test_invalid_asset_purchase_does_not_create_asset(self):
        account = account_service.create_account("Cash", "CASH")
        initial_assets = len(asset_service.get_assets())
        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(ValueError):
            asset_service.buy_asset(
                "2026-10-01",
                "Invalid purchase",
                account,
                "Laptop",
                "Electronics",
                0,
                "2026-10-01",
            )

        self.assertEqual(len(asset_service.get_assets()), initial_assets)
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )

    def test_invalid_account_rolls_back_asset_purchase(self):
        initial_assets = len(asset_service.get_assets())
        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            asset_service.buy_asset(
                "2026-10-01",
                "Invalid account purchase",
                999999,
                "Laptop",
                "Electronics",
                30000,
                "2026-10-01",
            )

        self.assertEqual(len(asset_service.get_assets()), initial_assets)
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )

    def test_invalid_account_rolls_back_asset_sale(self):
        account = account_service.create_account("Cash", "CASH")

        aid = asset_service.create_asset(
            "Laptop",
            "Electronics",
            30000,
            25000,
            "2026-10-01",
        )

        initial_transactions = len(transaction_service.get_transactions())

        with self.assertRaises(Exception):
            asset_service.sell_asset(
                "2026-10-05",
                "Invalid account sale",
                999999,
                aid,
                28000,
                "2026-10-05",
            )

        asset = asset_service.get_asset_by_id(aid)

        self.assertEqual(asset[6], "ACTIVE")
        self.assertEqual(
            len(transaction_service.get_transactions()),
            initial_transactions,
        )
        self.assertEqual(
            transaction_service.get_account_balance(account),
            0,
        )

    def test_duplicate_valuation_date_is_rejected_without_changing_value(self):
        aid = asset_service.create_asset(
            "Laptop",
            "Electronics",
            30000,
            25000,
            "2026-10-01",
        )

        asset_service.update_asset_value(
            aid,
            22000,
            "2026-10-05",
        )

        with self.assertRaises(Exception):
            asset_service.update_asset_value(
                aid,
                20000,
                "2026-10-05",
            )

        self.assertEqual(
            asset_service.get_asset_by_id(aid)[4],
            22000,
        )

        self.assertEqual(
            asset_service.get_asset_value_as_of(aid, "2026-10-05"),
            22000,
        )