from datetime import date
from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def _validate_positive_amount(amount, field_name):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError(f"{field_name} must be a positive integer")


def _record_receivable_balance(
    connection,
    receivable_id,
    effective_date,
    outstanding_amount,
    status,
    notes=None
):
    connection.execute(
        """
        INSERT INTO receivable_balance_history (
            receivable_id,
            effective_date,
            outstanding_amount,
            status,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            receivable_id,
            effective_date,
            outstanding_amount,
            status,
            notes
        )
    )


def create_receivable(
    person_id,
    description,
    original_amount,
    date_created,
    due_date=None,
    status="OPEN"
):
    _validate_positive_amount(original_amount, "Original amount")

    if status not in ("OPEN", "PAID"):
        raise ValueError("Invalid receivable status")

    if status == "PAID":
        outstanding_amount = 0
    else:
        outstanding_amount = original_amount

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

        receivable_id = cursor.lastrowid

        _record_receivable_balance(
            connection,
            receivable_id,
            date_created,
            outstanding_amount,
            status,
            "Receivable created"
        )

        connection.commit()
        return receivable_id

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


def get_receivable_balance_history(receivable_id):
    connection = get_connection()

    try:
        receivable = connection.execute(
            "SELECT id FROM receivables WHERE id = ?",
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        return connection.execute(
            """
            SELECT
                id,
                receivable_id,
                effective_date,
                outstanding_amount,
                status,
                notes,
                created_at
            FROM receivable_balance_history
            WHERE receivable_id = ?
            ORDER BY effective_date DESC, id DESC
            """,
            (receivable_id,)
        ).fetchall()

    finally:
        connection.close()


def get_receivable_balance_as_of(receivable_id, as_of_date):
    connection = get_connection()

    try:
        receivable = connection.execute(
            """
            SELECT date_created
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        if as_of_date < receivable[0]:
            return None

        balance = connection.execute(
            """
            SELECT outstanding_amount
            FROM receivable_balance_history
            WHERE receivable_id = ?
              AND effective_date <= ?
            ORDER BY effective_date DESC, id DESC
            LIMIT 1
            """,
            (receivable_id, as_of_date)
        ).fetchone()

        if not balance:
            return None

        return balance[0]

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
    _validate_positive_amount(original_amount, "Original amount")

    if status not in ("OPEN", "PAID"):
        raise ValueError("Invalid receivable status")

    connection = get_connection()

    try:
        receivable = connection.execute(
            """
            SELECT date_created
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        if date_created != receivable[0]:
            raise ValueError("The creation date cannot be changed")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        if original_amount < paid:
            raise ValueError("Original amount cannot be less than payments received")

        remaining = original_amount - paid

        if status == "PAID" and remaining != 0:
            raise ValueError("Receivable cannot be marked paid while a balance remains")

        if remaining == 0:
            effective_status = "PAID"
        else:
            effective_status = "OPEN"

        connection.execute(
            """
            UPDATE receivables
            SET
                description = ?,
                original_amount = ?,
                due_date = ?,
                status = ?
            WHERE id = ?
            """,
            (
                description,
                original_amount,
                due_date,
                effective_status,
                receivable_id
            )
        )

        latest_payment_date = connection.execute(
            "SELECT MAX(date) FROM receivable_payments WHERE receivable_id = ?",
            (receivable_id,),
        ).fetchone()[0]
        latest_history_date = connection.execute(
            "SELECT MAX(effective_date) FROM receivable_balance_history WHERE receivable_id = ?",
            (receivable_id,),
        ).fetchone()[0]
        effective_date = max(
            value for value in (date.today().isoformat(), latest_payment_date, latest_history_date)
            if value is not None
        )
        connection.execute(
            """
            INSERT INTO receivable_balance_history (
                receivable_id, effective_date, outstanding_amount, status, notes
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(receivable_id, effective_date) DO UPDATE SET
                outstanding_amount = excluded.outstanding_amount,
                status = excluded.status,
                notes = excluded.notes
            """,
            (receivable_id, effective_date, remaining, effective_status, "Receivable updated"),
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
        receivable = connection.execute(
            """
            SELECT date_created, status
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        if receivable[1] == "PAID":
            return

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        original_amount = connection.execute(
            """
            SELECT original_amount
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        remaining = original_amount - paid

        if remaining != 0:
            raise ValueError("Receivable cannot be closed while a balance remains")

        latest_payment = connection.execute(
            """
            SELECT MAX(date)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        effective_date = latest_payment or receivable[0]

        connection.execute(
            """
            UPDATE receivables
            SET status = 'PAID'
            WHERE id = ?
            """,
            (receivable_id,)
        )

        _record_receivable_balance(
            connection,
            receivable_id,
            effective_date,
            0,
            "PAID",
            "Receivable closed"
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
    _validate_positive_amount(amount, "Receivable amount")

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

        _record_receivable_balance(
            connection,
            receivable_id,
            date,
            amount,
            "OPEN",
            "Receivable recorded"
        )

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
    _validate_positive_amount(amount, "Payment amount")

    connection = get_connection()

    try:
        receivable = connection.execute(
            """
            SELECT original_amount, date_created, status
            FROM receivables
            WHERE id = ?
            """,
            (receivable_id,)
        ).fetchone()

        if not receivable:
            raise ValueError("Receivable not found")

        original_amount, date_created, status = receivable

        if date < date_created:
            raise ValueError("Payment date cannot be before receivable creation")

        if status == "PAID":
            raise ValueError("Receivable is already paid")

        paid = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM receivable_payments
            WHERE receivable_id = ?
            """,
            (receivable_id,)
        ).fetchone()[0]

        remaining = original_amount - paid

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
        new_status = "PAID" if new_remaining == 0 else "OPEN"

        connection.execute(
            """
            UPDATE receivables
            SET status = ?
            WHERE id = ?
            """,
            (new_status, receivable_id)
        )

        _record_receivable_balance(
            connection,
            receivable_id,
            date,
            new_remaining,
            new_status,
            "Payment received"
        )

        connection.commit()

        return transaction_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()