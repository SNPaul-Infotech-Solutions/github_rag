import tomllib

from github_rag.core.exceptions import ExtractionError
from github_rag.domain.enums import FileStatus, FileType
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryFile,
)
from github_rag.extraction.text_reader import TextFileReader


class DependencyParser:
    """Extracts content from supported dependency files."""

    _SUPPORTED_FILE_NAMES = frozenset({
        "requirements.txt",
        "pyproject.toml",
    })

    def __init__(
        self,
        text_reader: TextFileReader,
    ) -> None:
        self._text_reader = text_reader

    @property
    def supported_file_types(self) -> frozenset:
        
        """Return the file types supported by this parser."""

        return frozenset({FileType.DEPENDENCY})

    def can_parse(
        self,
        repository_file: RepositoryFile,
    ) -> bool:
        """Return whether this parser can process the repository file."""

        return (
            repository_file.status is FileStatus.ELIGIBLE
            and repository_file.file_type in self.supported_file_types
            and repository_file.file_name.lower()
            in self._SUPPORTED_FILE_NAMES
        )

    def parse(
        self,
        repository_file: RepositoryFile,
    ) -> ExtractedDocument:
        """Extract content from an eligible dependency file."""

        if not self.can_parse(repository_file):
            raise ExtractionError(
                "DependencyParser cannot process file: "
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

        if repository_file.file_name.lower() == "pyproject.toml":
            self._validate_toml(
                content=content,
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
    def _validate_toml(
        content: str,
        relative_path: str,
    ) -> None:
        """Validate TOML syntax without modifying the original content."""

        try:
            tomllib.loads(content)
        except tomllib.TOMLDecodeError as error:
            raise ExtractionError(
                f"Invalid TOML in {relative_path}: {error}"
            ) from error