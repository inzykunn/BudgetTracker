import unittest

from database.connection import get_connection
from services.financial_snapshot_service import (
    create_snapshot,
    finalize_snapshot,
    get_snapshot,
    list_snapshots,
)
from tests.base_test import BaseDatabaseTest


class FinancialSnapshotServiceTest(BaseDatabaseTest):
    def test_snapshot_captures_account_balance_and_records(self):
        account_id = self.create_account()
        connection = get_connection()
        try:
            transaction = connection.execute(
                "INSERT INTO transactions (date, description, type) VALUES (?, ?, ?)",
                ("2026-10-09", "Opening balance", "OPENING_BALANCE"),
            )
            connection.execute(
                "INSERT INTO transaction_entries (transaction_id, account_id, amount) VALUES (?, ?, ?)",
                (transaction.lastrowid, account_id, 7574),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        snapshot_id = create_snapshot("Opening position", "2026-10-09")
        snapshot = get_snapshot(snapshot_id)

        self.assertEqual(snapshot["data"]["account_balances"][0]["balance"], 7574)
        self.assertEqual(snapshot["snapshot_date"], "2026-10-09")

    def test_finalized_snapshot_preserves_captured_values(self):
        account_id = self.create_account()
        connection = get_connection()
        try:
            transaction = connection.execute(
                "INSERT INTO transactions (date, description, type) VALUES (?, ?, ?)",
                ("2026-10-09", "Opening balance", "OPENING_BALANCE"),
            )
            connection.execute(
                "INSERT INTO transaction_entries (transaction_id, account_id, amount) VALUES (?, ?, ?)",
                (transaction.lastrowid, account_id, 7574),
            )
            connection.commit()
        finally:
            connection.close()

        snapshot_id = create_snapshot("Verified opening", "2026-10-09")
        finalize_snapshot(snapshot_id)

        connection = get_connection()
        try:
            connection.execute(
                "INSERT INTO transaction_entries (transaction_id, account_id, amount) VALUES (?, ?, ?)",
                (transaction.lastrowid, account_id, 1000),
            )
            connection.commit()
        finally:
            connection.close()

        snapshot = get_snapshot(snapshot_id)
        self.assertTrue(snapshot["finalized"])
        self.assertEqual(snapshot["data"]["account_balances"][0]["balance"], 7574)
        self.assertEqual(len(list_snapshots()), 1)

    def test_invalid_snapshot_date_is_rejected(self):
        with self.assertRaises(ValueError):
            create_snapshot("Bad date", "October 9, 2026")


if __name__ == "__main__":
    unittest.main()
