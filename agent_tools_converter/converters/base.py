"""Abstract base class for all converters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseConverter(ABC):
    """Abstract base class defining the converter interface.

    Each concrete converter implements direction-specific field mappings
    while sharing common frontmatter handling logic.
    """

    # Subclasses override these
    source_fields: set = set()
    destination_fields: set = set()

    @abstractmethod
    def convert_file(self, source_path: str, dest_path: str) -> dict:
        """Convert a single file from source format to destination format.

        Args:
            source_path: Path to the source file.
            dest_path: Path to write the converted file.

        Returns:
            Dict with 'success', 'source', 'dest', 'skipped' info.
        """
        ...

    @abstractmethod
    def convert_folder(self, source_dir: str, dest_dir: str) -> list:
        """Convert all files in a source directory to the destination.

        Args:
            source_dir: Path to the source directory.
            dest_dir: Path to write converted files.

        Returns:
            List of result dicts from convert_file.
        """
        ...

    @staticmethod
    def _extract_mapped(source_fm: dict, known_source: set, dest_fm: dict) -> dict:
        """Copy known fields from source to dest, collect unknowns into metadata.

        Fields in known_source that exist in source_fm are copied to dest_fm.
        All other source fields are collected under a 'metadata' key in dest_fm.

        Args:
            source_fm: Source frontmatter dictionary.
            known_source: Set of field names that have direct equivalents.
            dest_fm: Destination frontmatter dictionary to populate.

        Returns:
            The populated dest_fm dictionary.
        """
        metadata = {}
        for key, value in source_fm.items():
            if key in known_source:
                dest_fm[key] = value
            else:
                metadata[key] = value

        if metadata:
            dest_fm["metadata"] = metadata

        return dest_fm

    @staticmethod
    def _restore_metadata(source_fm: dict, dest_fm: dict) -> dict:
        """Expand metadata dict back to top-level fields.

        The 'metadata' key from the source is expanded so each key-value
        pair becomes a top-level entry in dest_fm. The metadata key itself
        is not copied.

        Args:
            source_fm: Source frontmatter dictionary containing a 'metadata' key.
            dest_fm: Destination frontmatter dictionary to populate.

        Returns:
            The populated dest_fm dictionary.
        """
        metadata = source_fm.get("metadata", {})
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                dest_fm[key] = value
        return dest_fm
