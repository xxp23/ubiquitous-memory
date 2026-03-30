"""Tests for the annual expense tracker."""

import os
import tempfile
import pytest

from expense_tracker.models import BudgetItem, ExpenseItem
from expense_tracker.tracker import ExpenseTracker


@pytest.fixture
def tracker(tmp_path):
    """Create a fresh tracker backed by a temporary directory."""
    return ExpenseTracker(data_dir=str(tmp_path))


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TestBudgetItem:
    def test_roundtrip(self):
        item = BudgetItem(year=2025, month=3, category="餐饮", amount=1500.0)
        assert BudgetItem.from_dict(item.to_dict()) == item

    def test_from_dict_coerces_types(self):
        item = BudgetItem.from_dict({"year": "2025", "month": "3", "category": "餐饮", "amount": "1500"})
        assert item.year == 2025
        assert item.month == 3
        assert item.amount == 1500.0


class TestExpenseItem:
    def test_roundtrip(self):
        item = ExpenseItem(year=2025, month=3, day=15, category="餐饮", amount=200.0, description="午餐", id=1)
        assert ExpenseItem.from_dict(item.to_dict()) == item

    def test_optional_description(self):
        item = ExpenseItem.from_dict({"year": 2025, "month": 3, "day": 15, "category": "餐饮", "amount": 200.0, "id": 1})
        assert item.description == ""


# ---------------------------------------------------------------------------
# Budget management
# ---------------------------------------------------------------------------

class TestBudget:
    def test_set_and_get_monthly_budget(self, tracker):
        tracker.set_budget(2025, 3, "餐饮", 1500.0)
        items = tracker.get_budget(2025, 3)
        assert len(items) == 1
        assert items[0].amount == 1500.0

    def test_update_existing_budget(self, tracker):
        tracker.set_budget(2025, 3, "餐饮", 1500.0)
        tracker.set_budget(2025, 3, "餐饮", 2000.0)
        items = tracker.get_budget(2025, 3)
        assert len(items) == 1
        assert items[0].amount == 2000.0

    def test_set_annual_budget_creates_12_months(self, tracker):
        tracker.set_annual_budget(2025, "住房", 3000.0)
        items = tracker.get_budget(2025)
        assert len(items) == 12
        for item in items:
            assert item.amount == 3000.0

    def test_negative_budget_raises(self, tracker):
        with pytest.raises(ValueError):
            tracker.set_budget(2025, 1, "餐饮", -100.0)

    def test_budget_filtered_by_year(self, tracker):
        tracker.set_budget(2025, 1, "餐饮", 1000.0)
        tracker.set_budget(2024, 1, "餐饮", 800.0)
        assert len(tracker.get_budget(2025)) == 1
        assert len(tracker.get_budget(2024)) == 1


# ---------------------------------------------------------------------------
# Expense management
# ---------------------------------------------------------------------------

class TestExpenses:
    def test_add_and_list(self, tracker):
        expense = tracker.add_expense(2025, 3, 15, "餐饮", 200.0, "午餐")
        assert expense.id == 1
        expenses = tracker.get_expenses(2025)
        assert len(expenses) == 1
        assert expenses[0].amount == 200.0

    def test_id_auto_increments(self, tracker):
        e1 = tracker.add_expense(2025, 1, 1, "餐饮", 100.0)
        e2 = tracker.add_expense(2025, 1, 2, "交通", 50.0)
        assert e2.id == e1.id + 1

    def test_delete_expense(self, tracker):
        expense = tracker.add_expense(2025, 3, 15, "餐饮", 200.0)
        result = tracker.delete_expense(expense.id)
        assert result is True
        assert tracker.get_expenses(2025) == []

    def test_delete_nonexistent_returns_false(self, tracker):
        assert tracker.delete_expense(999) is False

    def test_negative_expense_raises(self, tracker):
        with pytest.raises(ValueError):
            tracker.add_expense(2025, 1, 1, "餐饮", -50.0)

    def test_filter_by_month(self, tracker):
        tracker.add_expense(2025, 1, 5, "餐饮", 100.0)
        tracker.add_expense(2025, 2, 5, "餐饮", 200.0)
        assert len(tracker.get_expenses(2025, month=1)) == 1
        assert len(tracker.get_expenses(2025, month=2)) == 1

    def test_filter_by_category(self, tracker):
        tracker.add_expense(2025, 1, 5, "餐饮", 100.0)
        tracker.add_expense(2025, 1, 6, "交通", 50.0)
        assert len(tracker.get_expenses(2025, category="餐饮")) == 1
        assert len(tracker.get_expenses(2025, category="交通")) == 1


# ---------------------------------------------------------------------------
# Statistics / summaries
# ---------------------------------------------------------------------------

class TestSummaries:
    def test_monthly_summary_with_budget_and_actual(self, tracker):
        tracker.set_budget(2025, 1, "餐饮", 1000.0)
        tracker.add_expense(2025, 1, 10, "餐饮", 600.0)
        tracker.add_expense(2025, 1, 20, "餐饮", 200.0)
        summary = tracker.monthly_summary(2025, 1)
        assert "餐饮" in summary
        assert summary["餐饮"]["budget"] == 1000.0
        assert summary["餐饮"]["actual"] == 800.0
        assert summary["餐饮"]["difference"] == -200.0

    def test_monthly_summary_overspent(self, tracker):
        tracker.set_budget(2025, 1, "娱乐", 300.0)
        tracker.add_expense(2025, 1, 15, "娱乐", 500.0)
        summary = tracker.monthly_summary(2025, 1)
        assert summary["娱乐"]["difference"] == 200.0

    def test_annual_summary_aggregates_all_months(self, tracker):
        for month in range(1, 4):
            tracker.set_budget(2025, month, "餐饮", 1000.0)
            tracker.add_expense(2025, month, 10, "餐饮", 800.0)
        summary = tracker.annual_summary(2025)
        assert summary["餐饮"]["budget"] == 3000.0
        assert summary["餐饮"]["actual"] == 2400.0

    def test_monthly_totals_returns_12_months(self, tracker):
        totals = tracker.monthly_totals(2025)
        assert len(totals) == 12
        assert all(len(t) == 3 for t in totals)

    def test_monthly_totals_values(self, tracker):
        tracker.set_budget(2025, 6, "住房", 3000.0)
        tracker.add_expense(2025, 6, 1, "住房", 2800.0)
        totals = tracker.monthly_totals(2025)
        june = totals[5]  # index 5 = month 6
        assert june[0] == 6
        assert june[1] == 3000.0
        assert june[2] == 2800.0

    def test_category_without_budget_shows_in_summary(self, tracker):
        tracker.add_expense(2025, 1, 1, "旅行", 5000.0)
        summary = tracker.monthly_summary(2025, 1)
        assert "旅行" in summary
        assert summary["旅行"]["budget"] == 0.0
        assert summary["旅行"]["actual"] == 5000.0


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_budget_persists_across_tracker_instances(self, tmp_path):
        t1 = ExpenseTracker(data_dir=str(tmp_path))
        t1.set_budget(2025, 1, "餐饮", 1500.0)

        t2 = ExpenseTracker(data_dir=str(tmp_path))
        items = t2.get_budget(2025, 1)
        assert len(items) == 1
        assert items[0].amount == 1500.0

    def test_expenses_persist_across_tracker_instances(self, tmp_path):
        t1 = ExpenseTracker(data_dir=str(tmp_path))
        t1.add_expense(2025, 1, 5, "交通", 150.0, "地铁月票")

        t2 = ExpenseTracker(data_dir=str(tmp_path))
        expenses = t2.get_expenses(2025)
        assert len(expenses) == 1
        assert expenses[0].description == "地铁月票"

    def test_id_continues_after_reload(self, tmp_path):
        t1 = ExpenseTracker(data_dir=str(tmp_path))
        e1 = t1.add_expense(2025, 1, 1, "餐饮", 100.0)

        t2 = ExpenseTracker(data_dir=str(tmp_path))
        e2 = t2.add_expense(2025, 1, 2, "交通", 50.0)
        assert e2.id == e1.id + 1
