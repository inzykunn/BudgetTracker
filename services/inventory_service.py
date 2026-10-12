from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def create_inventory_item(
    name,
    purchase_cost,
    acquired_date,
    sale_price=None,
    sold_date=None,
    status="AVAILABLE",
    notes=None,
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO inventory_items (
                name,
                purchase_cost,
                acquired_date,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                purchase_cost,
                acquired_date,
                status,
            ),
        )

        item_id = cursor.lastrowid

        # Update optional fields only when provided.
        if sale_price is not None or sold_date is not None or notes is not None:
            connection.execute(
                """
                UPDATE inventory_items
                SET sale_price = ?, sold_date = ?, notes = ?
                WHERE id = ?
                """,
                (sale_price, sold_date, notes, item_id),
            )

        connection.commit()
        return item_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_inventory_item_by_id(item_id):
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                name,
                purchase_cost,
                sale_price,
                acquired_date,
                sold_date,
                status,
                notes
            FROM inventory_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

    finally:
        connection.close()


def get_inventory_items():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                name,
                purchase_cost,
                sale_price,
                acquired_date,
                sold_date,
                status,
                notes
            FROM inventory_items
            ORDER BY acquired_date DESC, id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def update_inventory_item(
    item_id,
    name,
    purchase_cost,
    acquired_date,
    sale_price=None,
    sold_date=None,
    status="AVAILABLE",
    notes=None,
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE inventory_items
            SET
                name = ?,
                purchase_cost = ?,
                acquired_date = ?,
                sale_price = ?,
                sold_date = ?,
                status = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                name,
                purchase_cost,
                acquired_date,
                sale_price,
                sold_date,
                status,
                notes,
                item_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def buy_inventory(
    date,
    description,
    account_id,
    name,
    purchase_cost,
    acquired_date,
    notes=None,
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO inventory_items (
                name,
                purchase_cost,
                acquired_date,
                status,
                notes
            )
            VALUES (?, ?, ?, 'AVAILABLE', ?)
            """,
            (
                name,
                purchase_cost,
                acquired_date,
                notes,
            ),
        )

        item_id = cursor.lastrowid

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "EXPENSE",
            None,
            [(account_id, -purchase_cost)],
        )

        connection.commit()

        return transaction_id, item_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def sell_inventory(
    date,
    description,
    account_id,
    item_id,
    sale_price,
    sold_date,
):
    connection = get_connection()

    try:
        item = connection.execute(
            """
            SELECT purchase_cost, status
            FROM inventory_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if not item:
            raise ValueError("Inventory item not found")

        if item[1] == "SOLD":
            raise ValueError("Inventory item is already sold")

        if sale_price <= 0:
            raise ValueError("Sale price must be greater than zero")

        connection.execute(
            """
            UPDATE inventory_items
            SET
                sale_price = ?,
                sold_date = ?,
                status = 'SOLD'
            WHERE id = ?
            """,
            (
                sale_price,
                sold_date,
                item_id,
            ),
        )

        transaction_id = create_transaction_with_connection(
            connection,
            date,
            description,
            "INCOME",
            None,
            [(account_id, sale_price)],
        )

        connection.commit()

        profit = sale_price - item[0]

        return transaction_id, profit

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def calculate_inventory_profit(item_id):
    connection = get_connection()

    try:
        item = connection.execute(
            """
            SELECT purchase_cost, sale_price, status
            FROM inventory_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if not item:
            raise ValueError("Inventory item not found")

        if item[1] is None:
            return 0

        return item[1] - item[0]

    finally:
        connection.close()