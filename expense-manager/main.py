#!/usr/bin/env python3
"""Convenience entry point so the tool can be run as `python main.py <command>`."""

from expense_manager.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
