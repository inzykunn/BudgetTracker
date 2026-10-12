import sqlite3
import unittest

from database import connection


class BaseDatabaseTest(unittest.TestCase):

    def setUp(self):
        self.original_db_path = connection.DATABASE_PATH
        connection.DATABASE_PATH = self.original_db_path

        schema_path = (
            connection.BASE_DIR / "database" / "schema.sql"
        )

        db = sqlite3.connect(self.original_db_path)

        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.executescript(
                schema_path.read_text(encoding="utf-8")
            )

            tables = [
                "liability_payments",
                "receivable_payments",
                "liability_balance_history",
                "receivable_balance_history",
                "asset_valuations",
                "transaction_entries",
                "transactions",
                "liabilities",
                "receivables",
                "inventory_items",
                "assets",
                "credit_accounts",
                "people",
                "categories",
                "accounts",
            ]

            for table in tables:
                db.execute(f"DELETE FROM {table}")

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def tearDown(self):
        connection.DATABASE_PATH = self.original_db_path

    def create_account(self, name="Test Cash", account_type="CASH"):
        from services.account_service import create_account

        return create_account(name, account_type)

    def create_person(self, name="Test Person", person_type="PERSON"):
        from services.people_service import create_person

        return create_person(name, person_type)