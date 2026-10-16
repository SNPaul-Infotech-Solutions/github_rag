from datetime import UTC, datetime
from pathlib import Path

from github_rag.connectors.base import RepositoryConnector
from github_rag.domain.models import RepositoryFile, RepositoryInventory
from github_rag.inventory.classifier import FileClassifier
from github_rag.inventory.file_policy import FilePolicy
from github_rag.inventory.hash_service import ContentHashService
from github_rag.domain.enums import FileStatus


class RepositoryInventoryService:
    """Creates file metadata for files discovered in a repository."""

    def __init__(
        self,
        connector: RepositoryConnector,
        file_policy: FilePolicy,
        classifier: FileClassifier,
        hash_service: ContentHashService,
    ) -> None:
        self._connector = connector
        self._file_policy = file_policy
        self._classifier = classifier
        self._hash_service = hash_service
    
    def generate(self) -> RepositoryInventory:
        """Generate a complete inventory of the repository."""

        repository = self._connector.get_repository_reference()

        repository_files = [
            self.inspect_file(file_path)
            for file_path in self._connector.iter_files()
        ]

        eligible_count = sum(
            1
            for repository_file in repository_files
            if repository_file.status is FileStatus.ELIGIBLE
        )

        excluded_count = len(repository_files) - eligible_count

        return RepositoryInventory(
            repository=repository,
            total_files_discovered=len(repository_files),
            total_files_eligible=eligible_count,
            total_files_excluded=excluded_count,
            files=repository_files,
        )

    def inspect_file(
        self,
        file_path: Path,
    ) -> RepositoryFile:
        """Inspect one repository file and return its metadata."""

        repository = self._connector.get_repository_reference()
        relative_path = file_path.relative_to(repository.local_path)

        eligibility = self._file_policy.evaluate(file_path)
        file_type, language = self._classifier.classify(file_path)

        try:
            file_stat = file_path.stat()
            size_bytes = file_stat.st_size
            modified_at = datetime.fromtimestamp(
                file_stat.st_mtime,
                tz=UTC,
            )
        except OSError:
            size_bytes = 0
            modified_at = None

        content_hash = None

        if eligibility.eligible:
            content_hash = self._hash_service.calculate(file_path)

        return RepositoryFile(
            repository_name=repository.name,
            absolute_path=file_path.resolve(),
            relative_path=relative_path.as_posix(),
            directory=relative_path.parent.as_posix(),
            file_name=file_path.name,
            extension=file_path.suffix,
            file_type=file_type,
            language=language,
            size_bytes=size_bytes,
            status=eligibility.status,
            status_reason=eligibility.reason,
            content_hash=content_hash,
            modified_at=modified_at,
        )