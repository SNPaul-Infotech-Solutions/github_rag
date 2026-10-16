from pathlib import Path

from github_rag.domain.enums import FileType


class FileClassifier:
    """Classifies repository files by type and programming language."""

    _DEPENDENCY_FILE_NAMES: set[str] = {
        "pyproject.toml",
        "requirements.txt",
        "poetry.lock",
        "uv.lock",
        "package.json",
        "package-lock.json",
        "pom.xml",
        "build.gradle",
        "go.mod",
    }

    _INFRASTRUCTURE_FILE_NAMES: set[str] = {
        "dockerfile",
        "docker-compose.yaml",
        "docker-compose.yml",
    }

    def classify(self, file_path: Path) -> tuple[FileType, str | None]:
        """Return the logical file type and language for a file."""

        file_name = file_path.name.lower()
        extension = file_path.suffix.lower()

        if file_name in self._DEPENDENCY_FILE_NAMES:
            return FileType.DEPENDENCY, self._dependency_language(file_name)

        if file_name in self._INFRASTRUCTURE_FILE_NAMES:
            return FileType.INFRASTRUCTURE, self._infrastructure_language(
                file_name
            )

        if extension == ".tf":
            return FileType.INFRASTRUCTURE, "terraform"

        if extension == ".py":
            return FileType.SOURCE_CODE, "python"

        if extension == ".sql":
            return FileType.SQL, "sql"

        if extension == ".md":
            return FileType.DOCUMENTATION, "markdown"

        if extension in {".yaml", ".yml"}:
            return FileType.CONFIGURATION, "yaml"

        if extension == ".json":
            return FileType.CONFIGURATION, "json"
        
        if extension == ".sh":
            return FileType.SOURCE_CODE, "shell"

        return FileType.UNKNOWN, None

    @staticmethod
    def _dependency_language(file_name: str) -> str | None:
        """Return the format associated with a dependency file."""

        if file_name == "pyproject.toml":
            return "toml"

        if file_name in {"package.json", "package-lock.json"}:
            return "json"

        if file_name == "pom.xml":
            return "xml"

        if file_name == "build.gradle":
            return "gradle"

        if file_name == "go.mod":
            return "go"

        if file_name.endswith(".txt"):
            return "text"

        if file_name.endswith(".lock"):
            return "lock"

        return None

    @staticmethod
    def _infrastructure_language(file_name: str) -> str:
        """Return the format associated with an infrastructure file."""

        if file_name == "dockerfile":
            return "dockerfile"

        return "yaml"