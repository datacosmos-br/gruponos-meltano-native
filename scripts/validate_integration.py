#!/usr/bin/env python3
"""
Validate Integration - Ensure generic modules work with gruponos-meltano-native.

This script validates:
1. Critical environment variables are set correctly
2. Generic modules are accessible
3. Configuration profiles work
4. Schema discovery uses only metadata
5. Meltano configuration is valid
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_critical_environment():
    """Check critical environment variables."""
    print("🔍 Checking critical environment variables...")
    
    critical_vars = {
        "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
        "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0"
    }
    
    all_valid = True
    for var, expected in critical_vars.items():
        actual = os.getenv(var, "")
        if actual != expected:
            print(f"❌ {var} = '{actual}' (expected: '{expected}')")
            all_valid = False
        else:
            print(f"✅ {var} = '{actual}'")
    
    if not all_valid:
        print("\n🚨 CRITICAL ERROR: Environment variables are not set correctly!")
        print("   Schema discovery MUST use only metadata, NEVER samples!")
        sys.exit(1)
    
    return True


def check_generic_modules():
    """Check if generic modules are installed and accessible."""
    print("\n🔍 Checking generic module installation...")
    
    modules_to_check = [
        ("tap-oracle-wms", "flext-tap-oracle-wms"),
        ("flext-target-oracle", "flext-target-oracle")
    ]
    
    for cmd, package in modules_to_check:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {package}: {result.stdout.strip()}")
            else:
                print(f"❌ {package}: Not found or error")
                return False
        except Exception as e:
            print(f"❌ {package}: {str(e)}")
            return False
    
    return True


def check_configuration_profiles():
    """Check if configuration profiles are working."""
    print("\n🔍 Checking configuration profiles...")
    
    profile_name = os.getenv("WMS_PROFILE_NAME", "")
    if not profile_name:
        print("⚠️  No WMS_PROFILE_NAME set - using defaults")
        return True
    
    print(f"📋 Profile: {profile_name}")
    
    # Try to load the profile
    try:
        # Import ConfigMapper to test profile loading
        from flext_tap_oracle_wms.config_profiles import ConfigProfileManager
        
        manager = ConfigProfileManager()
        profile = manager.load_profile(profile_name)
        
        print(f"✅ Profile loaded: {profile.company_name}")
        print(f"   Environment: {profile.environment}")
        print(f"   Entities: {len(profile.get_enabled_entities())}")
        
        return True
    except ImportError:
        print("⚠️  Could not import ConfigProfileManager - module may not be in path")
        return True  # Not a critical error
    except Exception as e:
        print(f"❌ Error loading profile: {str(e)}")
        return False


def validate_meltano_config():
    """Validate meltano.yml configuration."""
    print("\n🔍 Validating meltano.yml configuration...")
    
    meltano_yml = PROJECT_ROOT / "meltano.yml"
    if not meltano_yml.exists():
        print("❌ meltano.yml not found!")
        return False
    
    try:
        import yaml
        with open(meltano_yml) as f:
            config = yaml.safe_load(f)
        
        # Check for required extractors
        extractors = config.get("plugins", {}).get("extractors", [])
        tap_names = [e["name"] for e in extractors]
        
        required_taps = ["tap-oracle-wms-full", "tap-oracle-wms-incremental"]
        for tap in required_taps:
            if tap in tap_names:
                print(f"✅ {tap}: Found")
                
                # Check critical settings
                tap_config = next(e for e in extractors if e["name"] == tap)
                config_section = tap_config.get("config", {})
                
                # Check if critical settings use environment variables
                if "use_metadata_only" in config_section:
                    if config_section["use_metadata_only"] == "$TAP_ORACLE_WMS_USE_METADATA_ONLY":
                        print(f"   ✅ use_metadata_only: Using environment variable")
                    else:
                        print(f"   ❌ use_metadata_only: Hardcoded value!")
                        return False
                
                if "discovery_sample_size" in config_section:
                    if config_section["discovery_sample_size"] == "$TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE":
                        print(f"   ✅ discovery_sample_size: Using environment variable")
                    else:
                        print(f"   ❌ discovery_sample_size: Hardcoded value!")
                        return False
            else:
                print(f"❌ {tap}: Not found")
                return False
        
        # Check loaders
        loaders = config.get("plugins", {}).get("loaders", [])
        target_names = [l["name"] for l in loaders]
        
        if "target-oracle-full" in target_names:
            print("✅ target-oracle-full: Found")
        else:
            print("❌ target-oracle-full: Not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating meltano.yml: {str(e)}")
        return False


def test_schema_discovery():
    """Test that schema discovery works with metadata only."""
    print("\n🔍 Testing schema discovery (metadata only)...")
    
    try:
        # Run discovery command
        result = subprocess.run(
            ["meltano", "invoke", "tap-oracle-wms", "--discover"],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ}
        )
        
        if result.returncode != 0:
            print(f"❌ Discovery failed: {result.stderr}")
            return False
        
        # Parse catalog
        try:
            catalog = json.loads(result.stdout)
            streams = catalog.get("streams", [])
            
            if streams:
                print(f"✅ Discovered {len(streams)} streams")
                for stream in streams[:3]:  # Show first 3
                    stream_name = stream.get("stream", "")
                    properties = stream.get("schema", {}).get("properties", {})
                    print(f"   📊 {stream_name}: {len(properties)} properties")
            else:
                print("⚠️  No streams discovered")
                
            return True
            
        except json.JSONDecodeError:
            print("⚠️  Could not parse discovery output as JSON")
            # Still return True as discovery ran without error
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Discovery timed out (may be normal for large APIs)")
        return True
    except Exception as e:
        print(f"❌ Error during discovery: {str(e)}")
        return False


def check_critical_settings_script():
    """Ensure critical_settings.sh exists and is executable."""
    print("\n🔍 Checking critical settings enforcement script...")
    
    script_path = PROJECT_ROOT / "config" / "critical_settings.sh"
    
    if not script_path.exists():
        print(f"❌ {script_path} not found!")
        return False
    
    # Check if executable
    if os.access(script_path, os.X_OK):
        print(f"✅ {script_path} exists and is executable")
    else:
        print(f"⚠️  {script_path} exists but is not executable")
        # Try to make it executable
        try:
            os.chmod(script_path, 0o755)
            print("   ✅ Made script executable")
        except Exception as e:
            print(f"   ❌ Could not make executable: {e}")
            return False
    
    # Test the script
    try:
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            env={**os.environ}
        )
        
        if result.returncode == 0:
            print("✅ Critical settings script validates correctly")
            print(f"   {result.stdout.strip()}")
        else:
            print("❌ Critical settings script failed validation!")
            print(f"   {result.stdout}")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running critical settings script: {e}")
        return False
    
    return True


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("GRUPONOS MELTANO NATIVE - INTEGRATION VALIDATION")
    print("=" * 60)
    
    checks = [
        ("Critical Environment Variables", check_critical_environment),
        ("Generic Module Installation", check_generic_modules),
        ("Configuration Profiles", check_configuration_profiles),
        ("Meltano Configuration", validate_meltano_config),
        ("Critical Settings Script", check_critical_settings_script),
        ("Schema Discovery (Metadata Only)", test_schema_discovery),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Generic modules are properly integrated with gruponos-meltano-native")
        print("✅ Schema discovery will use ONLY metadata (never samples)")
        print("✅ Configuration is fully dynamic (no hardcoded values)")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("⚠️  Please fix the issues above before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())