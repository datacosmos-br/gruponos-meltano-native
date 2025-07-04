#!/usr/bin/env python3
"""Test script to verify configuration migration from hardcoded to environment-based.

This script validates that:
1. Environment variables are properly loaded
2. Configuration values are accessible in meltano
3. The new configurable system works correctly
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_environment_variables():
    """Test that environment variables are set and accessible."""
    print("🔍 Testing Environment Variables...")
    
    # Required variables that must be set
    required_vars = [
        'TAP_ORACLE_WMS_BASE_URL',
        'TAP_ORACLE_WMS_USERNAME', 
        'TAP_ORACLE_WMS_PASSWORD',
        'FLEXT_TARGET_ORACLE_HOST',
        'FLEXT_TARGET_ORACLE_SERVICE_NAME',
        'FLEXT_TARGET_ORACLE_USERNAME',
        'FLEXT_TARGET_ORACLE_PASSWORD'
    ]
    
    # Optional configurable variables (should have defaults)
    configurable_vars = [
        'WMS_API_VERSION',
        'WMS_PAGE_SIZE',
        'WMS_REQUEST_TIMEOUT',
        'WMS_MAX_RETRIES',
        'WMS_OAUTH_SCOPE',
        'WMS_CATALOG_CACHE_TTL'
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        print("💡 Please set these in your .env file or environment")
        return False
    
    print("✅ All required environment variables are set")
    
    # Check configurable variables (they should have defaults)
    print("\n📊 Configurable Variables Status:")
    for var in configurable_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "🔧 Using default"
        print(f"  {var}: {status}")
        if value:
            print(f"    Value: {value}")
    
    return True

def test_meltano_config():
    """Test that meltano can read and parse the configuration."""
    print("\n🔍 Testing Meltano Configuration...")
    
    try:
        # Test tap configuration
        result = subprocess.run([
            'meltano', 'config', 'tap-oracle-wms-full', 'list'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print(f"❌ Meltano config list failed: {result.stderr}")
            return False
        
        print("✅ Meltano can read tap configuration")
        
        # Test target configuration  
        result = subprocess.run([
            'meltano', 'config', 'target-oracle-full', 'list'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print(f"❌ Meltano target config list failed: {result.stderr}")
            return False
            
        print("✅ Meltano can read target configuration")
        
        return True
        
    except FileNotFoundError:
        print("❌ Meltano not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error testing meltano config: {e}")
        return False

def test_configuration_values():
    """Test that specific configuration values are properly resolved."""
    print("\n🔍 Testing Configuration Value Resolution...")
    
    try:
        # Get resolved configuration for tap
        result = subprocess.run([
            'meltano', 'config', 'tap-oracle-wms-full', 'list', '--format=json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            print(f"❌ Failed to get tap config: {result.stderr}")
            return False
        
        config = json.loads(result.stdout)
        
        # Check key configuration values
        checks = [
            ('base_url', 'TAP_ORACLE_WMS_BASE_URL'),
            ('username', 'TAP_ORACLE_WMS_USERNAME'),
            ('wms_api_version', 'WMS_API_VERSION'),
            ('page_size', 'WMS_PAGE_SIZE'),
            ('request_timeout', 'WMS_REQUEST_TIMEOUT'),
        ]
        
        print("📊 Configuration Value Checks:")
        for config_key, env_var in checks:
            config_value = config.get(config_key)
            env_value = os.getenv(env_var)
            
            if config_value is not None:
                print(f"  ✅ {config_key}: {config_value}")
                # Verify it matches environment variable (if set)
                if env_value and str(config_value) != env_value:
                    print(f"    ⚠️  Config value doesn't match env var {env_var}={env_value}")
            else:
                print(f"  ❓ {config_key}: Not set (using default)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse meltano config JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking configuration values: {e}")
        return False

def test_tap_help():
    """Test that the tap can be invoked and shows help."""
    print("\n🔍 Testing Tap Invocation...")
    
    try:
        result = subprocess.run([
            'meltano', 'invoke', 'tap-oracle-wms-full', '--help'
        ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Tap invocation failed: {result.stderr}")
            return False
        
        if 'Oracle WMS' in result.stdout or 'Singer' in result.stdout:
            print("✅ Tap can be invoked and shows help")
            return True
        else:
            print("❌ Tap help output doesn't look correct")
            print(f"Output: {result.stdout[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Tap invocation timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing tap invocation: {e}")
        return False

def check_configuration_file():
    """Check that configuration files exist and are readable."""
    print("\n🔍 Checking Configuration Files...")
    
    files_to_check = [
        ('.env.example', 'Environment template'),
        ('meltano.yml', 'Meltano configuration'),
        ('CONFIGURATION_MIGRATION_GUIDE.md', 'Migration guide')
    ]
    
    base_dir = Path(__file__).parent
    all_good = True
    
    for filename, description in files_to_check:
        file_path = base_dir / filename
        if file_path.exists():
            print(f"  ✅ {description}: {filename}")
        else:
            print(f"  ❌ Missing {description}: {filename}")
            all_good = False
    
    return all_good

def main():
    """Run all configuration migration tests."""
    print("🚀 Configuration Migration Test Suite")
    print("=" * 50)
    
    # Set working directory to script location
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Configuration Files", check_configuration_file),
        ("Environment Variables", test_environment_variables),
        ("Meltano Configuration", test_meltano_config),
        ("Configuration Values", test_configuration_values),
        ("Tap Invocation", test_tap_help),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*20} SUMMARY {'='*20}")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Configuration migration successful.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the issues above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure .env file is created from .env.example")
        print("   2. Set all required environment variables")
        print("   3. Run 'meltano install' to ensure plugins are installed")
        print("   4. Check that flext-tap-oracle-wms is accessible in PATH")
        return 1

if __name__ == '__main__':
    sys.exit(main())