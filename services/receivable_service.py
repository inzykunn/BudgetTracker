from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def create_receivable(
    person_id,
    description,
    original_amount,
    date_created,
    due_date=None,
    status="OPEN"
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO receivables (
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            )
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_receivable_by_id(receivable_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

    finally:
        connection.close()


def get_receivables():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            FROM receivables
            ORDER BY date_created DESC, id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def update_receivable(
    receivable_id,
    description,
    original_amount,
    date_created,
    due_date,
    status
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE receivables
            SET
                description = ?,
                original_amount = ?,
                date_created = ?,
                due_date = ?,
                status = ?
            WHERE id = ?
            """,
            (
                description,
                original_amount,
                date_created,
                due_date,
                status,
                receivable_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def close_receivable(receivable_id):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE receivables
            SET status = 'PAID'
            WHERE id = ?
            """,
            (receivable_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def record_receivable(
    date,
    description,
    account_id,
    person_id,
    amount,
    due_date=None
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO receivables (
                person_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'OPEN')
            """,
            (
                person_id,
                description,
                amount,
                date,
                due_date
            )
        )

        receivable_id = cursor.lastrowid

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "RECEIVABLE",
            None,
            [(account_id, -amount)]
        )

        connection.commit()

        return transaction_id, receivable_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_receivable_balance(receivable_id):
    connection = get_connection()

    try:
        receivable = connection.execute(
            """
            SELECT original_amount
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        return receivable[0] - paid

    finally:
        connection.close()

def record_receivable_payment(
    date,
    description,
    account_id,
    receivable_id,
    amount
):
    connection = get_connection()

    try:
        receivable = connection.execute(
            """
            SELECT original_amount
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        remaining = receivable[0] - paid

        if amount <= 0:
            raise ValueError("Payment must be greater than zero")

        if amount > remaining:
            raise ValueError("Payment exceeds remaining receivable")

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "RECEIVABLE_PAYMENT",
            None,
            [(account_id, amount)]
        )

        connection.execute(
            """
            INSERT INTO receivable_payments (
                receivable_id,
                transaction_id,
                amount,
                date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                receivable_id,
                transaction_id,
                amount,
                date
            )
        )

        new_remaining = remaining - amount

        if new_remaining == 0:
            connection.execute(
                """
                UPDATE receivables
                SET status = 'PAID'
                WHERE id = ?
                """,
                (receivable_id,)
            )

        connection.commit()

        return transaction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()