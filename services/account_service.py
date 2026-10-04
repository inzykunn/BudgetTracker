from database.connection import get_connection


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


def create_account(name, account_type):
    existing_account = get_account_by_name(name)

    if existing_account:
        return existing_account[0]

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO accounts (name, type)
            VALUES (?, ?)
            """,
            (name, account_type)
        )

        connection.commit()
        return cursor.lastrowid
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