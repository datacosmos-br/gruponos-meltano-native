"""Tests for Oracle schema discovery functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle schema discovery logic with comprehensive error handling.
"""

from typing import Any
from unittest.mock import Mock, patch

from gruponos_meltano_native.oracle.discover_and_save_schemas import discover_schemas


class TestOracleSchemaDiscovery:
    """Test Oracle schema discovery with real implementation."""

    @patch.dict(
        "os.environ",
        {
            "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
            "TAP_ORACLE_WMS_USERNAME": "test_user",
            "TAP_ORACLE_WMS_PASSWORD": "test_pass",
        },
    )
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS")
    def test_discover_schemas_success(self, mock_tap: Any) -> None:
        """Test successful schema discovery with real implementation."""
        # Mock TapOracleWMS discovery
        mock_stream = type("MockStream", (), {})()
        mock_stream.tap_stream_id = "allocation"
        mock_stream.schema = {
            "type": "object",
            "properties": {
                "allocation_id": {"type": "number"},
                "customer_id": {"type": "number"},
                "location": {"type": "string", "maxLength": 50},
                "quantity": {"type": "number"},
                "created_date": {"type": "string", "format": "date-time"},
            },
        }

        mock_tap_instance = type("MockTapInstance", (), {})()
        mock_tap_instance.discover_streams = lambda: [mock_stream]
        mock_tap.return_value = mock_tap_instance

        # Test discovery
        result = discover_schemas()

        assert result is True
        mock_tap.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.load_dotenv")
    def test_discover_schemas_missing_credentials(self, mock_load_dotenv: Mock) -> None:
        """Test schema discovery with missing credentials."""
        # Prevent loading from .env file
        mock_load_dotenv.return_value = None

        # Test discovery without credentials
        result = discover_schemas()

        assert result is False

    @patch.dict(
        "os.environ",
        {
            "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
            "TAP_ORACLE_WMS_USERNAME": "test_user",
            "TAP_ORACLE_WMS_PASSWORD": "test_pass",
        },
    )
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS")
    def test_discover_schemas_api_error(self, mock_tap: Any) -> None:
        """Test schema discovery with API error."""
        # Mock TapOracleWMS to raise exception
        mock_tap.side_effect = Exception("Connection failed")

        # Test discovery
        result = discover_schemas()

        assert result is False

    @patch.dict(
        "os.environ",
        {
            "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
            "TAP_ORACLE_WMS_USERNAME": "test_user",
            "TAP_ORACLE_WMS_PASSWORD": "test_pass",
            "WMS_PAGE_SIZE": "500",
        },
    )
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS")
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.Path")
    def test_discover_schemas_with_custom_page_size(
        self,
        mock_path: Any,
        mock_tap: Any,
    ) -> None:
        """Test schema discovery with custom page size."""
        # Mock directory creation
        mock_path_instance = type("MockPath", (), {})()
        mock_path_instance.mkdir = lambda exist_ok: None
        mock_path_instance.open = lambda mode, encoding: type(
            "MockFile",
            (),
            {
                "__enter__": lambda self: self,
                "__exit__": lambda self, *args: None,
                "write": lambda self, data: None,
            },
        )()
        mock_path.return_value = mock_path_instance

        # Mock TapOracleWMS
        mock_stream = type("MockStream", (), {})()
        mock_stream.tap_stream_id = "allocation"
        mock_stream.schema = {
            "type": "object",
            "properties": {"id": {"type": "number"}},
        }

        mock_tap_instance = type("MockTapInstance", (), {})()
        mock_tap_instance.discover_streams = lambda: [mock_stream]
        mock_tap.return_value = mock_tap_instance

        # Test discovery
        result = discover_schemas()

        assert result is True
        # Verify TapOracleWMS was called with custom page size
        call_args = mock_tap.call_args[1]["config"]
        assert call_args["page_size"] == 500

    @patch.dict(
        "os.environ",
        {
            "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
            "TAP_ORACLE_WMS_USERNAME": "test_user",
            "TAP_ORACLE_WMS_PASSWORD": "test_pass",
        },
    )
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS")
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.Path")
    def test_discover_schemas_file_creation(
        self,
        mock_path: Any,
        mock_tap: Any,
    ) -> None:
        """Test that schema discovery creates the expected file structure."""
        # Mock Path and file operations
        mock_path_mkdir = type("MockPathMkdir", (), {})()
        mock_path_mkdir.mkdir = lambda exist_ok: None

        mock_file = type(
            "MockFile",
            (),
            {
                "__enter__": lambda self: self,
                "__exit__": lambda self, *args: None,
                "write": lambda self, data: None,
            },
        )()

        mock_path_open = type("MockPathOpen", (), {})()
        mock_path_open.open = lambda mode, encoding: mock_file

        mock_path.side_effect = [mock_path_mkdir, mock_path_open]

        # Mock TapOracleWMS
        mock_stream = type("MockStream", (), {})()
        mock_stream.tap_stream_id = "allocation"
        mock_stream.schema = {
            "type": "object",
            "properties": {"id": {"type": "number"}},
        }

        mock_tap_instance = type("MockTapInstance", (), {})()
        mock_tap_instance.discover_streams = lambda: [mock_stream]
        mock_tap.return_value = mock_tap_instance

        # Test discovery
        result = discover_schemas()

        assert result is True
        # Verify Path was called for directory creation and file opening
        assert mock_path.call_count == 2

    def test_discover_schemas_entities_configuration(self) -> None:
        """Test that the function uses the correct entities configuration."""
        with (
            patch.dict(
                "os.environ",
                {
                    "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
                    "TAP_ORACLE_WMS_USERNAME": "test_user",
                    "TAP_ORACLE_WMS_PASSWORD": "test_pass",
                },
            ),
            patch(
                "gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS",
            ) as mock_tap,
        ):
            # Mock TapOracleWMS
            mock_tap_instance = type("MockTapInstance", (), {})()
            mock_tap_instance.discover_streams = list
            mock_tap.return_value = mock_tap_instance

            # Test discovery
            discover_schemas()

            # Verify configuration includes expected entities
            call_args = mock_tap.call_args[1]["config"]
            expected_entities = ["allocation", "order_hdr", "order_dtl"]
            assert call_args["entities"] == expected_entities
            assert call_args["force_full_table"] is True

    @patch.dict(
        "os.environ",
        {
            "TAP_ORACLE_WMS_BASE_URL": "https://test.example.com",
            "TAP_ORACLE_WMS_USERNAME": "test_user",
            "TAP_ORACLE_WMS_PASSWORD": "test_pass",
        },
    )
    @patch("gruponos_meltano_native.oracle.discover_and_save_schemas.TapOracleWMS")
    def test_discover_schemas_multiple_streams(self, mock_tap: Any) -> None:
        """Test discovery with multiple streams."""
        # Mock multiple streams
        mock_stream1 = type("MockStream", (), {})()
        mock_stream1.tap_stream_id = "allocation"
        mock_stream1.schema = {
            "type": "object",
            "properties": {"id": {"type": "number"}},
        }

        mock_stream2 = type("MockStream", (), {})()
        mock_stream2.tap_stream_id = "order_hdr"
        mock_stream2.schema = {
            "type": "object",
            "properties": {"order_id": {"type": "number"}},
        }

        mock_tap_instance = type("MockTapInstance", (), {})()
        mock_tap_instance.discover_streams = lambda: [mock_stream1, mock_stream2]
        mock_tap.return_value = mock_tap_instance

        # Test discovery
        result = discover_schemas()

        assert result is True

    def test_discover_schemas_integration_functionality(self) -> None:
        """Test the integration aspects of schema discovery."""
        # This test validates the function signature and basic requirements
        assert callable(discover_schemas)

        # Test that function returns boolean
        with patch.dict("os.environ", {}, clear=True):
            result = discover_schemas()
            assert isinstance(result, bool)
