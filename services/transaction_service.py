from database.connection import get_connection


def create_transaction(
    date,
    description,
    transaction_type,
    category_id,
    entries,
):
    connection = get_connection()

    try:
        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            transaction_type,
            category_id,
            entries,
        )

        connection.commit()

        return transaction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def create_transaction_with_connection(
    connection,
    date,
    description,
    transaction_type,
    category_id,
    entries,
):
    if not date:
        raise ValueError("Transaction date is required")

    if not description or not description.strip():
        raise ValueError("Transaction description is required")

    if not transaction_type or not transaction_type.strip():
        raise ValueError("Transaction type is required")

    if entries is None:
        raise ValueError("Transaction entries are required")

    entries = list(entries)

    if not entries:
        raise ValueError(
            "A transaction must contain at least one entry"
        )

    validated_entries = []

    for entry in entries:
        if not isinstance(entry, (tuple, list)) or len(entry) != 2:
            raise ValueError(
                "Each entry must contain an account ID and amount"
            )

        account_id, amount = entry

        if account_id is None:
            raise ValueError(
                "Account ID is required for each entry"
            )

        if not isinstance(amount, int) or isinstance(amount, bool):
            raise ValueError("Entry amount must be an integer")

        if amount == 0:
            raise ValueError("Entry amount cannot be zero")

        validated_entries.append((account_id, amount))

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
        (
            date,
            description.strip(),
            transaction_type.strip(),
            category_id,
        ),
    )

    transaction_id = cursor.lastrowid

    for account_id, amount in validated_entries:
        connection.execute(
            """
            INSERT INTO transaction_entries (
                transaction_id,
                account_id,
                amount
            )
            VALUES (?, ?, ?)
            """,
            (
                transaction_id,
                account_id,
                amount,
            ),
        )

    return transaction_id


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
            (transaction_id,),
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
            (transaction_id,),
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


def get_transactions_as_of(as_of_date):
    if not as_of_date:
        raise ValueError("Historical date is required")

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
            WHERE date <= ?
            ORDER BY date DESC, id DESC
            """,
            (as_of_date,),
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
            (account_id,),
        ).fetchone()

        return result[0]

    finally:
        connection.close()


def get_account_balance_as_of(account_id, as_of_date):
    if not as_of_date:
        raise ValueError("Historical date is required")

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(SUM(te.amount), 0)
            FROM transaction_entries AS te
            JOIN transactions AS t
                ON t.id = te.transaction_id
            WHERE te.account_id = ?
              AND t.date <= ?
            """,
            (
                account_id,
                as_of_date,
            ),
        ).fetchone()

        return result[0]

    finally:
        connection.close()