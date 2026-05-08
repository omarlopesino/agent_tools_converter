"""Walk source directories to find files to convert.

Only processes top-level entries (no recursion).
"""

from pathlib import Path


def list_skill_dirs(path: str) -> list:
    """List subdirectories in a skills folder, one per skill.

    Each subdirectory is expected to contain a SKILL.md file.

    Args:
        path: Path to the skills source directory.

    Returns:
        List of Path objects for each skill subdirectory.
    """
    source = Path(path)
    if not source.is_dir():
        raise FileNotFoundError(f"Source folder not found: {path}")

    skill_dirs = []
    for entry in source.iterdir():
        if entry.is_dir() and (entry / "SKILL.md").exists():
            skill_dirs.append(entry)
    return skill_dirs


def list_md_files(path: str) -> list:
    """List .md files in a folder (agents or commands).

    Only top-level files are returned, no recursion.

    Args:
        path: Path to the agents or commands source directory.

    Returns:
        List of Path objects for each .md file.
    """
    source = Path(path)
    if not source.is_dir():
        raise FileNotFoundError(f"Source folder not found: {path}")

    md_files = []
    for entry in sorted(source.iterdir()):
        if entry.is_file() and entry.suffix == ".md":
            md_files.append(entry)
    return md_files
