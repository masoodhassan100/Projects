# 📁 File Organizer

A small, dependable command-line tool that cleans up messy folders (looking at you, `Downloads`) by automatically sorting files into category folders — Images, Documents, Video, Code, and so on — based on file extension, with optional grouping by date.

No bloat, no GUI you don't need, no external dependencies for the core tool. Just point it at a folder and let it work.

## Why this exists

Most "file organizer" scripts you find online are 20-line one-offs that move files with no way to undo the change, no duplicate detection, and no tests. This one is built the way you'd actually want to run it on your own machine:

- **Safe by default** — dry-run mode lets you preview every move before committing to it
- **Reversible** — the last run can be undone
- **Duplicate-aware** — identical files (by content hash, not just name) are detected and skipped rather than silently overwritten
- **Configurable** — bring your own category → extension mapping via JSON
- **Tested** — the core engine has a full pytest suite

## Features

| Feature | Description |
|---|---|
| Sort by type | Groups files into `Images/`, `Documents/`, `Video/`, `Audio/`, `Code/`, `Archives/`, etc. |
| Sort by date | Optional `--by-date` flag adds `Year/Month` sub-folders on top of category sorting |
| Recursive mode | `--recursive` organizes nested sub-folders too |
| Dry run | `--dry-run` shows exactly what would move, without touching anything |
| Duplicate detection | Uses SHA-256 hashing to detect true duplicates, not just matching filenames |
| Safe renaming | Same-name-but-different files are renamed (`file_1.txt`) instead of overwritten |
| Custom categories | Supply your own `categories.json` to override the defaults |
| Undo | Programmatic `organizer.undo(result)` reverses a run |

## Installation

```bash
git clone https://github.com/masoodhassan100/file-organizer.git
cd file-organizer
pip install -r requirements.txt
```

No third-party runtime dependencies are required — `requirements.txt` only installs `pytest` for running the test suite.

## Usage

```bash
# Organize a folder by file type
python main.py ~/Downloads

# Preview changes first (recommended the first time)
python main.py ~/Downloads --dry-run

# Also group by year/month based on last-modified date
python main.py ~/Downloads --by-date

# Organize sub-folders too
python main.py ~/Downloads --recursive

# Use your own category mapping
python main.py ~/Downloads --config config.example.json

# See all options
python main.py --help
```

### Example output

```
14:22:01 [INFO] Found 42 file(s) to process in /home/user/Downloads
14:22:01 [INFO] Moved /home/user/Downloads/invoice.pdf -> /home/user/Downloads/Documents/invoice.pdf
14:22:01 [INFO] Moved /home/user/Downloads/vacation.jpg -> /home/user/Downloads/Images/vacation.jpg
...

Moved: 39 | Skipped: 0 | Duplicates: 3 | Errors: 0
```

### Install as a CLI command (optional)

```bash
pip install -e .
file-organizer ~/Downloads --dry-run
```

## Project structure

```
file-organizer/
├── file_organizer/
│   ├── __init__.py
│   ├── cli.py           # argument parsing and CLI entry point
│   ├── config.py        # default category → extension mapping
│   └── organizer.py      # core engine: scanning, moving, undo, duplicates
├── tests/
│   └── test_organizer.py
├── config.example.json  # sample custom category file
├── main.py              # `python main.py <dir>` entry point
├── requirements.txt
├── setup.py
└── LICENSE
```

## Running tests

```bash
pip install -r requirements.txt
pytest -v
```

## Roadmap / ideas for contributions

- [ ] Config-driven ignore list (skip certain files/patterns)
- [ ] Watch mode — organize a folder continuously as new files arrive
- [ ] Optional GUI (Tkinter or a small web front-end)
- [ ] Packaging for `pipx install`

Pull requests are welcome — this is a good project to practice contributing to open source.

## License

MIT — see [LICENSE](LICENSE).
