from pathlib import Path

from github_rag.core.exceptions import ExtractionError


class TextFileReader:
    """Safely reads text content from repository files."""

    def __init__(
        self,
        encoding: str = "utf-8",
    ) -> None:
        self._encoding = encoding

    def read(self, file_path: Path) -> str:
        """Read and return text content from a file."""

        resolved_path = file_path.expanduser().resolve()

        if not resolved_path.exists():
            raise ExtractionError(
                f"File does not exist: {resolved_path}"
            )

        if not resolved_path.is_file():
            raise ExtractionError(
                f"Path is not a file: {resolved_path}"
            )

        try:
            content = resolved_path.read_text(
                encoding=self._encoding
            )
        except UnicodeDecodeError as error:
            raise ExtractionError(
                f"Unable to decode file using "
                f"{self._encoding}: {resolved_path}"
            ) from error
        except OSError as error:
            raise ExtractionError(
                f"Unable to read file {resolved_path}: {error}"
            ) from error

        if not content.strip():
            raise ExtractionError(
                f"File contains no readable text: {resolved_path}"
            )

        return content
