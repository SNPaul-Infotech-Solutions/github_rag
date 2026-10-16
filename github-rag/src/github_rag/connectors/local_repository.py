from collections.abc import Iterator
from pathlib import Path

from github_rag.core.exceptions import RepositoryAccessError
from github_rag.domain.enums import RepositorySourceType
from github_rag.domain.models import RepositoryReference
from github_rag.inventory.file_policy import FilePolicy


class LocalRepositoryConnector:
    """Provides access to a repository available on the local filesystem."""

    def __init__(
        self,
        repository_path: Path,
        file_policy: FilePolicy,
    ) -> None:
        resolved_path = repository_path.expanduser().resolve()

        if not resolved_path.exists():
            raise RepositoryAccessError(
                f"Repository path does not exist: {resolved_path}"
            )

        if not resolved_path.is_dir():
            raise RepositoryAccessError(
                f"Repository path is not a directory: {resolved_path}"
            )

        self._repository_path = resolved_path
        self._file_policy = file_policy

    def get_repository_reference(self) -> RepositoryReference:
        """Return identity and source information for the repository."""

        return RepositoryReference(
            name=self._repository_path.name,
            source_type=RepositorySourceType.LOCAL,
            local_path=self._repository_path,
        )

    def iter_files(self) -> Iterator:
        
        """Yield files discovered inside allowed repository directories."""

        yield from self._walk_directory(self._repository_path)

    def _walk_directory(self,directory_path: Path,) -> Iterator:
        
        """Recursively traverse allowed repository directories."""

        try:
            child_paths = sorted(directory_path.iterdir())
        except OSError as error:
            raise RepositoryAccessError(
                f"Unable to read directory {directory_path}: {error}"
            ) from error

        for child_path in child_paths:
            if child_path.is_dir():
                if self._file_policy.should_traverse_directory(
                    child_path
                ):
                    yield from self._walk_directory(child_path)

                continue

            if child_path.is_file():
                yield child_path