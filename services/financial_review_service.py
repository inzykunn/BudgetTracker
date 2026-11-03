import json
import sqlite3
from datetime import date

from database.connection import get_connection


def _validate_period(start_date, end_date):
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("Dates must use YYYY-MM-DD format") from exc
    if start.isoformat() != start_date or end.isoformat() != end_date or start > end:
        raise ValueError("Invalid review period")
    return start_date, end_date


def _rows(connection, query, params=()):
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def review_period(start_date, end_date):
    start_date, end_date = _validate_period(start_date, end_date)
    connection = get_connection()
    try:
        totals = connection.execute(
            """SELECT
                COALESCE(SUM(CASE WHEN type = 'INCOME' THEN
                    (SELECT COALESCE(SUM(amount), 0) FROM transaction_entries e WHERE e.transaction_id = t.id AND e.amount > 0)
                    ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN
                    -(SELECT COALESCE(SUM(amount), 0) FROM transaction_entries e WHERE e.transaction_id = t.id AND e.amount < 0)
                    ELSE 0 END), 0)
               FROM transactions t WHERE date BETWEEN ? AND ?""",
            (start_date, end_date),
        ).fetchone()
        income, expenses = totals
        by_account = _rows(connection, """
            SELECT a.id account_id, a.name account_name, COALESCE(SUM(e.amount), 0) net_change
            FROM transaction_entries e JOIN transactions t ON t.id=e.transaction_id
            JOIN accounts a ON a.id=e.account_id
            WHERE t.date BETWEEN ? AND ?
            GROUP BY a.id, a.name ORDER BY a.name
        """, (start_date, end_date))
        by_category = _rows(connection, """
            SELECT c.id category_id, COALESCE(c.name, 'Uncategorized') category,
                t.type, COUNT(DISTINCT t.id) transaction_count,
                CASE WHEN t.type='EXPENSE' THEN -SUM(e.amount)
                     WHEN t.type='INCOME' THEN SUM(e.amount) ELSE 0 END amount
            FROM transactions t
            LEFT JOIN categories c ON c.id=t.category_id
            LEFT JOIN transaction_entries e ON e.transaction_id=t.id
            WHERE t.date BETWEEN ? AND ? AND t.type IN ('INCOME','EXPENSE')
            GROUP BY c.id, c.name, t.type ORDER BY t.type, category
        """, (start_date, end_date))
        transactions = _rows(connection, """
            SELECT t.id, t.date, t.description, t.type, t.category_id,
                COALESCE(SUM(e.amount),0) net_amount
            FROM transactions t LEFT JOIN transaction_entries e ON e.transaction_id=t.id
            WHERE t.date BETWEEN ? AND ? GROUP BY t.id ORDER BY t.date, t.id
        """, (start_date, end_date))
        asset_activity = _rows(connection, """
            SELECT id, name, category, purchase_cost, current_value, acquired_date, status
            FROM assets WHERE acquired_date BETWEEN ? AND ? OR status IN ('SOLD','DISPOSED')
            ORDER BY acquired_date, id
        """, (start_date, end_date))
        asset_valuations = _rows(connection, """
            SELECT v.asset_id, a.name, v.valuation_date, v.value
            FROM asset_valuations v JOIN assets a ON a.id=v.asset_id
            WHERE v.valuation_date BETWEEN ? AND ? ORDER BY v.valuation_date, v.id
        """, (start_date, end_date))
        inventory = _rows(connection, """
            SELECT id, name, purchase_cost, sale_price, acquired_date, sold_date, status,
                CASE WHEN status='SOLD' AND sale_price IS NOT NULL THEN sale_price-purchase_cost ELSE NULL END profit_loss
            FROM inventory_items
            WHERE acquired_date BETWEEN ? AND ? OR sold_date BETWEEN ? AND ?
            ORDER BY acquired_date, id
        """, (start_date, end_date, start_date, end_date))
        receivables = connection.execute("""
            SELECT COALESCE(SUM(CASE WHEN status!='PAID' THEN
                COALESCE((SELECT h.outstanding_amount FROM receivable_balance_history h
                WHERE h.receivable_id=r.id AND h.effective_date<=? ORDER BY h.effective_date DESC,h.id DESC LIMIT 1), r.original_amount)
                ELSE 0 END),0) FROM receivables r WHERE date_created<=?
        """, (end_date, end_date)).fetchone()[0]
        liabilities = connection.execute("""
            SELECT COALESCE(SUM(CASE WHEN status!='PAID' THEN
                COALESCE((SELECT h.outstanding_amount FROM liability_balance_history h
                WHERE h.liability_id=l.id AND h.effective_date<=? ORDER BY h.effective_date DESC,h.id DESC LIMIT 1), l.original_amount)
                ELSE 0 END),0) FROM liabilities l WHERE date_created<=?
        """, (end_date, end_date)).fetchone()[0]
        asset_value = connection.execute("SELECT COALESCE(SUM(current_value),0) FROM assets WHERE status='ACTIVE'").fetchone()[0]
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "income": income,
            "expenses": expenses,
            "net_cash_flow": income - expenses,
            "transactions_by_account": by_account,
            "transactions_by_category": by_category,
            "transactions": transactions,
            "asset_activity": asset_activity,
            "asset_valuations": asset_valuations,
            "inventory_sales": inventory,
            "inventory_profit_loss": sum(item["profit_loss"] or 0 for item in inventory),
            "outstanding_receivables": receivables,
            "outstanding_liabilities": liabilities,
            "estimated_net_worth": asset_value + receivables - liabilities,
            "estimated_values": ["Asset values use current recorded valuations; they are not reconstructed as of the review date."],
            "missing_information": []
        }
    finally:
        connection.close()


def compare_snapshots(first_snapshot_id, second_snapshot_id):
    from services.financial_snapshot_service import get_snapshot
    first = get_snapshot(first_snapshot_id)
    second = get_snapshot(second_snapshot_id)
    first_data = first["data"]
    second_data = second["data"]
    first_accounts = {row["id"]: row for row in first_data.get("account_balances", [])}
    second_accounts = {row["id"]: row for row in second_data.get("account_balances", [])}
    account_changes = []
    for account_id in sorted(set(first_accounts) | set(second_accounts)):
        old = first_accounts.get(account_id)
        new = second_accounts.get(account_id)
        account_changes.append({
            "account_id": account_id,
            "account_name": (new or old)["name"],
            "before": old["balance"] if old else 0,
            "after": new["balance"] if new else 0,
            "change": (new["balance"] if new else 0) - (old["balance"] if old else 0)
        })
    changes = {}
    for table in ("assets", "inventory_items", "receivables", "liabilities"):
        old_rows = {row["id"]: row for row in first_data.get(table, [])}
        new_rows = {row["id"]: row for row in second_data.get(table, [])}
        changes[table] = {
            "added": [new_rows[key] for key in sorted(set(new_rows)-set(old_rows))],
            "removed": [old_rows[key] for key in sorted(set(old_rows)-set(new_rows))],
            "changed": [{"before": old_rows[key], "after": new_rows[key]} for key in sorted(set(old_rows)&set(new_rows)) if old_rows[key] != new_rows[key]]
        }
    return {
        "first_snapshot": {"id": first["id"], "name": first["name"], "date": first["snapshot_date"]},
        "second_snapshot": {"id": second["id"], "name": second["name"], "date": second["snapshot_date"]},
        "account_balance_changes": account_changes,
        "record_changes": changes
    }


def reconcile_account_balances(actual_balances):
    if not isinstance(actual_balances, dict):
        raise ValueError("Actual balances must be a dictionary of account IDs to balances")
    connection = get_connection()
    try:
        rows = _rows(connection, """
            SELECT a.id, a.name, a.type, a.is_active, COALESCE(SUM(e.amount),0) recorded_balance
            FROM accounts a LEFT JOIN transaction_entries e ON e.account_id=a.id
            GROUP BY a.id, a.name, a.type, a.is_active ORDER BY a.id
        """)
        result = []
        known = {row["id"] for row in rows}
        for row in rows:
            actual = actual_balances.get(row["id"], actual_balances.get(str(row["id"])))
            result.append({
                **row,
                "actual_balance": actual,
                "discrepancy": None if actual is None else actual - row["recorded_balance"],
                "status": "MISSING_ACTUAL_BALANCE" if actual is None else ("MATCH" if actual == row["recorded_balance"] else "DISCREPANCY")
            })
        unknown = [key for key in actual_balances if str(key).isdigit() and int(key) not in known]
        return {"accounts": result, "unknown_account_ids": unknown}
    finally:
        connection.close()


def generate_report(start_date, end_date):
    review = review_period(start_date, end_date)
    lines = [
        "FINANCIAL REVIEW",
        f"Period: {start_date} to {end_date}",
        f"Income: {review['income']}",
        f"Expenses: {review['expenses']}",
        f"Net cash flow: {review['net_cash_flow']}",
        f"Inventory profit/loss: {review['inventory_profit_loss']}",
        f"Outstanding receivables: {review['outstanding_receivables']}",
        f"Outstanding liabilities: {review['outstanding_liabilities']}",
        f"Estimated net worth: {review['estimated_net_worth']}",
        "Transfers are excluded from income and expense totals.",
        *review["estimated_values"]
    ]
    return "\n".join(lines)
