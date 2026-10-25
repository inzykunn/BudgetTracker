from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def create_asset(
    name,
    category,
    purchase_cost,
    current_value,
    acquired_date,
    status="ACTIVE",
    notes=None,
):
    connection = get_connection()

    try:
        if purchase_cost < 0:
            raise ValueError("Purchase cost cannot be negative")

        if current_value < 0:
            raise ValueError("Current value cannot be negative")

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
                notes,
            ),
        )

        asset_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO asset_valuations (
                asset_id,
                valuation_date,
                value,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                asset_id,
                acquired_date,
                current_value,
                notes,
            ),
        )

        connection.commit()
        return asset_id

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
            (asset_id,),
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


def get_asset_valuation_history(asset_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                asset_id,
                valuation_date,
                value,
                notes,
                created_at
            FROM asset_valuations
            WHERE asset_id = ?
            ORDER BY valuation_date DESC, id DESC
            """,
            (asset_id,),
        ).fetchall()

    finally:
        connection.close()


def get_asset_value_as_of(asset_id, as_of_date):
    connection = get_connection()

    try:
        asset = connection.execute(
            """
            SELECT acquired_date
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

        if as_of_date < asset[0]:
            return None

        valuation = connection.execute(
            """
            SELECT value
            FROM asset_valuations
            WHERE asset_id = ?
              AND valuation_date <= ?
            ORDER BY valuation_date DESC, id DESC
            LIMIT 1
            """,
            (asset_id, as_of_date),
        ).fetchone()

        if not valuation:
            return None

        return valuation[0]

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
    notes=None,
):
    connection = get_connection()

    try:
        if purchase_cost < 0:
            raise ValueError("Purchase cost cannot be negative")

        if current_value < 0:
            raise ValueError("Current value cannot be negative")

        asset = connection.execute(
            """
            SELECT id
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

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
                asset_id,
            ),
        )

        existing_valuation = connection.execute(
            """
            SELECT id
            FROM asset_valuations
            WHERE asset_id = ?
              AND valuation_date = ?
            """,
            (asset_id, acquired_date),
        ).fetchone()

        if not existing_valuation:
            connection.execute(
                """
                INSERT INTO asset_valuations (
                    asset_id,
                    valuation_date,
                    value,
                    notes
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    asset_id,
                    acquired_date,
                    current_value,
                    notes,
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_asset_value(asset_id, current_value, valuation_date=None, notes=None):
    connection = get_connection()

    try:
        if current_value < 0:
            raise ValueError("Current value cannot be negative")

        asset = connection.execute(
            """
            SELECT acquired_date
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

        if valuation_date is None:
            valuation_date = asset[0]

        if valuation_date < asset[0]:
            raise ValueError(
                "Valuation date cannot be before the acquisition date"
            )

        connection.execute(
            """
            INSERT INTO asset_valuations (
                asset_id,
                valuation_date,
                value,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                asset_id,
                valuation_date,
                current_value,
                notes,
            ),
        )

        latest_valuation = connection.execute(
            """
            SELECT value
            FROM asset_valuations
            WHERE asset_id = ?
            ORDER BY valuation_date DESC, id DESC
            LIMIT 1
            """,
            (asset_id,),
        ).fetchone()

        connection.execute(
            """
            UPDATE assets
            SET current_value = ?
            WHERE id = ?
            """,
            (latest_valuation[0], asset_id),
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
            (asset_id,),
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

        if asset[0] in ("DISPOSED", "SOLD"):
            raise ValueError("Asset is already disposed or sold")

        connection.execute(
            """
            UPDATE assets
            SET status = 'DISPOSED'
            WHERE id = ?
            """,
            (asset_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def buy_asset(
    date,
    description,
    account_id,
    name,
    category,
    purchase_cost,
    acquired_date,
    current_value=None,
    notes=None,
):
    connection = get_connection()

    try:
        if purchase_cost <= 0:
            raise ValueError("Purchase cost must be greater than zero")

        if current_value is None:
            current_value = purchase_cost

        if current_value < 0:
            raise ValueError("Current value cannot be negative")

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
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?)
            """,
            (
                name,
                category,
                purchase_cost,
                current_value,
                acquired_date,
                notes,
            ),
        )

        asset_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO asset_valuations (
                asset_id,
                valuation_date,
                value,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                asset_id,
                acquired_date,
                current_value,
                notes,
            ),
        )

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "ASSET_PURCHASE",
            None,
            [(account_id, -purchase_cost)],
        )

        connection.commit()

        return transaction_id, asset_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def sell_asset(
    date,
    description,
    account_id,
    asset_id,
    sale_price,
    sold_date,
):
    connection = get_connection()

    try:
        asset = connection.execute(
            """
            SELECT current_value, status
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()

        if not asset:
            raise ValueError("Asset not found")

        if asset[1] in ("DISPOSED", "SOLD"):
            raise ValueError("Asset is already disposed or sold")

        if sale_price <= 0:
            raise ValueError("Sale price must be greater than zero")

        connection.execute(
            """
            UPDATE assets
            SET status = 'SOLD'
            WHERE id = ?
            """,
            (asset_id,),
        )

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "ASSET_SALE",
            None,
            [(account_id, sale_price)],
        )

        connection.commit()

        profit = sale_price - asset[0]

        return transaction_id, profit

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()