from database.connection import get_connection
from services.account_service import create_account, get_accounts
from services.category_service import create_category, get_categories
from services.transaction_service import create_transaction, get_transactions, get_account_balance
from services.people_service import create_person, get_people
from services.receivable_service import create_receivable, get_receivables
from services.liability_service import create_liability, get_liabilities
from services.credit_service import create_credit_account, get_credit_accounts


SCHEMA_PATH = "database/schema.sql"


def initialize_database():
    connection = get_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        connection.executescript(schema)
        connection.commit()

    finally:
        connection.close()


def main():
    initialize_database()

    cash_id = create_account("Cash", "CASH")
    gcash_id = create_account("GCash", "EWALLET")

    category_id = create_category("Test Income", "INCOME")

    transaction_id = create_transaction(
        "2026-10-04",
        "Test income",
        "INCOME",
        category_id,
        [(cash_id, 100000)]
    )

    person_id = create_person(
        "Mama",
        "PERSON",
        "Family"
    )

    receivable_id = create_receivable(
        person_id,
        "Borrowed money",
        150000,
        "2026-10-04"
    )

    liability_id = create_liability(
        "Test liability",
        50000,
        "2026-10-04"
    )

    credit_id = create_credit_account(
        "SPayLater",
        3000000
    )

    print("=== ACCOUNTS ===")
    print(get_accounts())

    print("\n=== CATEGORIES ===")
    print(get_categories())

    print("\n=== TRANSACTIONS ===")
    print(get_transactions())

    print("\n=== CASH BALANCE ===")
    print(get_account_balance(cash_id))

    print("\n=== PEOPLE ===")
    print(get_people())

    print("\n=== RECEIVABLES ===")
    print(get_receivables())

    print("\n=== LIABILITIES ===")
    print(get_liabilities())

    print("\n=== CREDIT ACCOUNTS ===")
    print(get_credit_accounts())

    print("\n=== CREATED IDS ===")
    print("Transaction:", transaction_id)
    print("Person:", person_id)
    print("Receivable:", receivable_id)
    print("Liability:", liability_id)
    print("Credit:", credit_id)


if __name__ == "__main__":
    main()