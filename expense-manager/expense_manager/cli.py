"""
Command-line interface for Expense Manager.

Examples
--------
    python main.py add 25.50 Food --description "Lunch with team"
    python main.py list --category Food
    python main.py summary 2026 7
    python main.py budget set Food 300
    python main.py budget status
    python main.py export expenses.csv
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from expense_manager.manager import ExpenseManager

__version__ = "1.0.0"


def _print_table(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        print("No records found.")
        return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense-manager",
        description="Track expenses, set category budgets, and view spending reports from the terminal.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a new expense")
    p_add.add_argument("amount", type=float, help="Amount spent")
    p_add.add_argument("category", help="Expense category, e.g. Food, Rent, Transport")
    p_add.add_argument("--description", default="", help="Optional note about the expense")
    p_add.add_argument("--date", default=None, help="Date in YYYY-MM-DD format (default: today)")

    # list
    p_list = subparsers.add_parser("list", help="List expenses")
    p_list.add_argument("--category", default=None)
    p_list.add_argument("--start", dest="start_date", default=None, help="YYYY-MM-DD")
    p_list.add_argument("--end", dest="end_date", default=None, help="YYYY-MM-DD")
    p_list.add_argument("--limit", type=int, default=None)

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete an expense by ID")
    p_delete.add_argument("expense_id", type=int)

    # summary
    p_summary = subparsers.add_parser("summary", help="Monthly spending summary")
    p_summary.add_argument("year", type=int, nargs="?", default=datetime.today().year)
    p_summary.add_argument("month", type=int, nargs="?", default=datetime.today().month)

    # total
    subparsers.add_parser("total", help="Show total spent across all recorded expenses")

    # budget
    p_budget = subparsers.add_parser("budget", help="Manage category budgets")
    budget_sub = p_budget.add_subparsers(dest="budget_command", required=True)
    p_budget_set = budget_sub.add_parser("set", help="Set a monthly budget for a category")
    p_budget_set.add_argument("category")
    p_budget_set.add_argument("monthly_limit", type=float)
    budget_sub.add_parser("status", help="Show budget vs. actual spending for the current month")

    # export
    p_export = subparsers.add_parser("export", help="Export all expenses to a CSV file")
    p_export.add_argument("output_path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = ExpenseManager()

    try:
        if args.command == "add":
            expense = manager.add_expense(args.amount, args.category, args.description, args.date)
            print(f"Added expense #{expense.id}: {expense.amount:.2f} in {expense.category} on {expense.date}")

        elif args.command == "list":
            expenses = manager.list_expenses(args.category, args.start_date, args.end_date, args.limit)
            rows = [
                {"ID": e.id, "Date": e.date, "Category": e.category, "Amount": f"{e.amount:.2f}", "Description": e.description}
                for e in expenses
            ]
            _print_table(rows, ["ID", "Date", "Category", "Amount", "Description"])

        elif args.command == "delete":
            deleted = manager.delete_expense(args.expense_id)
            print(f"Deleted expense #{args.expense_id}" if deleted else f"No expense found with ID {args.expense_id}")

        elif args.command == "summary":
            summary = manager.monthly_summary(args.year, args.month)
            print(f"\nSummary for {args.year}-{args.month:02d}")
            print(f"Total spent: {summary['total']:.2f} across {summary['count']} expense(s)\n")
            rows = [{"Category": c, "Amount": f"{amt:.2f}"} for c, amt in summary["by_category"].items()]
            _print_table(rows, ["Category", "Amount"])
            if summary["budget_status"]:
                print("\nBudget status:")
                for cat, status in summary["budget_status"].items():
                    flag = "OVER BUDGET" if status["over_budget"] else "OK"
                    print(f"  {cat}: spent {status['spent']:.2f} / limit {status['limit']:.2f} ({flag})")

        elif args.command == "total":
            print(f"Total spent (all time): {manager.total_spent():.2f}")

        elif args.command == "budget":
            if args.budget_command == "set":
                budget = manager.set_budget(args.category, args.monthly_limit)
                print(f"Budget set: {budget.category} -> {budget.monthly_limit:.2f} / month")
            elif args.budget_command == "status":
                status = manager.check_budgets()
                if not status:
                    print("No budgets configured yet. Use 'budget set <category> <limit>' first.")
                for cat, s in status.items():
                    flag = "OVER BUDGET" if s["over_budget"] else "OK"
                    print(f"{cat}: spent {s['spent']:.2f} / limit {s['limit']:.2f} | remaining {s['remaining']:.2f} ({flag})")

        elif args.command == "export":
            path = manager.export_csv(args.output_path)
            print(f"Exported expenses to {path}")

    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
