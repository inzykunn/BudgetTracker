from database.connection import get_connection
from services.transaction_service import create_transaction_with_connection


def _validate_amount(amount, field_name, allow_zero=False):
    minimum = 0 if allow_zero else 1
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < minimum:
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{field_name} must be a {qualifier} integer")


def create_inventory_item(
    name,
    purchase_cost,
    acquired_date,
    sale_price=None,
    sold_date=None,
    status="AVAILABLE",
    notes=None,
):
    _validate_amount(purchase_cost, "Purchase cost")
    if status not in ("AVAILABLE", "SOLD"):
        raise ValueError("Invalid inventory status")
    if status == "SOLD":
        _validate_amount(sale_price, "Sale price")
        if not sold_date:
            raise ValueError("Sold date is required for sold inventory")
    elif sale_price is not None or sold_date is not None:
        raise ValueError("Sale details require SOLD status")

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
    _validate_amount(purchase_cost, "Purchase cost")
    if status != "AVAILABLE":
        raise ValueError("Use sell_inventory to mark an item as sold")
    if sale_price is not None or sold_date is not None:
        raise ValueError("Use sell_inventory to record sale details")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE inventory_items
            SET name = ?, purchase_cost = ?, acquired_date = ?, notes = ?
            WHERE id = ? AND status = 'AVAILABLE'
            """,
            (name, purchase_cost, acquired_date, notes, item_id),
        )
        if cursor.rowcount == 0:
            exists = connection.execute(
                "SELECT id FROM inventory_items WHERE id = ?", (item_id,)
            ).fetchone()
            if not exists:
                raise ValueError("Inventory item not found")
            raise ValueError("Sold inventory items cannot be edited")
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
    _validate_amount(purchase_cost, "Purchase cost")
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
    _validate_amount(sale_price, "Sale price")
    connection = get_connection()

    try:
        item = connection.execute(
            """
            SELECT purchase_cost, status, acquired_date
            FROM inventory_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if not item:
            raise ValueError("Inventory item not found")

        if item[1] != "AVAILABLE":
            raise ValueError("Inventory item is not available for sale")
        if sold_date < item[2]:
            raise ValueError("Sold date cannot be before the acquisition date")

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

        if item[2] != "SOLD" or item[1] is None:
            return 0

        return item[1] - item[0]

    finally:
        connection.close()