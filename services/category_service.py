from database.connection import get_connection


def create_category(name, category_type):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO categories (name, type)
            VALUES (?, ?)
            """,
            (name, category_type)
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_categories():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type
            FROM categories
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()


def get_category_by_id(category_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type
            FROM categories
            WHERE id = ?
            """,
            (category_id,)
        ).fetchone()

    finally:
        connection.close()