import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database import connection as db_connection


class DatabaseTest(unittest.TestCase):
    expected_tables = {
        "accounts",
        "categories",
        "transactions",
        "transaction_entries",
        "people",
        "assets",
        "asset_valuations",
        "inventory_items",
        "receivables",
        "receivable_payments",
        "receivable_balance_history",
        "credit_accounts",
        "liabilities",
        "liability_payments",
        "liability_balance_history",
        "financial_snapshots",
    }

    def test_new_database_initializes_expected_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_dir = Path(temp_dir)
            database_path = database_dir / "budget.db"
            with patch.object(db_connection, "DATABASE_DIR", database_dir), patch.object(
                db_connection, "DATABASE_PATH", database_path
            ):
                connection = db_connection.get_connection()
                try:
                    rows = connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                finally:
                    connection.close()

            actual_tables = {row[0] for row in rows}
            missing_tables = self.expected_tables - actual_tables
            self.assertFalse(missing_tables, f"Missing database tables: {missing_tables}")

    def test_initialize_database_does_not_delete_existing_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_dir = Path(temp_dir)
            database_path = database_dir / "budget.db"
            with patch.object(db_connection, "DATABASE_DIR", database_dir), patch.object(
                db_connection, "DATABASE_PATH", database_path
            ):
                db_connection.initialize_database()
                connection = sqlite3.connect(database_path)
                try:
                    connection.execute(
                        "INSERT INTO accounts (name, type) VALUES (?, ?)",
                        ("Preserved Account", "CASH"),
                    )
                    connection.commit()
                finally:
                    connection.close()
                db_connection.initialize_database()
                connection = sqlite3.connect(database_path)
                try:
                    row = connection.execute(
                        "SELECT name FROM accounts WHERE name = ?",
                        ("Preserved Account",),
                    ).fetchone()
                finally:
                    connection.close()

            self.assertEqual(("Preserved Account",), row)


if __name__ == "__main__":
    unittest.main()
