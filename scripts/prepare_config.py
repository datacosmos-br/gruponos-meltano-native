#!/usr/bin/env python3
"""
Script to prepare configuration files with environment variable substitution.
This ensures all configurations come from the .env file.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict


def load_env_file(env_path: str) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars: Dict[str, str] = {}
    if not os.path.exists(env_path):
        print(f"Warning: .env file not found at {env_path}")
        return env_vars
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"\'')
                env_vars[key] = value
    
    return env_vars


def substitute_env_vars(config_str: str, env_vars: Dict[str, str]) -> str:
    """Substitute ${VAR_NAME} patterns with actual environment variable values."""
    def replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1)
        # Try environment first, then .env file
        value = os.environ.get(var_name) or env_vars.get(var_name)
        if value is None:
            print(f"Warning: Environment variable {var_name} not found")
            return match.group(0)  # Return original if not found
        
        # Handle boolean values
        if value.lower() in ('true', 'false'):
            return value.lower()
        # Handle integer values
        elif value.isdigit():
            return value
        # Handle float values
        elif value.replace('.', '', 1).isdigit():
            return value
        else:
            # Return string value without quotes (they're already in template)
            return value
    
    # Replace ${VAR_NAME} patterns
    return re.sub(r'\$\{([^}]+)\}', replace_var, config_str)


def prepare_target_config() -> bool:
    """Prepare target configuration with environment variable substitution."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    config_template = project_root / "target_config.json"
    config_output = project_root / "target_config_resolved.json"
    
    # Load environment variables
    env_vars = load_env_file(str(env_file))
    
    # Read template
    with open(config_template, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Substitute variables
    resolved_content = substitute_env_vars(template_content, env_vars)
    
    # Write resolved configuration
    with open(config_output, 'w', encoding='utf-8') as f:
        f.write(resolved_content)
    
    print(f"✅ Target configuration prepared: {config_output}")
    
    # Validate JSON
    try:
        with open(config_output, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ Configuration JSON is valid")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration: {e}")
        return False
    
    return True


def verify_env_variables() -> bool:
    """Verify that all required environment variables are set."""
    required_vars = [
        'FLEXT_TARGET_ORACLE_HOST',
        'FLEXT_TARGET_ORACLE_PORT',
        'FLEXT_TARGET_ORACLE_SERVICE_NAME',
        'FLEXT_TARGET_ORACLE_USERNAME',
        'FLEXT_TARGET_ORACLE_PASSWORD',
        'FLEXT_TARGET_ORACLE_PROTOCOL',
        'TAP_ORACLE_WMS_BASE_URL',
        'TAP_ORACLE_WMS_USERNAME',
        'TAP_ORACLE_WMS_PASSWORD',
        'WMS_PROFILE_NAME'
    ]
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_vars = load_env_file(str(env_file))
    
    missing_vars = []
    for var in required_vars:
        if var not in env_vars and var not in os.environ:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables are set")
    return True


def main() -> int:
    """Main function to prepare all configurations."""
    print("🔧 Preparing configurations from .env file...")
    
    # Verify environment variables
    if not verify_env_variables():
        return 1
    
    # Prepare target configuration
    if not prepare_target_config():
        return 1
    
    print("✅ All configurations prepared successfully!")
    return 0


if __name__ == "__main__":
    exit(main()) 
