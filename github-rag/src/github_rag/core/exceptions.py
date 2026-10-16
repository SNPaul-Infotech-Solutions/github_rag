class GitHubRagError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(GitHubRagError):
    """Raised when the application configuration is invalid."""


class RepositoryAccessError(GitHubRagError):
    """Raised when a repository cannot be accessed."""

class ExtractionError(GitHubRagError):
    """Raised when content cannot be extracted from a repository file."""