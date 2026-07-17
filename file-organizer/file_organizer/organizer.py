"""
Core engine that scans a directory and organizes files into
category sub-folders based on extension, with optional
date-based sorting, duplicate handling, and dry-run support.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from file_organizer.config import DEFAULT_CATEGORIES, FALLBACK_CATEGORY

logger = logging.getLogger("file_organizer")


@dataclass
class OrganizeResult:
    """Summary of a single organize run."""

    moved: list[tuple[Path, Path]] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    duplicates: list[Path] = field(default_factory=list)
    errors: list[tuple[Path, str]] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return len(self.moved) + len(self.skipped) + len(self.duplicates)

    def summary(self) -> str:
        return (
            f"Moved: {len(self.moved)} | "
            f"Skipped: {len(self.skipped)} | "
            f"Duplicates: {len(self.duplicates)} | "
            f"Errors: {len(self.errors)}"
        )


class FileOrganizer:
    """Organizes files in a target directory into category folders."""

    def __init__(
        self,
        target_dir: str | Path,
        categories: dict[str, list[str]] | None = None,
        by_date: bool = False,
        dry_run: bool = False,
        recursive: bool = False,
        skip_duplicates: bool = True,
    ) -> None:
        self.target_dir = Path(target_dir).expanduser().resolve()
        self.categories = categories or DEFAULT_CATEGORIES
        self.by_date = by_date
        self.dry_run = dry_run
        self.recursive = recursive
        self.skip_duplicates = skip_duplicates
        self._ext_lookup = self._build_ext_lookup(self.categories)

        if not self.target_dir.exists():
            raise FileNotFoundError(f"Target directory does not exist: {self.target_dir}")
        if not self.target_dir.is_dir():
            raise NotADirectoryError(f"Target path is not a directory: {self.target_dir}")

    @staticmethod
    def _build_ext_lookup(categories: dict[str, list[str]]) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for category, extensions in categories.items():
            for ext in extensions:
                lookup[ext.lower()] = category
        return lookup

    @classmethod
    def from_config_file(cls, target_dir: str | Path, config_path: str | Path, **kwargs) -> "FileOrganizer":
        """Build an organizer using a user-supplied JSON category map."""
        with open(config_path, "r", encoding="utf-8") as f:
            categories = json.load(f)
        return cls(target_dir=target_dir, categories=categories, **kwargs)

    def _category_for(self, file_path: Path) -> str:
        return self._ext_lookup.get(file_path.suffix.lower(), FALLBACK_CATEGORY)

    def _destination_for(self, file_path: Path) -> Path:
        category = self._category_for(file_path)
        dest_dir = self.target_dir / category

        if self.by_date:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            dest_dir = dest_dir / mtime.strftime("%Y") / mtime.strftime("%m-%B")

        return dest_dir

    @staticmethod
    def _file_hash(path: Path, chunk_size: int = 65536) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _is_duplicate(self, source: Path, existing: Path) -> bool:
        try:
            if source.stat().st_size != existing.stat().st_size:
                return False
            return self._file_hash(source) == self._file_hash(existing)
        except OSError:
            return False

    def _unique_destination(self, dest: Path) -> Path:
        """Avoid overwriting a same-named but different file."""
        if not dest.exists():
            return dest
        stem, suffix = dest.stem, dest.suffix
        counter = 1
        candidate = dest
        while candidate.exists():
            candidate = dest.with_name(f"{stem}_{counter}{suffix}")
            counter += 1
        return candidate

    def _iter_files(self):
        if self.recursive:
            for path in self.target_dir.rglob("*"):
                if path.is_file() and self._is_organizable(path):
                    yield path
        else:
            for path in self.target_dir.iterdir():
                if path.is_file() and self._is_organizable(path):
                    yield path

    def _is_organizable(self, path: Path) -> bool:
        # Never move the organizer's own output folders back into themselves,
        # and skip hidden/system files.
        if path.name.startswith("."):
            return False
        known_category_dirs = set(self.categories.keys()) | {FALLBACK_CATEGORY}
        return not any(part in known_category_dirs for part in path.relative_to(self.target_dir).parts[:-1])

    def organize(self) -> OrganizeResult:
        """Run the organize pass and return a summary result."""
        result = OrganizeResult()
        files = list(self._iter_files())
        logger.info("Found %d file(s) to process in %s", len(files), self.target_dir)

        for file_path in files:
            try:
                dest_dir = self._destination_for(file_path)
                dest_path = dest_dir / file_path.name

                if dest_path.exists() and self._is_duplicate(file_path, dest_path):
                    if self.skip_duplicates:
                        result.duplicates.append(file_path)
                        logger.debug("Duplicate skipped: %s", file_path)
                        continue

                dest_path = self._unique_destination(dest_path)

                if self.dry_run:
                    logger.info("[DRY RUN] %s -> %s", file_path, dest_path)
                else:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                    logger.info("Moved %s -> %s", file_path, dest_path)

                result.moved.append((file_path, dest_path))

            except Exception as exc:  # noqa: BLE001 - report and continue
                logger.error("Failed to process %s: %s", file_path, exc)
                result.errors.append((file_path, str(exc)))

        return result

    def undo(self, result: OrganizeResult) -> None:
        """Reverse a previous organize run using its recorded moves."""
        for original, moved_to in reversed(result.moved):
            try:
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(moved_to), str(original))
                logger.info("Restored %s -> %s", moved_to, original)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to restore %s: %s", moved_to, exc)
