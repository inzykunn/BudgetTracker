from database.connection import get_connection


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