# 💰 Expense Manager

A terminal-based expense tracker backed by SQLite. Log expenses, tag them by category, set monthly budgets, and pull spending reports — all from the command line, with your data persisted locally in a real database (not a CSV you'll eventually corrupt).

## Why this exists

Most beginner expense trackers keep everything in a list in memory or a flat CSV with no validation. This one is built like a small real application:

- **Real persistence** — SQLite database with a proper schema, not a text file
- **Validated data** — amounts must be positive, categories are normalized (`food` and `Food` are the same category)
- **Budgets** — set a monthly limit per category and get an over/under-budget flag
- **Reports** — totals, per-category breakdowns, and monthly summaries
- **Exportable** — dump everything to CSV for Excel/Sheets
- **Tested** — full pytest suite covering the core business logic

## Features

| Feature | Description |
|---|---|
| Add / edit / delete expenses | Full CRUD from the CLI |
| Category normalization | `food`, `Food`, and `FOOD` are all treated as one category |
| Date filtering | List or summarize expenses between any two dates |
| Monthly summary | Total spent, count, and per-category breakdown for any month |
| Budgets | Set a monthly limit per category; see remaining balance and over-budget flags |
| CSV export | One command exports your full expense history |
| SQLite storage | Data lives in `~/.expense_manager/expenses.db` by default |

## Installation

```bash
git clone https://github.com/masoodhassan100/expense-manager.git
cd expense-manager
pip install -r requirements.txt
```

No third-party runtime dependencies are required — everything runs on Python's standard library (`sqlite3`, `csv`, `argparse`). `requirements.txt` only installs `pytest` for running tests.

## Usage

```bash
# Add an expense
python main.py add 25.50 Food --description "Lunch with team"

# Add an expense for a specific date
python main.py add 1200 Rent --date 2026-07-01

# List all expenses
python main.py list

# Filter by category or date range
python main.py list --category Food
python main.py list --start 2026-07-01 --end 2026-07-31

# Delete an expense by ID
python main.py delete 3

# Monthly summary (defaults to the current month if omitted)
python main.py summary 2026 7

# All-time total
python main.py total

# Set a monthly budget for a category
python main.py budget set Food 300

# Check current-month budget status
python main.py budget status

# Export everything to CSV
python main.py export expenses.csv
```

### Example output

```
$ python main.py summary 2026 7

Summary for 2026-07
Total spent: 845.50 across 12 expense(s)

Category    Amount
------------------
Rent        1200.00
Food        245.50
Transport   80.00

Budget status:
  Food: spent 245.50 / limit 300.00 (OK)
  Rent: spent 1200.00 / limit 1000.00 (OVER BUDGET)
```

### Install as a CLI command (optional)

```bash
pip install -e .
expense-manager add 25.50 Food
```

## Project structure

```
expense-manager/
├── expense_manager/
│   ├── __init__.py
│   ├── cli.py         # argument parsing and CLI entry point
│   ├── database.py    # SQLite connection + schema management
│   ├── manager.py      # core business logic (CRUD, reports, budgets)
│   └── models.py       # Expense / Budget data classes with validation
├── tests/
│   └── test_manager.py
├── main.py             # `python main.py <command>` entry point
├── requirements.txt
├── setup.py
└── LICENSE
```

## Data storage

By default, data is stored in `~/.expense_manager/expenses.db`. Pass a custom path when constructing `ExpenseManager(db_path=...)` if you want a project-local database instead (the test suite does exactly this, using a temporary file per test so tests never touch your real data).

## Running tests

```bash
pip install -r requirements.txt
pytest -v
```

## Roadmap / ideas for contributions

- [ ] Recurring expenses (rent, subscriptions) auto-logged each month
- [ ] Multi-currency support
- [ ] Simple charts (matplotlib) for spending trends
- [ ] Optional web dashboard (Flask) on top of the same `ExpenseManager` class

Pull requests are welcome — this is a good project to practice contributing to open source.

## License

MIT — see [LICENSE](LICENSE).
