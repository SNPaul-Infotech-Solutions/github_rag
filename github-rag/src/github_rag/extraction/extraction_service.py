from pydantic import BaseModel, ConfigDict, Field

from github_rag.core.exceptions import ExtractionError
from github_rag.domain.enums import FileStatus
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryInventory,
)
from github_rag.extraction.parser_registry import ParserRegistry


class ExtractionFailure(BaseModel):
    """Represents a file that could not be extracted."""

    model_config = ConfigDict(frozen=True)

    relative_path: str
    reason: str


class RepositoryExtractionResult(BaseModel):
    """Contains the results of repository content extraction."""

    model_config = ConfigDict(frozen=True)

    total_eligible_files: int = Field(ge=0)
    total_documents_extracted: int = Field(ge=0)
    total_extraction_failures: int = Field(ge=0)

    documents: tuple[ExtractedDocument, ...]
    failures: tuple[ExtractionFailure, ...]


class RepositoryExtractionService:
    """Extracts documents from eligible repository files."""

    def __init__(
        self,
        parser_registry: ParserRegistry,
    ) -> None:
        self._parser_registry = parser_registry

    def extract(
        self,
        inventory: RepositoryInventory,
    ) -> RepositoryExtractionResult:
        """Extract all supported eligible files in a repository inventory."""

        eligible_files = [
            repository_file
            for repository_file in inventory.files
            if repository_file.status is FileStatus.ELIGIBLE
        ]

        documents: list[ExtractedDocument] = []
        failures: list[ExtractionFailure] = []

        for repository_file in eligible_files:
            try:
                document = self._parser_registry.parse(
                    repository_file
                )
                documents.append(document)

            except ExtractionError as error:
                failures.append(
                    ExtractionFailure(
                        relative_path=repository_file.relative_path,
                        reason=str(error),
                    )
                )

        return RepositoryExtractionResult(
            total_eligible_files=len(eligible_files),
            total_documents_extracted=len(documents),
            total_extraction_failures=len(failures),
            documents=tuple(documents),
            failures=tuple(failures),
        )