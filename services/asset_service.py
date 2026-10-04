from database.connection import get_connection


def create_asset(
    name,
    category,
    purchase_cost,
    current_value,
    acquired_date,
    status="ACTIVE",
    notes=None
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO assets (
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes
            )
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_asset_by_id(asset_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes
            FROM assets
            WHERE id = ?
            """,
            (asset_id,)
        ).fetchone()

    finally:
        connection.close()


def get_assets():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes
            FROM assets
            ORDER BY acquired_date DESC, id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def update_asset(
    asset_id,
    name,
    category,
    purchase_cost,
    current_value,
    acquired_date,
    status,
    notes=None
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE assets
            SET
                name = ?,
                category = ?,
                purchase_cost = ?,
                current_value = ?,
                acquired_date = ?,
                status = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                status,
                notes,
                asset_id
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_asset_value(asset_id, current_value):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE assets
            SET current_value = ?
            WHERE id = ?
            """,
            (current_value, asset_id)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def dispose_asset(asset_id):
    connection = get_connection()

    try:
        asset = connection.execute(
            """
            SELECT status
            FROM assets
            WHERE id = ?
            """,
            (asset_id,)
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

        if asset[0] == "DISPOSED":
            raise ValueError("Asset is already disposed")

        connection.execute(
            """
            UPDATE assets
            SET status = 'DISPOSED'
            WHERE id = ?
            """,
            (asset_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()