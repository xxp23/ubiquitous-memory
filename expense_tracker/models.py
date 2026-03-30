"""Data models for the annual expense tracker."""

from dataclasses import dataclass
from typing import Optional


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_NAMES_CN = [
    "一月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "十一月", "十二月",
]

DEFAULT_CATEGORIES = [
    "住房",       # Housing
    "餐饮",       # Food & Dining
    "交通",       # Transportation
    "医疗健康",   # Healthcare
    "教育",       # Education
    "娱乐",       # Entertainment
    "服装",       # Clothing
    "日用品",     # Daily necessities
    "旅行",       # Travel
    "其他",       # Other
]


@dataclass
class BudgetItem:
    """A planned budget amount for a category in a given month."""

    year: int
    month: int        # 1-12
    category: str
    amount: float     # planned amount

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "category": self.category,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BudgetItem":
        return cls(
            year=int(data["year"]),
            month=int(data["month"]),
            category=data["category"],
            amount=float(data["amount"]),
        )


@dataclass
class ExpenseItem:
    """An actual expense record."""

    year: int
    month: int        # 1-12
    day: int          # 1-31
    category: str
    amount: float
    description: str = ""
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExpenseItem":
        return cls(
            year=int(data["year"]),
            month=int(data["month"]),
            day=int(data["day"]),
            category=data["category"],
            amount=float(data["amount"]),
            description=data.get("description", ""),
            id=int(data["id"]) if data.get("id") is not None else None,
        )
