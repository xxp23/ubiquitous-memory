"""Business logic: budget management and expense tracking."""

from typing import Dict, List, Optional, Tuple

from .models import BudgetItem, DEFAULT_CATEGORIES, ExpenseItem
from . import storage


class ExpenseTracker:
    """Central service for planning and tracking annual expenses."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._budget: List[BudgetItem] = storage.load_budget(data_dir)
        self._expenses: List[ExpenseItem] = storage.load_expenses(data_dir)
        self._next_id: int = self._compute_next_id()

    # ------------------------------------------------------------------
    # Budget (planned expenses)
    # ------------------------------------------------------------------

    def set_budget(self, year: int, month: int, category: str, amount: float) -> None:
        """Set (or update) the planned budget for a category in a month."""
        if amount < 0:
            raise ValueError("预算金额不能为负数")
        for item in self._budget:
            if item.year == year and item.month == month and item.category == category:
                item.amount = amount
                storage.save_budget(self.data_dir, self._budget)
                return
        self._budget.append(BudgetItem(year=year, month=month, category=category, amount=amount))
        storage.save_budget(self.data_dir, self._budget)

    def get_budget(self, year: int, month: Optional[int] = None) -> List[BudgetItem]:
        """Return budget items, optionally filtered to a specific month."""
        return [
            b for b in self._budget
            if b.year == year and (month is None or b.month == month)
        ]

    def set_annual_budget(self, year: int, category: str, amount_per_month: float) -> None:
        """Set the same monthly budget for all 12 months of a year."""
        for month in range(1, 13):
            self.set_budget(year, month, category, amount_per_month)

    # ------------------------------------------------------------------
    # Actual expenses
    # ------------------------------------------------------------------

    def add_expense(
        self,
        year: int,
        month: int,
        day: int,
        category: str,
        amount: float,
        description: str = "",
    ) -> ExpenseItem:
        """Record an actual expense and return it."""
        if amount < 0:
            raise ValueError("消费金额不能为负数")
        expense = ExpenseItem(
            year=year,
            month=month,
            day=day,
            category=category,
            amount=amount,
            description=description,
            id=self._next_id,
        )
        self._next_id += 1
        self._expenses.append(expense)
        storage.save_expenses(self.data_dir, self._expenses)
        return expense

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense record by ID. Returns True if found and removed."""
        before = len(self._expenses)
        self._expenses = [e for e in self._expenses if e.id != expense_id]
        if len(self._expenses) < before:
            storage.save_expenses(self.data_dir, self._expenses)
            return True
        return False

    def get_expenses(
        self,
        year: int,
        month: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[ExpenseItem]:
        """Return expense records, optionally filtered by month and category."""
        return [
            e for e in self._expenses
            if e.year == year
            and (month is None or e.month == month)
            and (category is None or e.category == category)
        ]

    # ------------------------------------------------------------------
    # Statistics / comparison
    # ------------------------------------------------------------------

    def monthly_summary(self, year: int, month: int) -> Dict[str, Dict[str, float]]:
        """
        Return a summary dict keyed by category with keys 'budget' and 'actual'.
        Categories without a budget or actual value are still included with 0.
        """
        budget_items = self.get_budget(year, month)
        expense_items = self.get_expenses(year, month)

        categories: set = {b.category for b in budget_items} | {e.category for e in expense_items}

        budget_map = {b.category: b.amount for b in budget_items}
        actual_map: Dict[str, float] = {}
        for e in expense_items:
            actual_map[e.category] = actual_map.get(e.category, 0.0) + e.amount

        summary: Dict[str, Dict[str, float]] = {}
        for cat in sorted(categories):
            budget_val = budget_map.get(cat, 0.0)
            actual_val = actual_map.get(cat, 0.0)
            summary[cat] = {
                "budget": budget_val,
                "actual": actual_val,
                "difference": actual_val - budget_val,
            }
        return summary

    def annual_summary(self, year: int) -> Dict[str, Dict[str, float]]:
        """
        Return a yearly summary dict keyed by category with keys
        'budget', 'actual', and 'difference'.
        """
        budget_items = self.get_budget(year)
        expense_items = self.get_expenses(year)

        categories: set = {b.category for b in budget_items} | {e.category for e in expense_items}

        budget_map: Dict[str, float] = {}
        for b in budget_items:
            budget_map[b.category] = budget_map.get(b.category, 0.0) + b.amount

        actual_map: Dict[str, float] = {}
        for e in expense_items:
            actual_map[e.category] = actual_map.get(e.category, 0.0) + e.amount

        summary: Dict[str, Dict[str, float]] = {}
        for cat in sorted(categories):
            budget_val = budget_map.get(cat, 0.0)
            actual_val = actual_map.get(cat, 0.0)
            summary[cat] = {
                "budget": budget_val,
                "actual": actual_val,
                "difference": actual_val - budget_val,
            }
        return summary

    def monthly_totals(self, year: int) -> List[Tuple[int, float, float]]:
        """
        Return list of (month, total_budget, total_actual) tuples for all 12 months.
        """
        result = []
        for month in range(1, 13):
            budget_total = sum(b.amount for b in self.get_budget(year, month))
            actual_total = sum(e.amount for e in self.get_expenses(year, month))
            result.append((month, budget_total, actual_total))
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def categories(self) -> List[str]:
        """Return the list of default spending categories."""
        return list(DEFAULT_CATEGORIES)

    def _compute_next_id(self) -> int:
        valid_ids = [e.id for e in self._expenses if e.id is not None]
        return max(valid_ids) + 1 if valid_ids else 1
