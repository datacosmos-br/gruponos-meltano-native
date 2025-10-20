"""Show Config Handler - GrupoNOS Meltano Native CLI.

Handler for show config command operations.
"""

from __future__ import annotations

import yaml

from gruponos_meltano_native.config import GruponosMeltanoNativeConfig


class ShowConfigHandler:
    """Handler for show config command."""

    def __init__(self, config: GruponosMeltanoNativeConfig) -> None:
        """Initialize the show config handler."""
        self._config = config

    def execute(self, output_format: str = "yaml") -> FlextResult[dict[str, str]]:
        """Execute show config command."""
        if output_format == "yaml":
            config_content = yaml.dump(
                self._config.model_dump(), default_flow_style=False
            )
        else:
            config_content = str(self._config.model_dump())

        return FlextResult[dict[str, str]].ok({
            "config": "loaded",
            "format": output_format,
            "content": config_content,
        })
