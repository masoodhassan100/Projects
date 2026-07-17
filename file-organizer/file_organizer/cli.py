"""
Command-line interface for File Organizer.

Examples
--------
    python main.py ~/Downloads
    python main.py ~/Downloads --by-date --recursive
    python main.py ~/Downloads --dry-run
    python main.py ~/Downloads --config my_categories.json
"""

from __future__ import annotations

import argparse
import logging
import sys

from file_organizer.organizer import FileOrganizer

__version__ = "1.0.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Automatically organize files in a directory by type (and optionally by date).",
    )
    parser.add_argument("directory", help="Path to the directory you want to organize")
    parser.add_argument(
        "--by-date",
        action="store_true",
        help="Additionally group files into year/month sub-folders based on last modified date",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into sub-directories instead of only organizing the top level",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving any files",
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to a JSON file defining custom category -> extensions mappings",
    )
    parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="Move duplicate files instead of skipping them (default: skip exact duplicates)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose (DEBUG level) logging"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        if args.config:
            organizer = FileOrganizer.from_config_file(
                target_dir=args.directory,
                config_path=args.config,
                by_date=args.by_date,
                dry_run=args.dry_run,
                recursive=args.recursive,
                skip_duplicates=not args.keep_duplicates,
            )
        else:
            organizer = FileOrganizer(
                target_dir=args.directory,
                by_date=args.by_date,
                dry_run=args.dry_run,
                recursive=args.recursive,
                skip_duplicates=not args.keep_duplicates,
            )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = organizer.organize()
    print("\n" + result.summary())
    if args.dry_run:
        print("(dry run — no files were actually moved)")
    return 0 if not result.errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
