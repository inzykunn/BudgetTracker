from database.connection import get_connection
from services.account_service import create_account, get_account_by_name
from services.category_service import create_category
from services.transaction_service import create_transaction, get_account_balance


SCHEMA_PATH = "database/schema.sql"


def initialize_database():
    connection = get_connection()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)
    connection.commit()
    connection.close()


def main():
    initialize_database()

    cash_id = create_account("Cash", "CASH")
    category_id = create_category("Test Income", "INCOME")

    transaction_id = create_transaction(
        "2026-10-04",
        "Test transaction",
        "INCOME",
        category_id,
        [(cash_id, 100000)]
    )

    balance = get_account_balance(cash_id)

    print("Transaction ID:", transaction_id)
    print("Cash balance:", balance)


if __name__ == "__main__":
    main()