from setuptools import setup, find_packages

setup(
    name="file-organizer",
    version="1.0.0",
    description="A CLI tool that automatically organizes files in a directory by type and date.",
    author="HASSAN MASOOD",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "file-organizer=file_organizer.cli:main",
        ],
    },
)
