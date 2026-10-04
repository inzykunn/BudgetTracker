from database.connection import get_connection


def create_person(name, person_type, notes=None):
    existing_person = get_person_by_name(name)

    if existing_person:
        return existing_person[0]

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO people (name, type, notes)
            VALUES (?, ?, ?)
            """,
            (name, person_type, notes)
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_person_by_id(person_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, notes
            FROM people
            WHERE id = ?
            """,
            (person_id,)
        ).fetchone()

    finally:
        connection.close()


def get_person_by_name(name):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, notes
            FROM people
            WHERE name = ?
            """,
            (name,)
        ).fetchone()

    finally:
        connection.close()


def get_people():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, type, notes
            FROM people
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()


def update_person(person_id, name, person_type, notes=None):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE people
            SET name = ?, type = ?, notes = ?
            WHERE id = ?
            """,
            (name, person_type, notes, person_id)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()