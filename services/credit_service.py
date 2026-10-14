from database.connection import get_connection


def _validate_credit_account(name, credit_limit):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Credit account name is required")
    if not isinstance(credit_limit, int) or isinstance(credit_limit, bool) or credit_limit < 0:
        raise ValueError("Credit limit must be a non-negative integer")


def create_credit_account(name, credit_limit):
    _validate_credit_account(name, credit_limit)
    name = name.strip()
    existing_account = get_credit_account_by_name(name)

    if existing_account:
        return existing_account[0]

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO credit_accounts (name, credit_limit)
            VALUES (?, ?)
            """,
            (name, credit_limit)
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_credit_account_by_id(credit_account_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, credit_limit, is_active
            FROM credit_accounts
            WHERE id = ?
            """,
            (credit_account_id,)
        ).fetchone()

    finally:
        connection.close()


def get_credit_account_by_name(name):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, credit_limit, is_active
            FROM credit_accounts
            WHERE name = ?
            """,
            (name,)
        ).fetchone()

    finally:
        connection.close()


def get_credit_accounts():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, credit_limit, is_active
            FROM credit_accounts
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()


def update_credit_account(credit_account_id, name, credit_limit):
    _validate_credit_account(name, credit_limit)
    name = name.strip()
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE credit_accounts
            SET name = ?, credit_limit = ?
            WHERE id = ?
            """,
            (name, credit_limit, credit_account_id)
        )
        if cursor.rowcount == 0:
            raise ValueError("Credit account not found")
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def deactivate_credit_account(credit_account_id):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE credit_accounts
            SET is_active = 0
            WHERE id = ?
            """,
            (credit_account_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError("Credit account not found")
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()