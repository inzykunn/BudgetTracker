from database.connection import get_connection


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