from enum import StrEnum


class RepositorySourceType(StrEnum):
    """Supported sources from which repository content can be obtained."""

    LOCAL = "local"
    GITHUB_API = "github_api"
    GITHUB_CLONE = "github_clone"
    CLOUD_STORAGE = "cloud_storage"

class FileType(StrEnum):
    """Logical categories of files supported by the RAG pipeline."""

    SOURCE_CODE = "source_code"
    SQL = "sql"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    NOTEBOOK = "notebook"
    DEPENDENCY = "dependency"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"

class FileStatus(StrEnum):
    """Possible outcomes of repository file eligibility checks."""

    ELIGIBLE = "eligible"
    EXCLUDED_DIRECTORY = "excluded_directory"
    EXCLUDED_FILE_NAME = "excluded_file_name"
    EXCLUDED_EXTENSION = "excluded_extension"
    UNSUPPORTED_TYPE = "unsupported_type"
    TOO_LARGE = "too_large"
    BINARY = "binary"
    EMPTY = "empty"
    UNREADABLE = "unreadable"