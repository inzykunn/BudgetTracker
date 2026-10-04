from database.connection import get_connection
from services.account_service import (
    create_account,
    get_accounts,
    get_account_by_id,
    get_account_by_name,
    update_account,
    deactivate_account
)

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
    gcash_id = create_account("GCash", "EWALLET")

    print("All accounts:")
    print(get_accounts())

    print("\nCash by ID:")
    print(get_account_by_id(cash_id))

    print("\nGCash by name:")
    print(get_account_by_name("GCash"))

    update_account(gcash_id, "GCash", "EWALLET")

    print("\nAfter update:")
    print(get_account_by_id(gcash_id))

    deactivate_account(gcash_id)

    print("\nAfter deactivation:")
    print(get_account_by_id(gcash_id))


if __name__ == "__main__":
    main()