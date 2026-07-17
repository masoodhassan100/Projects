#!/usr/bin/env python3
"""Convenience entry point so the tool can be run as `python main.py <dir>`."""

from file_organizer.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
