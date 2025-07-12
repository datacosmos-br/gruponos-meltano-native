#!/usr/bin/env python3
"""Test Meltano sync functionality."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, env=None):
    """Run a command and return output."""
    print(f"\n🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env or os.environ.copy()
    )
    
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        print(f"STDERR:\n{result.stderr}")
        return False
    
    print(f"✅ Command succeeded")
    if result.stdout:
        print(f"Output:\n{result.stdout[:500]}...")
    return True

def test_environment():
    """Test if environment is correctly configured."""
    print("\n" + "="*60)
    print("🧪 TESTING ENVIRONMENT CONFIGURATION")
    print("="*60)
    
    required_vars = [
        "TAP_ORACLE_WMS_BASE_URL",
        "TAP_ORACLE_WMS_USERNAME", 
        "TAP_ORACLE_WMS_PASSWORD",
        "FLEXT_TARGET_ORACLE_HOST",
        "FLEXT_TARGET_ORACLE_USERNAME",
        "FLEXT_TARGET_ORACLE_PASSWORD",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME"
    ]
    
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("Please configure your .env file")
        return False
    
    return True

def test_tap_installation():
    """Test if tap is properly installed."""
    print("\n" + "="*60)
    print("🧪 TESTING TAP INSTALLATION")
    print("="*60)
    
    # Check if tap is available
    result = subprocess.run(
        ["which", "tap-oracle-wms"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ tap-oracle-wms not found in PATH")
        return False
    
    print(f"✅ tap-oracle-wms found at: {result.stdout.strip()}")
    return True

def test_target_installation():
    """Test if target is properly installed."""
    print("\n" + "="*60)
    print("🧪 TESTING TARGET INSTALLATION")
    print("="*60)
    
    # Check if target is available
    result = subprocess.run(
        ["which", "flext-target-oracle"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ flext-target-oracle not found in PATH")
        return False
    
    print(f"✅ flext-target-oracle found at: {result.stdout.strip()}")
    return True

def test_meltano_config():
    """Test if Meltano can read config."""
    print("\n" + "="*60)
    print("🧪 TESTING MELTANO CONFIGURATION")
    print("="*60)
    
    # Test meltano config
    return run_command(["meltano", "config", "tap-oracle-wms-full", "list"])

def test_simple_sync():
    """Test a simple sync to JSONL."""
    print("\n" + "="*60)
    print("🧪 TESTING SIMPLE SYNC TO JSONL")
    print("="*60)
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Run sync to JSONL
    env = os.environ.copy()
    env["TARGET_JSONL_DESTINATION_PATH"] = str(output_dir / "test_output.jsonl")
    
    return run_command(
        ["meltano", "run", "tap-oracle-wms-full", "target-jsonl"],
        env=env
    )

def main():
    """Run all tests."""
    print("🚀 GRUPONOS MELTANO NATIVE - TEST SUITE")
    print("="*60)
    
    # Load .env file if exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  No .env file found, using system environment")
    
    # Run tests
    tests = [
        ("Environment Configuration", test_environment),
        ("Tap Installation", test_tap_installation),
        ("Target Installation", test_target_installation),
        ("Meltano Configuration", test_meltano_config),
        ("Simple Sync", test_simple_sync)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n⚠️  Some tests failed. Please fix the issues and try again.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Your setup is ready.")
        sys.exit(0)

if __name__ == "__main__":
    main()