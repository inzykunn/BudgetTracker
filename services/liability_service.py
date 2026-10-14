from datetime import date
from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def _record_liability_balance(
    connection,
    liability_id,
    effective_date,
    outstanding_amount,
    status,
    notes=None,
):
    connection.execute(
        """
        INSERT INTO liability_balance_history (
            liability_id,
            effective_date,
            outstanding_amount,
            status,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            liability_id,
            effective_date,
            outstanding_amount,
            status,
            notes,
        ),
    )


def create_liability(
    description,
    original_amount,
    date_created,
    person_id=None,
    credit_account_id=None,
    due_date=None,
    status="OPEN",
):
    connection = get_connection()

    try:
        if not isinstance(original_amount, int) or isinstance(original_amount, bool) or original_amount <= 0:
            raise ValueError("Original amount must be a positive integer")
        if status != "OPEN":
            raise ValueError("A liability must be paid through recorded payments")

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
                status,
            ),
        )

        liability_id = cursor.lastrowid

        _record_liability_balance(
            connection,
            liability_id,
            date_created,
            original_amount,
            status,
        )

        connection.commit()
        return liability_id

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
            (liability_id,),
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


def get_liability_balance_history(liability_id):
    connection = get_connection()

    try:
        liability = connection.execute(
            "SELECT id FROM liabilities WHERE id = ?",
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        return connection.execute(
            """
            SELECT
                id,
                liability_id,
                effective_date,
                outstanding_amount,
                status,
                notes,
                created_at
            FROM liability_balance_history
            WHERE liability_id = ?
            ORDER BY effective_date DESC, id DESC
            """,
            (liability_id,),
        ).fetchall()

    finally:
        connection.close()


def get_liability_balance_as_of(liability_id, as_of_date):
    connection = get_connection()

    try:
        liability = connection.execute(
            """
            SELECT date_created
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        if as_of_date < liability[0]:
            return None

        history = connection.execute(
            """
            SELECT outstanding_amount
            FROM liability_balance_history
            WHERE liability_id = ?
              AND effective_date <= ?
            ORDER BY effective_date DESC, id DESC
            LIMIT 1
            """,
            (liability_id, as_of_date),
        ).fetchone()

        if history:
            return history[0]

        return None

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
    status="OPEN",
):
    connection = get_connection()

    try:
        if not isinstance(original_amount, int) or isinstance(original_amount, bool) or original_amount <= 0:
            raise ValueError("Original amount must be a positive integer")

        if status not in ("OPEN", "PAID"):
            raise ValueError("Invalid liability status")

        liability = connection.execute(
            "SELECT date_created FROM liabilities WHERE id = ?",
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")
        if date_created != liability[0]:
            raise ValueError("The creation date cannot be changed")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,),
        ).fetchone()[0]

        if original_amount < paid:
            raise ValueError(
                "Original amount cannot be less than payments already made"
            )

        remaining = original_amount - paid
        if status == "PAID" and remaining != 0:
            raise ValueError("Liability cannot be marked paid while a balance remains")
        effective_status = "PAID" if remaining == 0 else "OPEN"

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
                effective_status,
                liability_id,
            ),
        )

        latest_payment_date = connection.execute(
            "SELECT MAX(date) FROM liability_payments WHERE liability_id = ?",
            (liability_id,),
        ).fetchone()[0]
        latest_history_date = connection.execute(
            "SELECT MAX(effective_date) FROM liability_balance_history WHERE liability_id = ?",
            (liability_id,),
        ).fetchone()[0]
        effective_date = max(
            value for value in (date.today().isoformat(), latest_payment_date, latest_history_date)
            if value is not None
        )
        connection.execute(
            """
            INSERT INTO liability_balance_history (
                liability_id, effective_date, outstanding_amount, status, notes
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(liability_id, effective_date) DO UPDATE SET
                outstanding_amount = excluded.outstanding_amount,
                status = excluded.status,
                notes = excluded.notes
            """,
            (liability_id, effective_date, remaining, effective_status, "Liability updated"),
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
        liability = connection.execute(
            """
            SELECT original_amount, date_created, status
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,),
        ).fetchone()[0]

        remaining = liability[0] - paid

        if remaining != 0:
            raise ValueError(
                "Liability cannot be closed while a balance remains"
            )

        if liability[2] == "PAID":
            return

        connection.execute(
            """
            UPDATE liabilities
            SET status = 'PAID'
            WHERE id = ?
            """,
            (liability_id,),
        )

        latest_date = connection.execute(
            """
            SELECT MAX(date)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,),
        ).fetchone()[0]

        effective_date = latest_date or liability[1]

        _record_liability_balance(
            connection,
            liability_id,
            effective_date,
            0,
            "PAID",
            "Liability closed",
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
    due_date=None,
):
    connection = get_connection()

    try:
        if amount <= 0:
            raise ValueError("Liability amount must be greater than zero")

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
                due_date,
            ),
        )

        liability_id = cursor.lastrowid

        _record_liability_balance(
            connection,
            liability_id,
            date,
            amount,
            "OPEN",
        )

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "LIABILITY",
            None,
            [(account_id, amount)],
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
    amount,
):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Payment amount must be a positive integer")

    connection = get_connection()

    try:
        liability = connection.execute(
            """
            SELECT original_amount, date_created, status
            FROM liabilities
            WHERE id = ?
            """,
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        if liability[2] == "PAID":
            raise ValueError("Liability is already paid")

        if date < liability[1]:
            raise ValueError(
                "Payment date cannot be before liability creation"
            )

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,),
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
            [(account_id, -amount)],
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
                date,
            ),
        )

        new_remaining = remaining - amount
        new_status = "PAID" if new_remaining == 0 else "OPEN"

        connection.execute(
            """
            UPDATE liabilities
            SET status = ?
            WHERE id = ?
            """,
            (new_status, liability_id),
        )

        _record_liability_balance(
            connection,
            liability_id,
            date,
            new_remaining,
            new_status,
            "Liability payment",
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
            (liability_id,),
        ).fetchone()

        if not liability:
            raise ValueError("Liability not found")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM liability_payments
            WHERE liability_id = ?
            """,
            (liability_id,),
        ).fetchone()[0]

        return liability[0] - paid

    finally:
        connection.close()