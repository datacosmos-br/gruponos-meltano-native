"""Tests for pipeline_executor.py subprocess removal conversions.

This module validates that all subprocess calls in pipeline_executor.py
have been successfully converted to use FlextUtilities.run_external_command()
with proper error handling using FlextResult[T] railway pattern.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


class TestPipelineExecutorNoSubprocessImports:
    """Verify subprocess has been completely removed from imports."""

    def test_no_subprocess_import(self) -> None:
        """Verify subprocess module is not imported."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Check all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "subprocess", (
                        f"subprocess module imported at line {node.lineno}"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "subprocess", (
                    f"subprocess module imported from at line {node.lineno}"
                )

    def test_no_subprocess_method_calls(self) -> None:
        """Verify no subprocess.run or subprocess.Popen calls exist."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Simple pattern matching (not AST based to catch all variations)
        assert "subprocess.run" not in source, "subprocess.run() still present in file"
        assert "subprocess.Popen" not in source, (
            "subprocess.Popen() still present in file"
        )
        assert "subprocess.TimeoutExpired" not in source, (
            "subprocess.TimeoutExpired exception handler still present in file"
        )

    def test_flextutilities_import_exists(self) -> None:
        """Verify FlextUtilities is imported."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        assert "FlextUtilities" in source, "FlextUtilities not imported"
        assert "from flext_core import" in source, "FLEXT core not imported"

    def test_flextlogger_import_exists(self) -> None:
        """Verify FlextLogger is imported."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        assert "FlextLogger" in source, "FlextLogger not imported"


class TestPipelineExecutorRunExternalCommandUsage:
    """Verify FlextUtilities.run_external_command() is used in all methods."""

    def test_get_job_status_uses_run_external_command(self) -> None:
        """Verify get_job_status() uses FlextUtilities.run_external_command()."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Extract get_job_status method
        tree = ast.parse(source)
        get_job_status_found = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_job_status":
                method_code = ast.unparse(node)
                assert "FlextUtilities.run_external_command" in method_code, (
                    "get_job_status() does not use FlextUtilities.run_external_command()"
                )
                assert "timed out" in method_code.lower(), (
                    "get_job_status() does not check for timeout in error message"
                )
                get_job_status_found = True
                break

        assert get_job_status_found, "get_job_status() method not found"

    def test_list_jobs_uses_run_external_command(self) -> None:
        """Verify list_jobs() uses FlextUtilities.run_external_command()."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        list_jobs_found = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "list_jobs":
                method_code = ast.unparse(node)
                assert "FlextUtilities.run_external_command" in method_code, (
                    "list_jobs() does not use FlextUtilities.run_external_command()"
                )
                assert "timed out" in method_code.lower(), (
                    "list_jobs() does not check for timeout in error message"
                )
                list_jobs_found = True
                break

        assert list_jobs_found, "list_jobs() method not found"

    def test_list_pipelines_uses_run_external_command(self) -> None:
        """Verify list_pipelines() uses FlextUtilities.run_external_command()."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        list_pipelines_found = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "list_pipelines":
                method_code = ast.unparse(node)
                assert "FlextUtilities.run_external_command" in method_code, (
                    "list_pipelines() does not use FlextUtilities.run_external_command()"
                )
                assert "timed out" in method_code.lower(), (
                    "list_pipelines() does not check for timeout in error message"
                )
                list_pipelines_found = True
                break

        assert list_pipelines_found, "list_pipelines() method not found"

    def test_execute_meltano_pipeline_uses_run_external_command(self) -> None:
        """Verify _execute_meltano_pipeline() uses FlextUtilities.run_external_command()."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        execute_pipeline_found = False

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "_execute_meltano_pipeline"
            ):
                method_code = ast.unparse(node)
                assert "FlextUtilities.run_external_command" in method_code, (
                    "_execute_meltano_pipeline() does not use FlextUtilities.run_external_command()"
                )
                assert "timed out" in method_code.lower(), (
                    "_execute_meltano_pipeline() does not check for timeout in error message"
                )
                assert "3600" in method_code, (
                    "_execute_meltano_pipeline() does not use 1-hour timeout (3600 seconds)"
                )
                execute_pipeline_found = True
                break

        assert execute_pipeline_found, "_execute_meltano_pipeline() method not found"


class TestPipelineExecutorErrorHandling:
    """Verify error handling patterns follow FlextResult[T] railway pattern."""

    def test_all_methods_return_flextresult(self) -> None:
        """Verify all public methods return FlextResult[T]."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        methods_to_check = [
            "get_job_status",
            "list_jobs",
            "list_pipelines",
        ]

        for method_name in methods_to_check:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    # Check return annotation
                    if node.returns:
                        annotation = ast.unparse(node.returns)
                        assert "FlextResult" in annotation, (
                            f"{method_name}() does not return FlextResult[T]"
                        )

    def test_error_message_detection_instead_of_exceptions(self) -> None:
        """Verify error detection uses message checking instead of exception handlers."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Should have error message checking
        assert 'timed out" in' in source.lower(), (
            "No timeout detection via error message"
        )
        assert "exec_result.is_failure" in source, "No failure checking on FlextResult"
        assert "exec_result.error" in source, "No error message access from FlextResult"

    def test_json_decode_error_handling(self) -> None:
        """Verify JSONDecodeError is still caught for JSON parsing."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # JSON parsing methods should still have JSONDecodeError handlers
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in {
                "get_job_status",
                "list_jobs",
                "list_pipelines",
            }:
                # These methods parse JSON
                assert "json.loads" in ast.unparse(node), (
                    f"{node.name}() should parse JSON"
                )

                # Check for JSONDecodeError handling
                code = ast.unparse(node)
                assert "JSONDecodeError" in code, (
                    f"{node.name}() should handle JSONDecodeError"
                )


class TestPipelineExecutorModuleStructure:
    """Verify overall module structure is correct."""

    def test_module_can_be_imported(self) -> None:
        """Verify pipeline_executor module can be imported without subprocess errors."""
        try:
            # Try importing the module
            from gruponos_meltano_native.core.pipeline_executor import (
                MeltanoPipelineExecutor,
            )

            assert MeltanoPipelineExecutor is not None
        except ImportError as e:
            if "subprocess" in str(e):
                pytest.fail(f"Module import failed due to subprocess issue: {e}")
            raise

    def test_executor_class_has_required_methods(self) -> None:
        """Verify MeltanoPipelineExecutor has all required methods."""
        from gruponos_meltano_native.core.pipeline_executor import (
            MeltanoPipelineExecutor,
        )

        required_methods = [
            "execute_pipeline",
            "get_job_status",
            "list_jobs",
            "list_pipelines",
            "_execute_meltano_pipeline",
            "_validate_job_name",
            "_build_meltano_environment",
        ]

        for method_name in required_methods:
            assert hasattr(MeltanoPipelineExecutor, method_name), (
                f"MeltanoPipelineExecutor missing method: {method_name}"
            )

    def test_flextlogger_initialized_correctly(self) -> None:
        """Verify FlextLogger is initialized in __init__."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_code = ast.unparse(node)
                assert "self.logger" in init_code, (
                    "__init__ does not initialize self.logger"
                )
                assert "FlextLogger.get_logger" in init_code, (
                    "__init__ does not use FlextLogger.get_logger()"
                )


class TestSprintTwoPatternConsistency:
    """Verify conversions follow Sprint 2 proven patterns."""

    def test_uses_timeout_parameter_correctly(self) -> None:
        """Verify timeout is passed as float to run_external_command()."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Check for proper timeout parameter format
        assert "timeout=30.0" in source, "Timeouts not specified as float (e.g., 30.0)"
        assert "timeout=3600.0" in source, (
            "1-hour timeout not specified as float (3600.0)"
        )

    def test_error_result_unwrapping(self) -> None:
        """Verify FlextResult unwrapping pattern is used."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Should use .value pattern to get wrapper
        assert "wrapper = exec_result.value" in source, (
            "Does not use .value pattern to extract wrapper from FlextResult"
        )

    def test_wrapper_attribute_access(self) -> None:
        """Verify wrapper attributes are accessed correctly."""
        executor_path = (
            Path(__file__).parent.parent.parent
            / "src/gruponos_meltano_native/core/pipeline_executor.py"
        )

        with Path(executor_path).open(encoding="utf-8") as f:
            source = f.read()

        # Should access wrapper attributes
        assert "wrapper.stdout" in source, "Does not access wrapper.stdout"
        assert "wrapper.stderr" in source, "Does not access wrapper.stderr"
        assert "wrapper.returncode" in source, "Does not access wrapper.returncode"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
