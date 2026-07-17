"""
Default configuration for File Organizer.

Users can override this by supplying their own JSON config file
via the --config CLI flag. See config.example.json for the format.
"""

from __future__ import annotations

DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
    "Presentations": [".ppt", ".pptx", ".odp"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css", ".json", ".sh"],
    "Executables": [".exe", ".msi", ".dmg", ".apk", ".deb"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
}

# Anything not matched above goes here.
FALLBACK_CATEGORY = "Others"
