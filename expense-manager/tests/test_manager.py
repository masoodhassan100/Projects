"""Unit tests for the Expense Manager engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from expense_manager.manager import ExpenseManager


@pytest.fixture
def manager(tmp_path: Path) -> ExpenseManager:
    return ExpenseManager(db_path=tmp_path / "test_expenses.db")


def test_add_expense(manager: ExpenseManager):
    expense = manager.add_expense(25.5, "food", "Lunch")
    assert expense.id is not None
    assert expense.category == "Food"  # title-cased
    assert expense.amount == 25.5


def test_add_expense_rejects_non_positive_amount(manager: ExpenseManager):
    with pytest.raises(ValueError):
        manager.add_expense(0, "Food")
    with pytest.raises(ValueError):
        manager.add_expense(-5, "Food")


def test_add_expense_rejects_empty_category(manager: ExpenseManager):
    with pytest.raises(ValueError):
        manager.add_expense(10, "   ")


def test_list_expenses_filters_by_category(manager: ExpenseManager):
    manager.add_expense(10, "Food")
    manager.add_expense(20, "Transport")
    manager.add_expense(15, "food")  # should merge with "Food" after title-casing

    food_expenses = manager.list_expenses(category="Food")
    assert len(food_expenses) == 2
    assert all(e.category == "Food" for e in food_expenses)


def test_list_expenses_filters_by_date_range(manager: ExpenseManager):
    manager.add_expense(10, "Food", date="2026-01-01")
    manager.add_expense(20, "Food", date="2026-02-15")
    manager.add_expense(30, "Food", date="2026-03-01")

    results = manager.list_expenses(start_date="2026-02-01", end_date="2026-02-28")
    assert len(results) == 1
    assert results[0].amount == 20


def test_delete_expense(manager: ExpenseManager):
    expense = manager.add_expense(10, "Food")
    assert manager.delete_expense(expense.id) is True
    assert manager.list_expenses() == []
    assert manager.delete_expense(9999) is False


def test_update_expense(manager: ExpenseManager):
    expense = manager.add_expense(10, "Food")
    updated = manager.update_expense(expense.id, amount=99.0, description="Updated")
    assert updated is True

    refreshed = manager.list_expenses()[0]
    assert refreshed.amount == 99.0
    assert refreshed.description == "Updated"


def test_total_spent(manager: ExpenseManager):
    manager.add_expense(10, "Food")
    manager.add_expense(20, "Transport")
    assert manager.total_spent() == 30.0


def test_spending_by_category(manager: ExpenseManager):
    manager.add_expense(10, "Food")
    manager.add_expense(5, "Food")
    manager.add_expense(20, "Transport")

    totals = manager.spending_by_category()
    assert totals["Food"] == 15.0
    assert totals["Transport"] == 20.0


def test_monthly_summary(manager: ExpenseManager):
    manager.add_expense(10, "Food", date="2026-07-01")
    manager.add_expense(20, "Food", date="2026-07-15")
    manager.add_expense(5, "Transport", date="2026-06-30")  # different month

    summary = manager.monthly_summary(2026, 7)
    assert summary["total"] == 30.0
    assert summary["count"] == 2
    assert summary["by_category"]["Food"] == 30.0


def test_budget_set_and_status(manager: ExpenseManager):
    manager.set_budget("Food", 100)
    manager.add_expense(30, "Food")

    status = manager.check_budgets()
    assert status["Food"]["spent"] == 30
    assert status["Food"]["limit"] == 100
    assert status["Food"]["remaining"] == 70
    assert status["Food"]["over_budget"] is False


def test_budget_over_limit_flagged(manager: ExpenseManager):
    manager.set_budget("Food", 20)
    manager.add_expense(30, "Food")

    status = manager.check_budgets()
    assert status["Food"]["over_budget"] is True


def test_export_csv(manager: ExpenseManager, tmp_path: Path):
    manager.add_expense(10, "Food", "Lunch")
    manager.add_expense(20, "Transport", "Bus")

    output = manager.export_csv(tmp_path / "out.csv")
    content = output.read_text()

    assert "Food" in content
    assert "Transport" in content
    assert "id,date,category,amount,description" in content
