import hashlib
from pathlib import Path

from github_rag.core.exceptions import RepositoryAccessError


class ContentHashService:
    """Calculates a deterministic content hash for repository files."""

    def __init__(
        self,
        algorithm: str = "sha256",
        read_buffer_size: int = 64 * 1024,
    ) -> None:
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(
                f"Unsupported hashing algorithm: {algorithm}"
            )

        if read_buffer_size <= 0:
            raise ValueError(
                "read_buffer_size must be greater than zero"
            )

        self._algorithm = algorithm
        self._read_buffer_size = read_buffer_size

    def calculate(self, file_path: Path) -> str:
        """Calculate and return the content hash of a file."""

        resolved_path = file_path.expanduser().resolve()

        if not resolved_path.exists():
            raise RepositoryAccessError(
                f"File does not exist: {resolved_path}"
            )

        if not resolved_path.is_file():
            raise RepositoryAccessError(
                f"Path is not a file: {resolved_path}"
            )

        digest = hashlib.new(self._algorithm)

        try:
            with resolved_path.open("rb") as source_file:
                while chunk := source_file.read(
                    self._read_buffer_size
                ):
                    digest.update(chunk)
        except OSError as error:
            raise RepositoryAccessError(
                f"Unable to calculate hash for {resolved_path}: {error}"
            ) from error

        return digest.hexdigest()