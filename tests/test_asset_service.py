from tests.base_test import BaseDatabaseTest
from services import account_service, asset_service, transaction_service


class AssetServiceTest(BaseDatabaseTest):
    def test_create_update_value(self):
        aid = asset_service.create_asset("Laptop", "Electronics", 30000, 25000, "2026-10-01")
        asset_service.update_asset_value(aid, 22000)
        self.assertEqual(asset_service.get_asset_by_id(aid)[3:5], (30000, 22000))

    def test_buy_and_sell_asset(self):
        account = account_service.create_account("Cash", "CASH")
        _, aid = asset_service.buy_asset("2026-10-01", "Buy laptop", account, "Laptop", "Electronics", 30000, "2026-10-01", current_value=25000)
        tid, profit = asset_service.sell_asset("2026-10-05", "Sell laptop", account, aid, 28000, "2026-10-05")
        self.assertEqual(profit, 3000)
        self.assertIsNotNone(transaction_service.get_transaction_by_id(tid)[0])
        with self.assertRaises(ValueError):
            asset_service.sell_asset("2026-10-06", "Sell again", account, aid, 28000, "2026-10-06")

    def test_dispose_asset(self):
        aid = asset_service.create_asset("Chair", "Furniture", 2000, 1500, "2026-10-01")
        asset_service.dispose_asset(aid)
        self.assertEqual(asset_service.get_asset_by_id(aid)[6], "DISPOSED")
