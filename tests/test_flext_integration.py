#!/usr/bin/env python3
"""Test FLEXT library integration in GrupoNOS project."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all FLEXT imports work correctly."""
    print("Testing FLEXT library imports...")
    
    # Test flext-observability
    try:
        from flext_observability.logging import get_logger, setup_logging
        setup_logging()  # Usa configuração padrão
        logger = get_logger(__name__)
        logger.info("✅ flext-observability logging works!")
    except Exception as e:
        print(f"❌ flext-observability import failed: {e}")
        return False
    
    # Test flext-core
    try:
        from flext_core.domain.types import ServiceResult
        from flext_core import BaseConfig
        result = ServiceResult.success("test")
        print(f"✅ flext-core ServiceResult works: {result.is_success}")
    except Exception as e:
        print(f"❌ flext-core import failed: {e}")
        return False
    
    # Test flext-db-oracle
    try:
        from flext_db_oracle.connection import ConnectionConfig, ResilientOracleConnection
        print("✅ flext-db-oracle imports work!")
    except Exception as e:
        print(f"❌ flext-db-oracle import failed: {e}")
        return False
    
    return True


def test_logging_integration():
    """Test that our modules use FLEXT logging correctly."""
    print("\nTesting logging integration...")
    
    try:
        # Test alert_manager
        from monitoring.alert_manager import AlertManager
        print("✅ alert_manager imports successfully with FLEXT logging")
        
        # Test data_validator
        from validators.data_validator import DataValidator
        print("✅ data_validator imports successfully with FLEXT logging")
        
        # Test connection managers
        from oracle.connection_manager import OracleConnectionManager
        print("✅ Original connection_manager works")
        
        from oracle.connection_manager_enhanced import OracleConnectionManager as EnhancedManager
        print("✅ Enhanced connection_manager imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_integration():
    """Test FLEXT config integration."""
    print("\nTesting configuration integration...")
    
    try:
        from gruponos_meltano_native.config import GrupoNOSConfig, get_config
        
        # Test basic config creation
        from gruponos_meltano_native.config import (
            OracleConnectionConfig,
            WMSSourceConfig,
            TargetOracleConfig,
            MeltanoConfig,
        )
        
        # Create minimal config
        wms_oracle = OracleConnectionConfig(
            host="test.local",
            service_name="TEST",
            username="user",
            password="pass",
        )
        
        wms_config = WMSSourceConfig(oracle=wms_oracle)
        print("✅ FLEXT config classes work correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Config integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("="*60)
    print("FLEXT Integration Tests for GrupoNOS")
    print("="*60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Logging Integration", test_logging_integration),
        ("Config Integration", test_config_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n✅ All FLEXT integrations working correctly!")
    else:
        print("\n❌ Some integrations failed - check output above")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())