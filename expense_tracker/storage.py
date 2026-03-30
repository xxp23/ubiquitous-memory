"""Storage layer: reads and writes budget/expense data as JSON files."""

import json
import os
from typing import List

from .models import BudgetItem, ExpenseItem

_BUDGET_FILE = "budget.json"
_EXPENSES_FILE = "expenses.json"


def _data_path(data_dir: str, filename: str) -> str:
    return os.path.join(data_dir, filename)


def load_budget(data_dir: str) -> List[BudgetItem]:
    """Load all budget items from disk."""
    path = _data_path(data_dir, _BUDGET_FILE)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [BudgetItem.from_dict(item) for item in raw]


def save_budget(data_dir: str, items: List[BudgetItem]) -> None:
    """Persist budget items to disk."""
    os.makedirs(data_dir, exist_ok=True)
    path = _data_path(data_dir, _BUDGET_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)


def load_expenses(data_dir: str) -> List[ExpenseItem]:
    """Load all expense records from disk."""
    path = _data_path(data_dir, _EXPENSES_FILE)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [ExpenseItem.from_dict(item) for item in raw]


def save_expenses(data_dir: str, items: List[ExpenseItem]) -> None:
    """Persist expense records to disk."""
    os.makedirs(data_dir, exist_ok=True)
    path = _data_path(data_dir, _EXPENSES_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)
