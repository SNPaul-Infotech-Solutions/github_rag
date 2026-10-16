import json

import yaml

from github_rag.core.exceptions import ExtractionError
from github_rag.domain.enums import FileStatus, FileType
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryFile,
)
from github_rag.extraction.text_reader import TextFileReader


class ConfigurationParser:
    """Extracts and validates YAML and JSON configuration files."""

    _SUPPORTED_EXTENSIONS = frozenset({
        ".yaml",
        ".yml",
        ".json",
    })

    def __init__(
        self,
        text_reader: TextFileReader,
    ) -> None:
        self._text_reader = text_reader

    @property
    def supported_file_types(self) -> frozenset:
        
        """Return the file types supported by this parser."""

        return frozenset({FileType.CONFIGURATION})

    def can_parse(
        self,
        repository_file: RepositoryFile,
    ) -> bool:
        """Return whether this parser can process the repository file."""

        return (
            repository_file.status is FileStatus.ELIGIBLE
            and repository_file.file_type in self.supported_file_types
            and repository_file.extension
            in self._SUPPORTED_EXTENSIONS
        )

    def parse(
        self,
        repository_file: RepositoryFile,
    ) -> ExtractedDocument:
        """Extract and validate configuration-file content."""

        if not self.can_parse(repository_file):
            raise ExtractionError(
                "ConfigurationParser cannot process file: "
                f"{repository_file.relative_path}"
            )

        if repository_file.content_hash is None:
            raise ExtractionError(
                "Eligible repository file does not have a content hash: "
                f"{repository_file.relative_path}"
            )

        content = self._text_reader.read(
            repository_file.absolute_path
        )

        self._validate_syntax(
            content=content,
            extension=repository_file.extension,
            relative_path=repository_file.relative_path,
        )

        document_id = (
            f"{repository_file.repository_name}:"
            f"{repository_file.relative_path}"
        )

        return ExtractedDocument(
            document_id=document_id,
            repository_name=repository_file.repository_name,
            relative_path=repository_file.relative_path,
            file_name=repository_file.file_name,
            file_type=repository_file.file_type,
            language=repository_file.language,
            content=content,
            line_count=len(content.splitlines()),
            content_hash=repository_file.content_hash,
        )

    @staticmethod
    def _validate_syntax(
        content: str,
        extension: str,
        relative_path: str,
    ) -> None:
        """Validate YAML or JSON syntax without modifying content."""

        try:
            if extension == ".json":
                json.loads(content)
            else:
                yaml.safe_load(content)

        except json.JSONDecodeError as error:
            raise ExtractionError(
                f"Invalid JSON in {relative_path} "
                f"at line {error.lineno}, column {error.colno}: "
                f"{error.msg}"
            ) from error

        except yaml.YAMLError as error:
            raise ExtractionError(
                f"Invalid YAML in {relative_path}: {error}"
            ) from error