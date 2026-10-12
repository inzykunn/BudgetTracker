from services.transaction_service import create_transaction


def record_income(date, description, account_id, amount, category_id=None):
    return create_transaction(
        date,
        description,
        "INCOME",
        category_id,
        [(account_id, amount)]
    )


def record_expense(date, description, account_id, amount, category_id=None):
    return create_transaction(
        date,
        description,
        "EXPENSE",
        category_id,
        [(account_id, -amount)]
    )


def record_transfer(date, description, from_account_id, to_account_id, amount):
    return create_transaction(
        date,
        description,
        "TRANSFER",
        None,
        [
            (from_account_id, -amount),
            (to_account_id, amount)
        ]
    )