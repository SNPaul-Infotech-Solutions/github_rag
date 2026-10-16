from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


from github_rag.domain.enums import (
    FileStatus,
    FileType,
    RepositorySourceType,
)


class RepositoryReference(BaseModel):
    """Identifies a source repository and how it was obtained."""

    model_config = ConfigDict(frozen=True)

    name: str
    source_type: RepositorySourceType
    local_path: Path

    organization: str | None = None
    remote_url: str | None = None
    branch: str | None = None
    commit_sha: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Repository name cannot be empty")

        return cleaned_value

    @field_validator("local_path")
    @classmethod
    def normalize_local_path(cls, value: Path) -> Path:
        return value.expanduser().resolve()
    

class RepositoryFile(BaseModel):
    """Represents metadata for a file discovered in a repository."""

    model_config = ConfigDict(frozen=True)

    repository_name: str

    absolute_path: Path
    relative_path: str
    directory: str

    file_name: str
    extension: str

    file_type: FileType
    language: str | None = None

    size_bytes: int = Field(ge=0)
    status: FileStatus
    status_reason: str | None = None

    content_hash: str | None = None
    modified_at: datetime | None = None

    @field_validator("extension")
    @classmethod
    def normalize_extension(cls, value: str) -> str:
        cleaned_value = value.strip().lower()

        if not cleaned_value:
            return ""

        if not cleaned_value.startswith("."):
            return f".{cleaned_value}"

        return cleaned_value
    
class RepositoryInventory(BaseModel):
    """Represents an inventory snapshot of a repository."""

    model_config = ConfigDict(frozen=True)

    repository: RepositoryReference
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    total_files_discovered: int = Field(ge=0)
    total_files_eligible: int = Field(ge=0)
    total_files_excluded: int = Field(ge=0)

    files: list[RepositoryFile]

    @model_validator(mode="after")
    def validate_file_counts(self) -> "RepositoryInventory":
        actual_discovered = len(self.files)

        if self.total_files_discovered != actual_discovered:
            raise ValueError(
                "total_files_discovered must match the number of files"
            )

        if (
            self.total_files_eligible + self.total_files_excluded
            != self.total_files_discovered
        ):
            raise ValueError(
                "Eligible and excluded file counts must equal "
                "total_files_discovered"
            )

        return self

class ExtractedDocument(BaseModel):
    """Represents content extracted from an eligible repository file."""

    model_config = ConfigDict(frozen=True)

    document_id: str

    repository_name: str
    relative_path: str
    file_name: str

    file_type: FileType
    language: str | None = None

    content: str
    line_count: int = Field(ge=1)

    content_hash: str

    branch: str | None = None
    commit_sha: str | None = None
    source_url: str | None = None

    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    @field_validator(
        "document_id",
        "repository_name",
        "relative_path",
        "file_name",
        "content_hash",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Value cannot be empty")

        return cleaned_value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError(
                "Extracted document content cannot be empty"
            )

        return value