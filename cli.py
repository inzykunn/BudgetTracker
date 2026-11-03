from datetime import date

from database.connection import initialize_database
from services import account_service, category_service, finance_service
from services import financial_review_service, financial_snapshot_service, transaction_service


def _read_int(prompt, minimum=None):
    value = int(input(prompt).strip())
    if minimum is not None and value < minimum:
        raise ValueError(f"Enter a number greater than or equal to {minimum}.")
    return value


def _read_date(prompt, default_today=False):
    value = input(prompt).strip()
    if not value and default_today:
        return date.today().isoformat()
    date.fromisoformat(value)
    return value


def _show_accounts():
    accounts = account_service.get_accounts()
    if not accounts:
        print("No accounts yet.")
        return
    print("\nACCOUNTS")
    for account in accounts:
        balance = transaction_service.get_account_balance(account[0])
        status = "Active" if account[3] else "Inactive"
        print(f"{account[0]}. {account[1]} | {account[2]} | Balance: {balance} | {status}")


def _show_categories():
    categories = category_service.get_categories()
    if not categories:
        print("No categories yet.")
        return
    print("\nCATEGORIES")
    for category in categories:
        print(f"{category[0]}. {category[1]} | {category[2]}")


def _create_account():
    name = input("Account name: ").strip()
    account_type = input("Account type (CASH/BANK/OTHER): ").strip().upper()
    opening_balance = _read_int("Opening balance (whole number, 0 if none): ", 0)
    opening_date = None
    if opening_balance:
        opening_date = _read_date("Opening date YYYY-MM-DD [today]: ", True)
    account_id = account_service.create_account(name, account_type, opening_balance, opening_date)
    print(f"Account saved. ID: {account_id}")


def _create_category():
    name = input("Category name: ").strip()
    category_type = input("Type (INCOME/EXPENSE): ").strip().upper()
    if category_type not in {"INCOME", "EXPENSE"}:
        raise ValueError("Category type must be INCOME or EXPENSE.")
    category_id = category_service.create_category(name, category_type)
    print(f"Category saved. ID: {category_id}")


def _record_income_or_expense(kind):
    _show_accounts()
    account_id = _read_int("Account ID: ", 1)
    description = input("Description: ").strip()
    amount = _read_int("Amount (whole number): ", 1)
    transaction_date = _read_date("Date YYYY-MM-DD [today]: ", True)
    _show_categories()
    category_input = input(f"{kind.title()} category ID (blank for none): ").strip()
    category_id = int(category_input) if category_input else None
    if category_id is not None:
        category = category_service.get_category_by_id(category_id)
        if not category or category[2] != kind.upper():
            raise ValueError(f"Choose an existing {kind.lower()} category.")
    if kind == "income":
        transaction_id = finance_service.record_income(transaction_date, description, account_id, amount, category_id)
    else:
        transaction_id = finance_service.record_expense(transaction_date, description, account_id, amount, category_id)
    print(f"Transaction saved. ID: {transaction_id}")


def _record_transfer():
    _show_accounts()
    from_id = _read_int("From account ID: ", 1)
    to_id = _read_int("To account ID: ", 1)
    amount = _read_int("Amount (whole number): ", 1)
    description = input("Description: ").strip() or "Account transfer"
    transaction_date = _read_date("Date YYYY-MM-DD [today]: ", True)
    transaction_id = finance_service.record_transfer(transaction_date, description, from_id, to_id, amount)
    print(f"Transfer saved. ID: {transaction_id}")


def _review_period():
    start_date = _read_date("Start date YYYY-MM-DD: ")
    end_date = _read_date("End date YYYY-MM-DD: ")
    print("\n" + financial_review_service.generate_report(start_date, end_date))
    review = financial_review_service.review_period(start_date, end_date)
    print("\nBY ACCOUNT")
    for row in review["transactions_by_account"]:
        print(f"{row['account_name']}: {row['net_change']}")
    print("\nBY CATEGORY")
    for row in review["transactions_by_category"]:
        print(f"{row['type']} | {row['category']}: {row['amount']}")


def _create_snapshot():
    name = input("Snapshot name: ").strip()
    snapshot_date = _read_date("Snapshot date YYYY-MM-DD [today]: ", True)
    notes = input("Notes (optional): ").strip() or None
    snapshot_id = financial_snapshot_service.create_snapshot(name, snapshot_date, notes)
    print(f"Snapshot saved. ID: {snapshot_id}")


def _list_snapshots():
    snapshots = financial_snapshot_service.list_snapshots()
    if not snapshots:
        print("No snapshots yet.")
        return
    print("\nSNAPSHOTS")
    for snapshot in snapshots:
        status = "Finalized" if snapshot["finalized"] else "Draft"
        print(f"{snapshot['id']}. {snapshot['name']} | {snapshot['snapshot_date']} | {status}")


def _compare_snapshots():
    _list_snapshots()
    first_id = _read_int("First snapshot ID: ", 1)
    second_id = _read_int("Second snapshot ID: ", 1)
    result = financial_review_service.compare_snapshots(first_id, second_id)
    print(f"\n{result['first_snapshot']['name']} -> {result['second_snapshot']['name']}")
    for row in result["account_balance_changes"]:
        print(f"{row['account_name']}: {row['before']} -> {row['after']} (change {row['change']})")
    for table, changes in result["record_changes"].items():
        print(f"{table}: {len(changes['added'])} added, {len(changes['removed'])} removed, {len(changes['changed'])} changed")


def _reconcile():
    _show_accounts()
    print("Enter actual balances for accounts you want to compare. Leave an ID blank to finish.")
    actual_balances = {}
    while True:
        account_input = input("Account ID (blank to finish): ").strip()
        if not account_input:
            break
        account_id = int(account_input)
        actual_balances[account_id] = _read_int("Actual balance (whole number): ")
    result = financial_review_service.reconcile_account_balances(actual_balances)
    print("\nRECONCILIATION")
    for row in result["accounts"]:
        actual = "Not entered" if row["actual_balance"] is None else str(row["actual_balance"])
        discrepancy = "N/A" if row["discrepancy"] is None else str(row["discrepancy"])
        print(f"{row['id']}. {row['name']} | Recorded: {row['recorded_balance']} | Actual: {actual} | Difference: {discrepancy} | {row['status']}")
    if result["unknown_account_ids"]:
        print(f"Unknown account IDs: {result['unknown_account_ids']}")


def run():
    initialize_database()
    actions = {
        "1": ("List accounts and balances", _show_accounts),
        "2": ("Create account", _create_account),
        "3": ("List categories", _show_categories),
        "4": ("Create category", _create_category),
        "5": ("Record income", lambda: _record_income_or_expense("income")),
        "6": ("Record expense", lambda: _record_income_or_expense("expense")),
        "7": ("Transfer between accounts", _record_transfer),
        "8": ("Financial review", _review_period),
        "9": ("Create snapshot", _create_snapshot),
        "10": ("List snapshots", _list_snapshots),
        "11": ("Compare snapshots", _compare_snapshots),
        "12": ("Reconcile account balances", _reconcile),
    }
    while True:
        print("\nBUDGET TRACKER")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        action = actions.get(choice)
        if action is None:
            print("Choose a listed option.")
            continue
        try:
            action[1]()
        except (ValueError, TypeError) as exc:
            print(f"Could not complete action: {exc}")
        except Exception as exc:
            print(f"Operation failed: {exc}")


if __name__ == "__main__":
    run()
