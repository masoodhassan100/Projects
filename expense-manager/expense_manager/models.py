"""Plain data classes representing domain entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_cls


@dataclass
class Expense:
    """A single expense record."""

    amount: float
    category: str
    description: str = ""
    date: str = ""  # ISO format YYYY-MM-DD
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.date:
            self.date = date_cls.today().isoformat()
        if self.amount <= 0:
            raise ValueError("Expense amount must be greater than zero")
        if not self.category or not self.category.strip():
            raise ValueError("Expense category cannot be empty")
        self.category = self.category.strip().title()

    @classmethod
    def from_row(cls, row) -> "Expense":
        return cls(
            id=row["id"],
            amount=row["amount"],
            category=row["category"],
            description=row["description"],
            date=row["date"],
        )


@dataclass
class Budget:
    """A monthly spending limit for a category."""

    category: str
    monthly_limit: float

    def __post_init__(self) -> None:
        self.category = self.category.strip().title()
        if self.monthly_limit < 0:
            raise ValueError("Budget limit cannot be negative")
