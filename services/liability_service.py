from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def create_liability(
    description,
    original_amount,
    date_created,
    person_id=None,
    credit_account_id=None,
    due_date=None,
    status="OPEN"
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO liabilities (
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                credit_account_id,
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


def get_liability_by_id(liability_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,)
        ).fetchone()

    finally:
        connection.close()


def get_liabilities():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            FROM liabilities
            ORDER BY date_created DESC, id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def update_liability(
    liability_id,
    description,
    original_amount,
    date_created,
    person_id=None,
    credit_account_id=None,
    due_date=None,
    status="OPEN"
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE liabilities
            SET
                person_id = ?,
                credit_account_id = ?,
                description = ?,
                original_amount = ?,
                date_created = ?,
                due_date = ?,
                status = ?
            WHERE id = ?
            """,
            (
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status,
                liability_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def close_liability(liability_id):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE liabilities
            SET status = 'PAID'
            WHERE id = ?
            """,
            (liability_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def record_liability(
    date,
    description,
    account_id,
    amount,
    person_id=None,
    credit_account_id=None,
    due_date=None
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO liabilities (
                person_id,
                credit_account_id,
                description,
                original_amount,
                date_created,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'OPEN')
            """,
            (
                person_id,
                credit_account_id,
                description,
                amount,
                date,
                due_date
            )
        )

        liability_id = cursor.lastrowid

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "LIABILITY",
            None,
            [(account_id, amount)]
        )

        connection.commit()

        return transaction_id, liability_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def record_liability_payment(
    date,
    description,
    account_id,
    liability_id,
    amount
):
    connection = get_connection()

    try:
        liability = connection.execute(
            """
            SELECT
                original_amount,
                status
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,)
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        if liability[1] == "PAID":
            raise ValueError("Liability is already paid")

        if amount <= 0:
            raise ValueError("Payment must be greater than zero")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,)
        ).fetchone()[0]

        remaining = liability[0] - paid

        if amount > remaining:
            raise ValueError("Payment exceeds remaining liability")

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "LIABILITY_PAYMENT",
            None,
            [(account_id, -amount)]
        )

        connection.execute(
            """
            INSERT INTO liability_payments (
                liability_id,
                transaction_id,
                amount,
                date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                liability_id,
                transaction_id,
                amount,
                date
            )
        )

        new_remaining = remaining - amount

        if new_remaining == 0:
            connection.execute(
                """
                UPDATE liabilities
                SET status = 'PAID'
                WHERE id = ?
                """,
                (liability_id,)
            )

        connection.commit()

        return transaction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_liability_balance(liability_id):
    connection = get_connection()

    try:
        liability = connection.execute(
            """
            SELECT original_amount
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,)
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,)
        ).fetchone()[0]

        return liability[0] - paid

    finally:
        connection.close()