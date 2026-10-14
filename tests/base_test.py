import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import connection


class BaseDatabaseTest(unittest.TestCase):

    def setUp(self):
        self.original_db_path = connection.DATABASE_PATH
        temporary_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temporary_file.close()
        self.test_db_path = Path(temporary_file.name)
        connection.DATABASE_PATH = self.test_db_path
        schema_path = connection.BASE_DIR / "database" / "schema.sql"
        db = sqlite3.connect(self.test_db_path)

        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.executescript(schema_path.read_text(encoding="utf-8"))
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def tearDown(self):
        connection.DATABASE_PATH = self.original_db_path
        self.test_db_path.unlink(missing_ok=True)

    def create_account(self, name="Test Cash", account_type="CASH"):
        from services.account_service import create_account

        return create_account(name, account_type)

    def create_person(self, name="Test Person", person_type="PERSON"):
        from services.people_service import create_person

        return create_person(name, person_type)