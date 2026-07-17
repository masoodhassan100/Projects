"""
Business logic for adding, querying, and analyzing expenses.

This module is UI-agnostic — the CLI (cli.py) is a thin layer on
top of ExpenseManager, so the same logic could back a web app or
GUI without changes.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from expense_manager.database import Database, DEFAULT_DB_PATH
from expense_manager.models import Budget, Expense


class ExpenseManager:
    """Handles all expense and budget operations."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db = Database(db_path)

    # ------------------------------------------------------------------ #
    # Expenses
    # ------------------------------------------------------------------ #
    def add_expense(self, amount: float, category: str, description: str = "", date: str | None = None) -> Expense:
        expense = Expense(amount=amount, category=category, description=description, date=date or "")
        with self.db.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                (expense.amount, expense.category, expense.description, expense.date),
            )
            expense.id = cursor.lastrowid
        return expense

    def delete_expense(self, expense_id: int) -> bool:
        with self.db.connect() as conn:
            cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            return cursor.rowcount > 0

    def update_expense(self, expense_id: int, **fields) -> bool:
        if not fields:
            return False
        allowed = {"amount", "category", "description", "date"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        with self.db.connect() as conn:
            cursor = conn.execute(
                f"UPDATE expenses SET {set_clause} WHERE id = ?",
                (*updates.values(), expense_id),
            )
            return cursor.rowcount > 0

    def list_expenses(
        self,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> list[Expense]:
        query = "SELECT * FROM expenses WHERE 1=1"
        params: list = []

        if category:
            query += " AND category = ?"
            params.append(category.strip().title())
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self.db.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [Expense.from_row(row) for row in rows]

    # ------------------------------------------------------------------ #
    # Reporting
    # ------------------------------------------------------------------ #
    def total_spent(self, start_date: str | None = None, end_date: str | None = None) -> float:
        expenses = self.list_expenses(start_date=start_date, end_date=end_date)
        return round(sum(e.amount for e in expenses), 2)

    def spending_by_category(self, start_date: str | None = None, end_date: str | None = None) -> dict[str, float]:
        expenses = self.list_expenses(start_date=start_date, end_date=end_date)
        totals: dict[str, float] = defaultdict(float)
        for e in expenses:
            totals[e.category] += e.amount
        return {k: round(v, 2) for k, v in sorted(totals.items(), key=lambda kv: -kv[1])}

    def monthly_summary(self, year: int, month: int) -> dict:
        start = f"{year:04d}-{month:02d}-01"
        end_day = 31
        end = f"{year:04d}-{month:02d}-{end_day:02d}"
        expenses = self.list_expenses(start_date=start, end_date=end)
        by_category = self.spending_by_category(start_date=start, end_date=end)

        return {
            "year": year,
            "month": month,
            "total": round(sum(e.amount for e in expenses), 2),
            "count": len(expenses),
            "by_category": by_category,
            "budget_status": self.check_budgets(by_category),
        }

    # ------------------------------------------------------------------ #
    # Budgets
    # ------------------------------------------------------------------ #
    def set_budget(self, category: str, monthly_limit: float) -> Budget:
        budget = Budget(category=category, monthly_limit=monthly_limit)
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO budgets (category, monthly_limit) VALUES (?, ?) "
                "ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit",
                (budget.category, budget.monthly_limit),
            )
        return budget

    def get_budgets(self) -> dict[str, float]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM budgets").fetchall()
        return {row["category"]: row["monthly_limit"] for row in rows}

    def check_budgets(self, spending_by_category: dict[str, float] | None = None) -> dict[str, dict]:
        """Compare current-month spending against configured budgets."""
        if spending_by_category is None:
            today = datetime.today()
            spending_by_category = self.spending_by_category(
                start_date=f"{today.year:04d}-{today.month:02d}-01"
            )

        budgets = self.get_budgets()
        status = {}
        for category, limit in budgets.items():
            spent = spending_by_category.get(category, 0.0)
            status[category] = {
                "spent": round(spent, 2),
                "limit": limit,
                "remaining": round(limit - spent, 2),
                "over_budget": spent > limit,
            }
        return status

    def export_csv(self, output_path: str | Path) -> Path:
        import csv

        output_path = Path(output_path)
        expenses = self.list_expenses()
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "category", "amount", "description"])
            for e in expenses:
                writer.writerow([e.id, e.date, e.category, e.amount, e.description])
        return output_path
