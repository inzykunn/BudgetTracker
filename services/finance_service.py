from services.transaction_service import create_transaction


def record_income(date, description, account_id, amount, category_id=None):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Income amount must be a positive integer")

    return create_transaction(
        date,
        description,
        "INCOME",
        category_id,
        [(account_id, amount)],
    )


def record_expense(date, description, account_id, amount, category_id=None):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Expense amount must be a positive integer")

    return create_transaction(
        date,
        description,
        "EXPENSE",
        category_id,
        [(account_id, -amount)],
    )


def record_transfer(date, description, from_account_id, to_account_id, amount):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Transfer amount must be a positive integer")

    if from_account_id == to_account_id:
        raise ValueError("Source and destination accounts must be different")

    return create_transaction(
        date,
        description,
        "TRANSFER",
        None,
        [
            (from_account_id, -amount),
            (to_account_id, amount),
        ],
    )