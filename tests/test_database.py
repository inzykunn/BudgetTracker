import sqlite3
import unittest

from database.connection import DATABASE_PATH


class DatabaseTest(unittest.TestCase):

    def test_expected_tables_exist(self):
        expected_tables = {
            "accounts",
            "categories",
            "transactions",
            "transaction_entries",
            "people",
            "assets",
            "inventory_items",
            "receivables",
            "credit_accounts",
            "liabilities",
            "receivable_payments",
            "liability_payments",
        }

        with sqlite3.connect(DATABASE_PATH) as db:
            rows = db.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()

        actual_tables = {row[0] for row in rows}

        missing_tables = expected_tables - actual_tables

        self.assertFalse(
            missing_tables,
            f"Missing database tables: {missing_tables}",
        )


if __name__ == "__main__":
    unittest.main()