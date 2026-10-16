from typing import Protocol

from github_rag.domain.enums import FileType
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryFile,
)


class DocumentParser(Protocol):
    """Defines the behavior required from a document parser."""

    @property
    def supported_file_types(self) -> frozenset:
        
        """Return the file types supported by this parser."""
        ...

    def can_parse(self, repository_file: RepositoryFile) -> bool:
        """Return whether this parser can process the repository file."""
        ...

    def parse(
        self,
        repository_file: RepositoryFile,
    ) -> ExtractedDocument:
        """Extract content from a repository file."""
        ...