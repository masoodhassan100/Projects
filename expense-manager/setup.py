from setuptools import setup, find_packages

setup(
    name="expense-manager",
    version="1.0.0",
    description="A CLI tool for tracking expenses, budgets, and monthly spending reports (SQLite-backed).",
    author="HASSAN MASOOD",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "expense-manager=expense_manager.cli:main",
        ],
    },
)
