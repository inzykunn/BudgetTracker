from database.connection import get_connection


def record_income(date, description, account_id, amount, category_id=None):
    return _create_transaction(
        date,
        description,
        "INCOME",
        category_id,
        [(account_id, amount)]
    )


def record_expense(date, description, account_id, amount, category_id=None):
    return _create_transaction(
        date,
        description,
        "EXPENSE",
        category_id,
        [(account_id, -amount)]
    )


def record_transfer(date, description, from_account_id, to_account_id, amount):
    return _create_transaction(
        date,
        description,
        "TRANSFER",
        None,
        [
            (from_account_id, -amount),
            (to_account_id, amount)
        ]
    )


def _create_transaction(date, description, transaction_type, category_id, entries):
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