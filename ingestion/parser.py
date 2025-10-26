"""
Obsidian Markdown Parser

Parses Obsidian markdown files with support for:
- YAML frontmatter
- Wikilinks [[note]] and [[note|alias]]
- Tags #tag and frontmatter tags
- Backlinks tracking
- Metadata extraction
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import frontmatter
from loguru import logger


class ObsidianNote:
    """Represents a parsed Obsidian note with metadata"""

    def __init__(
        self,
        file_path: Path,
        content: str,
        title: str,
        frontmatter: Dict,
        wikilinks: List[str],
        tags: Set[str],
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
    ):
        self.file_path = file_path
        self.content = content
        self.title = title
        self.frontmatter = frontmatter
        self.wikilinks = wikilinks
        self.tags = tags
        self.created_at = created_at
        self.modified_at = modified_at

    def to_dict(self) -> Dict:
        """Convert note to dictionary for serialization"""
        return {
            "file_path": str(self.file_path),
            "title": self.title,
            "content": self.content,
            "frontmatter": self.frontmatter,
            "wikilinks": self.wikilinks,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }


class ObsidianParser:
    """Parser for Obsidian markdown files"""

    # Regex patterns
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
    TAG_PATTERN = re.compile(r"(?:^|\s)#([a-zA-Z0-9/_-]+)")

    def __init__(self):
        self.parsed_notes: Dict[str, ObsidianNote] = {}
        self.backlinks: Dict[str, Set[str]] = {}  # note -> set of notes linking to it

    def parse_file(self, file_path: Path) -> Optional[ObsidianNote]:
        """
        Parse a single Obsidian markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            ObsidianNote object or None if parsing fails
        """
        try:
            # Read file with frontmatter parsing
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Extract frontmatter
            fm = dict(post.metadata) if post.metadata else {}

            # Get content without frontmatter
            content = post.content

            # Extract title (from frontmatter or filename)
            title = fm.get("title", file_path.stem)

            # Extract wikilinks
            wikilinks = self._extract_wikilinks(content)

            # Extract tags (from content and frontmatter)
            tags = self._extract_tags(content, fm)

            # Get file timestamps
            created_at = datetime.fromtimestamp(file_path.stat().st_ctime)
            modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)

            # Override with frontmatter dates if available
            if "created" in fm:
                try:
                    created_at = self._parse_date(fm["created"])
                except Exception:
                    pass

            if "modified" in fm:
                try:
                    modified_at = self._parse_date(fm["modified"])
                except Exception:
                    pass

            note = ObsidianNote(
                file_path=file_path,
                content=content,
                title=title,
                frontmatter=fm,
                wikilinks=wikilinks,
                tags=tags,
                created_at=created_at,
                modified_at=modified_at,
            )

            # Store for backlink tracking
            self.parsed_notes[str(file_path)] = note

            # Update backlinks
            self._update_backlinks(file_path, wikilinks)

            logger.debug(f"Parsed note: {title} ({len(wikilinks)} links, {len(tags)} tags)")

            return note

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None

    def _extract_wikilinks(self, content: str) -> List[str]:
        """
        Extract wikilinks from content.

        Supports:
        - [[Note Name]]
        - [[Note Name|Display Text]]
        - [[Note Name#Section]]
        - [[Note Name#Section|Display Text]]

        Args:
            content: Markdown content

        Returns:
            List of linked note names
        """
        links = []
        for match in self.WIKILINK_PATTERN.finditer(content):
            link = match.group(1)
            # Remove section anchors
            link = link.split("#")[0].strip()
            if link:
                links.append(link)
        return links

    def _extract_tags(self, content: str, frontmatter: Dict) -> Set[str]:
        """
        Extract tags from content and frontmatter.

        Args:
            content: Markdown content
            frontmatter: Frontmatter dictionary

        Returns:
            Set of tags (without # prefix)
        """
        tags = set()

        # Extract from content
        for match in self.TAG_PATTERN.finditer(content):
            tag = match.group(1)
            tags.add(tag)

        # Extract from frontmatter
        if "tags" in frontmatter:
            fm_tags = frontmatter["tags"]
            if isinstance(fm_tags, str):
                # Single tag as string
                tags.add(fm_tags.strip("#"))
            elif isinstance(fm_tags, list):
                # Multiple tags as list
                for tag in fm_tags:
                    if isinstance(tag, str):
                        tags.add(tag.strip("#"))

        return tags

    def _update_backlinks(self, file_path: Path, wikilinks: List[str]):
        """
        Update backlinks index.

        Args:
            file_path: Path of the note
            wikilinks: List of notes this note links to
        """
        for link in wikilinks:
            if link not in self.backlinks:
                self.backlinks[link] = set()
            self.backlinks[link].add(str(file_path))

    def _parse_date(self, date_value) -> datetime:
        """
        Parse date from various formats.

        Args:
            date_value: Date string or datetime object

        Returns:
            datetime object
        """
        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            # Try common date formats
            for fmt in [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%d/%m/%Y",
                "%d-%m-%Y",
            ]:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

        raise ValueError(f"Unable to parse date: {date_value}")

    def get_backlinks(self, note_name: str) -> Set[str]:
        """
        Get all notes that link to the given note.

        Args:
            note_name: Name of the note

        Returns:
            Set of file paths linking to this note
        """
        return self.backlinks.get(note_name, set())

    def parse_vault(
        self,
        vault_path: Path,
        file_extensions: List[str] = [".md", ".markdown"],
        exclude_folders: List[str] = [".obsidian", ".trash", "templates"],
    ) -> List[ObsidianNote]:
        """
        Parse all markdown files in an Obsidian vault.

        Args:
            vault_path: Path to the Obsidian vault
            file_extensions: List of file extensions to parse
            exclude_folders: List of folder names to exclude

        Returns:
            List of parsed ObsidianNote objects
        """
        logger.info(f"Parsing Obsidian vault at: {vault_path}")

        notes = []
        vault_path = Path(vault_path)

        if not vault_path.exists():
            logger.error(f"Vault path does not exist: {vault_path}")
            return notes

        # Find all markdown files
        for ext in file_extensions:
            for file_path in vault_path.rglob(f"*{ext}"):
                # Skip excluded folders
                if any(excluded in file_path.parts for excluded in exclude_folders):
                    continue

                note = self.parse_file(file_path)
                if note:
                    notes.append(note)

        logger.info(
            f"Parsed {len(notes)} notes from vault "
            f"({len(self.backlinks)} unique backlink targets)"
        )

        return notes

    def get_note_metadata(self, note: ObsidianNote) -> Dict:
        """
        Get enriched metadata for a note including backlinks.

        Args:
            note: ObsidianNote object

        Returns:
            Dictionary with all metadata
        """
        backlinks = self.get_backlinks(note.title)

        return {
            "title": note.title,
            "file_path": str(note.file_path),
            "tags": list(note.tags),
            "wikilinks": note.wikilinks,
            "backlinks": list(backlinks),
            "backlink_count": len(backlinks),
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "modified_at": note.modified_at.isoformat() if note.modified_at else None,
            **note.frontmatter,
        }
