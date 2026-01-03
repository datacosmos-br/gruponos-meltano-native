"""External command execution utility for GrupoNOS Meltano Native.

Provides subprocess execution with FlextResult error handling, following the
FLEXT railway-oriented programming pattern. This module wraps subprocess
operations to provide type-safe, result-oriented external command execution.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import subprocess  # noqa: S404 - Required for external command execution
from dataclasses import dataclass

from flext_core import FlextResult


@dataclass(frozen=True)
class ExternalCommandResult:
    """Result wrapper for external command execution.

    Provides typed access to stdout, stderr, and returncode from subprocess
    execution in an immutable container.
    """

    stdout: str
    stderr: str
    returncode: int


def run_external_command(
    cmd: list[str],
    env: dict[str, str] | None = None,
    timeout: float = 30.0,
    cwd: str | None = None,
) -> FlextResult[ExternalCommandResult]:
    """Execute external command and return result with FlextResult pattern.

    Args:
        cmd: Command and arguments as a list of strings
        env: Environment variables for the subprocess
        timeout: Maximum execution time in seconds
        cwd: Working directory for command execution

    Returns:
        FlextResult containing ExternalCommandResult on success, or error message on failure

    Example:
        result = run_external_command(["meltano", "run", "job-name"], timeout=3600.0)
        if result.is_success:
            wrapper = result.value
            print(f"Output: {wrapper.stdout}")
            print(f"Return code: {wrapper.returncode}")

    """
    try:
        process = subprocess.run(  # noqa: S603 - Command execution is intentional
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            check=False,
        )

        wrapper = ExternalCommandResult(
            stdout=process.stdout,
            stderr=process.stderr,
            returncode=process.returncode,
        )

        return FlextResult[ExternalCommandResult].ok(wrapper)

    except subprocess.TimeoutExpired as e:
        return FlextResult[ExternalCommandResult].fail(
            f"Command timed out after {timeout} seconds: {e!s}"
        )
    except FileNotFoundError as e:
        return FlextResult[ExternalCommandResult].fail(f"Command not found: {e!s}")
    except OSError as e:
        return FlextResult[ExternalCommandResult].fail(
            f"OS error executing command: {e!s}"
        )
    except Exception as e:
        return FlextResult[ExternalCommandResult].fail(
            f"Unexpected error executing command: {e!s}"
        )


__all__ = ["ExternalCommandResult", "run_external_command"]
