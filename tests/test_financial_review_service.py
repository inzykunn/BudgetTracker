import unittest

from database.connection import get_connection
from services import account_service, category_service, finance_service
from services.financial_review_service import (
    compare_snapshots,
    generate_report,
    reconcile_account_balances,
    review_period,
)
from services.financial_snapshot_service import create_snapshot
from tests.base_test import BaseDatabaseTest


class FinancialReviewServiceTest(BaseDatabaseTest):
    def test_period_summary_excludes_transfers(self):
        account_id = account_service.create_account("Review Cash", "CASH")
        bank_id = account_service.create_account("Review Bank", "CASH")
        income_category = category_service.create_category("Review Salary", "INCOME")
        expense_category = category_service.create_category("Review Food", "EXPENSE")
        finance_service.record_income("2026-10-01", "Salary", account_id, 5000, income_category)
        finance_service.record_expense("2026-10-02", "Food", account_id, 1200, expense_category)
        finance_service.record_transfer("2026-10-03", "Transfer", account_id, bank_id, 1000)

        review = review_period("2026-10-01", "2026-10-31")

        self.assertEqual(5000, review["income"])
        self.assertEqual(1200, review["expenses"])
        self.assertEqual(3800, review["net_cash_flow"])
        self.assertEqual(3, len(review["transactions"]))
        self.assertIn("Transfers are excluded", generate_report("2026-10-01", "2026-10-31"))

    def test_reconciliation_reports_discrepancies_and_missing_values(self):
        account_id = account_service.create_account("Review Cash", "CASH")
        result = reconcile_account_balances({account_id: 100})
        self.assertEqual("DISCREPANCY", result["accounts"][0]["status"])
        self.assertEqual(100, result["accounts"][0]["discrepancy"])
        self.assertEqual("MISSING_ACTUAL_BALANCE", reconcile_account_balances({})["accounts"][0]["status"])

    def test_snapshot_comparison(self):
        account_id = account_service.create_account("Review Cash", "CASH")
        first_id = create_snapshot("First", "2026-10-01")
        connection = get_connection()
        try:
            transaction = connection.execute(
                "INSERT INTO transactions (date, description, type) VALUES (?, ?, ?)",
                ("2026-10-02", "Change", "OPENING_BALANCE"),
            )
            connection.execute(
                "INSERT INTO transaction_entries (transaction_id, account_id, amount) VALUES (?, ?, ?)",
                (transaction.lastrowid, account_id, 250),
            )
            connection.commit()
        finally:
            connection.close()
        second_id = create_snapshot("Second", "2026-10-02")
        comparison = compare_snapshots(first_id, second_id)
        self.assertEqual(250, comparison["account_balance_changes"][0]["change"])

    def test_invalid_period_is_rejected(self):
        with self.assertRaises(ValueError):
            review_period("2026-10-31", "2026-10-01")


if __name__ == "__main__":
    unittest.main()
