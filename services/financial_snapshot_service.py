import json
from datetime import date

from database.connection import get_connection


SNAPSHOT_TABLES = (
    "accounts",
    "assets",
    "asset_valuations",
    "inventory_items",
    "receivables",
    "receivable_payments",
    "receivable_balance_history",
    "liabilities",
    "liability_payments",
    "liability_balance_history",
    "credit_accounts",
)


def _ensure_snapshot_table(connection):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS financial_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            snapshot_date DATE NOT NULL,
            notes TEXT,
            finalized INTEGER NOT NULL DEFAULT 0 CHECK (finalized IN (0, 1)),
            data_json TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_financial_snapshots_date "
        "ON financial_snapshots(snapshot_date DESC, id DESC)"
    )


def _table_rows(connection, table):
    rows = connection.execute(f'SELECT * FROM "{table}" ORDER BY id').fetchall()
    columns = [item[1] for item in connection.execute(f'PRAGMA table_info("{table}")')]
    return [dict(zip(columns, row)) for row in rows]


def _capture_snapshot(connection):
    data = {table: _table_rows(connection, table) for table in SNAPSHOT_TABLES}
    data["account_balances"] = connection.execute(
        """
        SELECT a.id, a.name, a.type, a.is_active,
               COALESCE(SUM(te.amount), 0) AS balance
        FROM accounts a
        LEFT JOIN transaction_entries te ON te.account_id = a.id
        GROUP BY a.id, a.name, a.type, a.is_active
        ORDER BY a.id
        """
    ).fetchall()
    data["account_balances"] = [
        {"id": row[0], "name": row[1], "type": row[2], "is_active": row[3], "balance": row[4]}
        for row in data["account_balances"]
    ]
    data["transactions"] = _table_rows(connection, "transactions")
    data["transaction_entries"] = _table_rows(connection, "transaction_entries")
    return data


def create_snapshot(name, snapshot_date=None, notes=None, finalized=False):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Snapshot name is required")
    snapshot_date = snapshot_date or date.today().isoformat()
    if not isinstance(snapshot_date, str) or len(snapshot_date) != 10:
        raise ValueError("Snapshot date must use YYYY-MM-DD format")
    try:
        date.fromisoformat(snapshot_date)
    except ValueError as exc:
        raise ValueError("Snapshot date must use YYYY-MM-DD format") from exc

    connection = get_connection()
    try:
        _ensure_snapshot_table(connection)
        snapshot_data = _capture_snapshot(connection)
        cursor = connection.execute(
            """INSERT INTO financial_snapshots
               (name, snapshot_date, notes, finalized, data_json)
               VALUES (?, ?, ?, ?, ?)""",
            (name.strip(), snapshot_date, notes, int(bool(finalized)), json.dumps(snapshot_data, ensure_ascii=False)),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_snapshot(snapshot_id):
    connection = get_connection()
    try:
        _ensure_snapshot_table(connection)
        row = connection.execute(
            """SELECT id, name, snapshot_date, notes, finalized, created_at, data_json
               FROM financial_snapshots WHERE id = ?""",
            (snapshot_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Financial snapshot {snapshot_id} was not found")
        return {
            "id": row[0],
            "name": row[1],
            "snapshot_date": row[2],
            "notes": row[3],
            "finalized": bool(row[4]),
            "created_at": row[5],
            "data": json.loads(row[6]),
        }
    finally:
        connection.close()


def list_snapshots():
    connection = get_connection()
    try:
        _ensure_snapshot_table(connection)
        rows = connection.execute(
            """SELECT id, name, snapshot_date, notes, finalized, created_at
               FROM financial_snapshots ORDER BY snapshot_date DESC, id DESC"""
        ).fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "snapshot_date": row[2],
                "notes": row[3],
                "finalized": bool(row[4]),
                "created_at": row[5],
            }
            for row in rows
        ]
    finally:
        connection.close()


def finalize_snapshot(snapshot_id):
    connection = get_connection()
    try:
        _ensure_snapshot_table(connection)
        cursor = connection.execute(
            "UPDATE financial_snapshots SET finalized = 1 WHERE id = ?",
            (snapshot_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Financial snapshot {snapshot_id} was not found")
        connection.commit()
        return get_snapshot(snapshot_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
