from pathlib import Path

from github_rag.core.exceptions import RepositoryAccessError
from github_rag.domain.models import RepositoryInventory


class InventoryWriter:
    """Writes repository inventory results to output files."""

    def write_json(
        self,
        inventory: RepositoryInventory,
        output_path: Path,
    ) -> Path:
        
        """Write a repository inventory to a formatted JSON file."""

        resolved_path = output_path.expanduser().resolve()

        try:
            resolved_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            resolved_path.write_text(
                inventory.model_dump_json(
                    indent=2,
                    exclude_none=True,
                ),
                encoding="utf-8",
            )
        except OSError as error:
            raise RepositoryAccessError(
                f"Unable to write inventory file "
                f"{resolved_path}: {error}"
            ) from error

        return resolved_path