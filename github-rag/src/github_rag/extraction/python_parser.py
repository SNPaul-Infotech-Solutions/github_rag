import ast

from github_rag.core.exceptions import ExtractionError
from github_rag.domain.enums import FileStatus, FileType
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryFile,
)
from github_rag.extraction.text_reader import TextFileReader


class PythonParser:
    """Extracts and validates content from Python source files."""

    def __init__(
        self,
        text_reader: TextFileReader,
    ) -> None:
        self._text_reader = text_reader

    @property
    def supported_file_types(self) -> frozenset:
        
        """Return the file types supported by this parser."""

        return frozenset({FileType.SOURCE_CODE})

    def can_parse(
        self,
        repository_file: RepositoryFile,
    ) -> bool:
        """Return whether this parser can process the repository file."""

        return (
            repository_file.status is FileStatus.ELIGIBLE
            and repository_file.file_type in self.supported_file_types
            and repository_file.extension == ".py"
        )

    def parse(
        self,
        repository_file: RepositoryFile,
    ) -> ExtractedDocument:
        """Extract and validate Python source code."""

        if not self.can_parse(repository_file):
            raise ExtractionError(
                "PythonParser cannot process file: "
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
            file_name=repository_file.relative_path,
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
        file_name: str,
    ) -> None:
        """Validate Python syntax without executing the source code."""

        try:
            ast.parse(
                source=content,
                filename=file_name,
            )
        except SyntaxError as error:
            raise ExtractionError(
                f"Invalid Python syntax in {file_name} "
                f"at line {error.lineno}: {error.msg}"
            ) from error