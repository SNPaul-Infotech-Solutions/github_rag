from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from github_rag.core.exceptions import ConfigurationError
from github_rag.domain.enums import FileStatus


class FilePolicyConfig(BaseModel):
    """Configuration containing repository file-selection rules."""

    model_config = ConfigDict(frozen=True)

    excluded_directories: frozenset[str] = Field(default_factory=frozenset)
    excluded_file_names: frozenset[str] = Field(default_factory=frozenset)
    excluded_extensions: frozenset[str] = Field(default_factory=frozenset)
    supported_extensions: frozenset[str] = Field(default_factory=frozenset)


class FileEligibilityResult(BaseModel):
    """Result of evaluating a repository file against the file policy."""

    model_config = ConfigDict(frozen=True)

    eligible: bool
    status: FileStatus
    reason: str

class FilePolicy:
    """Evaluates repository files against configured selection rules."""

    def __init__(
        self,
        config: FilePolicyConfig,
        max_file_size_bytes: int,
    ) -> None:
        if max_file_size_bytes <= 0:
            raise ValueError(
                "max_file_size_bytes must be greater than zero"
            )

        self._config = config
        self._max_file_size_bytes = max_file_size_bytes
    
    @classmethod
    def from_yaml(cls,config_path: Path,max_file_size_bytes: int,) -> Self:
        
        """Create a file policy from a YAML configuration file."""

        resolved_path = config_path.expanduser().resolve()

        if not resolved_path.exists():
            raise ConfigurationError(
                f"File-policy configuration does not exist: "
                f"{resolved_path}"
            )

        if not resolved_path.is_file():
            raise ConfigurationError(
                f"File-policy configuration is not a file: "
                f"{resolved_path}"
            )

        try:
            with resolved_path.open("r", encoding="utf-8") as config_file:
                raw_config = yaml.safe_load(config_file) or {}
        except (OSError, yaml.YAMLError) as error:
            raise ConfigurationError(
                f"Unable to load file-policy configuration: {error}"
            ) from error

        if not isinstance(raw_config, dict):
            raise ConfigurationError(
                "File-policy configuration must contain a YAML mapping"
            )

        try:
            config = FilePolicyConfig.model_validate(raw_config)
        except ValidationError as error:
            raise ConfigurationError(
                f"Invalid file-policy configuration: {error}"
            ) from error

        return cls(
            config=config,
            max_file_size_bytes=max_file_size_bytes,
        )

    def evaluate(self, file_path: Path) -> FileEligibilityResult:
        """Evaluate whether a file is eligible for processing."""

        excluded_parent = self._find_excluded_parent(file_path)

        if excluded_parent is not None:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.EXCLUDED_DIRECTORY,
                reason=(
                    f"File belongs to excluded directory: "
                    f"{excluded_parent}"
                ),
            )

        if file_path.name.lower() in self._normalized_excluded_file_names:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.EXCLUDED_FILE_NAME,
                reason=(
                    f"Filename is explicitly excluded: "
                    f"{file_path.name}"
                ),
            )

        extension = file_path.suffix.lower()

        if extension in self._normalized_excluded_extensions:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.EXCLUDED_EXTENSION,
                reason=f"File extension is excluded: {extension}",
            )

        if extension not in self._normalized_supported_extensions:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.UNSUPPORTED_TYPE,
                reason=(
                    f"File extension is not supported: "
                    f"{extension or '<no extension>'}"
                ),
            )

        try:
            file_size = file_path.stat().st_size
        except OSError as error:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.UNREADABLE,
                reason=f"Unable to read file metadata: {error}",
            )
        
        if file_size == 0:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.EMPTY,
                reason="File is empty",
            )

        if file_size > self._max_file_size_bytes:
            return FileEligibilityResult(
                eligible=False,
                status=FileStatus.TOO_LARGE,
                reason=(
                    f"File size {file_size} bytes exceeds maximum "
                    f"allowed size of {self._max_file_size_bytes} bytes"
                ),
            )

        return FileEligibilityResult(
            eligible=True,
            status=FileStatus.ELIGIBLE,
            reason="File passed the current eligibility checks",
        )
    
    def should_traverse_directory(self, directory_path: Path) -> bool:
        
        """Return whether the repository scanner should enter a directory."""

        excluded_directories = {
            directory.lower()
            for directory in self._config.excluded_directories
        }

        return directory_path.name.lower() not in excluded_directories

    def _find_excluded_parent(self, file_path: Path) -> str | None:
        """Return the excluded parent-directory name, if one exists."""

        excluded_directories = {
            directory.lower()
            for directory in self._config.excluded_directories
        }

        for parent in file_path.parents:
            if parent.name.lower() in excluded_directories:
                return parent.name

        return None

    @property
    def _normalized_excluded_file_names(self) -> set[str]:

        """Return excluded filenames normalized to lowercase."""

        return {
            file_name.lower()
            for file_name in self._config.excluded_file_names
        }

    @property
    def _normalized_excluded_extensions(self) -> set[str]:
        
        """Return excluded extensions normalized to lowercase."""

        return {
            extension.lower()
            for extension in self._config.excluded_extensions
        }

    @property
    def _normalized_supported_extensions(self) -> set[str]:
        
        """Return supported extensions normalized to lowercase."""

        return {
            extension.lower()
            for extension in self._config.supported_extensions
        }