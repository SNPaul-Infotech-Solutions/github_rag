from collections.abc import Iterable

from github_rag.core.exceptions import ExtractionError
from github_rag.domain.models import (
    ExtractedDocument,
    RepositoryFile,
)
from github_rag.extraction.base import DocumentParser


class ParserRegistry:
    """Selects an appropriate parser for a repository file."""

    def __init__(
        self,
        parsers: Iterable[DocumentParser],
    ) -> None:
        self._parsers = tuple(parsers)

        if not self._parsers:
            raise ValueError(
                "ParserRegistry requires at least one parser"
            )

    def get_parser(
        self,
        repository_file: RepositoryFile,
    ) -> DocumentParser:
        """Return the first parser that supports the repository file."""

        for parser in self._parsers:
            if parser.can_parse(repository_file):
                return parser

        raise ExtractionError(
            "No compatible parser found for file: "
            f"{repository_file.relative_path}"
        )

    def parse(
        self,
        repository_file: RepositoryFile,
    ) -> ExtractedDocument:
        """Select a compatible parser and extract the document."""

        parser = self.get_parser(repository_file)

        return parser.parse(repository_file)