from database.connection import get_connection


def create_transaction(date, description, transaction_type, category_id, entries):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO transactions (
                date,
                description,
                type,
                category_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (date, description, transaction_type, category_id)
        )

        transaction_id = cursor.lastrowid

        for account_id, amount in entries:
            connection.execute(
                """
                INSERT INTO transaction_entries (
                    transaction_id,
                    account_id,
                    amount
                )
                VALUES (?, ?, ?)
                """,
                (transaction_id, account_id, amount)
            )

        connection.commit()
        return transaction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_transaction_by_id(transaction_id):
    connection = get_connection()

    try:
        transaction = connection.execute(
            """
            SELECT
                id,
                date,
                description,
                type,
                category_id,
                created_at
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,)
        ).fetchone()

        entries = connection.execute(
            """
            SELECT
                id,
                account_id,
                amount
            FROM transaction_entries
            WHERE transaction_id = ?
            ORDER BY id
            """,
            (transaction_id,)
        ).fetchall()

        return transaction, entries

    finally:
        connection.close()


def get_transactions():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                date,
                description,
                type,
                category_id,
                created_at
            FROM transactions
            ORDER BY date DESC, id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def get_account_balance(account_id):
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM transaction_entries
            WHERE account_id = ?
            """,
            (account_id,)
        ).fetchone()

        return result[0]

    finally:
        connection.close()