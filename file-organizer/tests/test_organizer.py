"""Unit tests for the File Organizer engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from file_organizer.organizer import FileOrganizer


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    (tmp_path / "photo.jpg").write_text("fake image data")
    (tmp_path / "report.pdf").write_text("fake pdf data")
    (tmp_path / "notes.txt").write_text("hello world")
    (tmp_path / "script.py").write_text("print('hi')")
    (tmp_path / "unknown.xyz").write_text("mystery bytes")
    return tmp_path


def test_organize_moves_files_into_categories(sample_dir: Path):
    organizer = FileOrganizer(sample_dir)
    result = organizer.organize()

    assert (sample_dir / "Images" / "photo.jpg").exists()
    assert (sample_dir / "Documents" / "report.pdf").exists()
    assert (sample_dir / "Documents" / "notes.txt").exists()
    assert (sample_dir / "Code" / "script.py").exists()
    assert (sample_dir / "Others" / "unknown.xyz").exists()
    assert len(result.moved) == 5
    assert not result.errors


def test_dry_run_does_not_move_files(sample_dir: Path):
    organizer = FileOrganizer(sample_dir, dry_run=True)
    result = organizer.organize()

    assert (sample_dir / "photo.jpg").exists()
    assert not (sample_dir / "Images").exists()
    assert len(result.moved) == 5


def test_duplicate_files_are_skipped(sample_dir: Path):
    (sample_dir / "Images").mkdir()
    (sample_dir / "Images" / "photo.jpg").write_text("fake image data")  # identical content

    organizer = FileOrganizer(sample_dir, skip_duplicates=True)
    result = organizer.organize()

    assert len(result.duplicates) == 1
    assert (sample_dir / "photo.jpg").exists()  # original untouched


def test_by_date_creates_year_month_subfolders(sample_dir: Path):
    organizer = FileOrganizer(sample_dir, by_date=True)
    result = organizer.organize()

    moved_paths = [dest for _, dest in result.moved]
    assert any(p.parent.parent.name.isdigit() for p in moved_paths)


def test_custom_config_file(tmp_path: Path):
    (tmp_path / "song.mp3").write_text("fake audio")
    config_path = tmp_path / "categories.json"
    config_path.write_text(json.dumps({"Music": [".mp3"]}))

    organizer = FileOrganizer.from_config_file(tmp_path, config_path)
    organizer.organize()

    assert (tmp_path / "Music" / "song.mp3").exists()


def test_undo_restores_original_locations(sample_dir: Path):
    organizer = FileOrganizer(sample_dir)
    result = organizer.organize()
    organizer.undo(result)

    assert (sample_dir / "photo.jpg").exists()
    assert not (sample_dir / "Images").exists()


def test_raises_for_missing_directory(tmp_path: Path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        FileOrganizer(missing)
