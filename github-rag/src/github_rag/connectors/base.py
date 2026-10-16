from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from github_rag.domain.models import RepositoryReference


class RepositoryConnector(Protocol):
    """Defines the operations required from a repository connector."""

    def get_repository_reference(self) -> RepositoryReference:

        """Return identity and source information for the repository."""
        ...

    def iter_files(self) -> Iterator:
    
        """Yield file paths discovered in the repository."""
        ...