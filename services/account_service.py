from datetime import date

from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def get_account_by_name(name):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, is_active, created_at
            FROM accounts
            WHERE name = ?
            """,
            (name,)
        ).fetchone()
    finally:
        connection.close()


def get_account_by_id(account_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, is_active, created_at
            FROM accounts
            WHERE id = ?
            """,
            (account_id,)
        ).fetchone()
    finally:
        connection.close()


def create_account(name, account_type, opening_balance=None, opening_date=None):
    if opening_balance is not None:
        if isinstance(opening_balance, bool) or not isinstance(opening_balance, int):
            raise ValueError("Opening balance must be an integer.")
        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")

    if opening_date is None and opening_balance not in (None, 0):
        opening_date = date.today().isoformat()

    if opening_balance not in (None, 0):
        if not isinstance(opening_date, str) or not opening_date.strip():
            raise ValueError("Opening date must be provided.")

    connection = get_connection()

    try:
        existing_account = connection.execute(
            "SELECT id FROM accounts WHERE name = ?",
            (name,)
        ).fetchone()

        if existing_account:
            connection.rollback()
            return existing_account[0]

        cursor = connection.execute(
            """
            INSERT INTO accounts (name, type)
            VALUES (?, ?)
            """,
            (name, account_type)
        )

        account_id = cursor.lastrowid

        if opening_balance not in (None, 0):
            create_transaction_with_connection(
                connection,
                opening_date,
                f"Opening balance - {name}",
                "OPENING_BALANCE",
                None,
                [(account_id, opening_balance)]
            )

        connection.commit()
        return account_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_accounts():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, is_active, created_at
            FROM accounts
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()


def update_account(account_id, name, account_type):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE accounts
            SET name = ?, type = ?
            WHERE id = ?
            """,
            (name, account_type, account_id)
        )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def deactivate_account(account_id):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE accounts
            SET is_active = 0
            WHERE id = ?
            """,
            (account_id,)
        )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
