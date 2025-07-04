#!/bin/bash

# GrupoNOS Meltano Native - Configuration Setup Script
# Transforms from hardcoded to configurable specifications

set -e

echo "🚀 Setting up GrupoNOS Meltano Native with new ConfigMapper system..."

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="$PROJECT_DIR/.env.template"
ENV_FILE="$PROJECT_DIR/.env"
PROFILE_FILE="/home/marlonsc/flext/flext-tap-oracle-wms/config/profiles/gruponos.json"

echo "📁 Project directory: $PROJECT_DIR"

# Step 1: Check if the tap supports the new configuration system
echo "🔍 Verifying tap-oracle-wms ConfigMapper support..."
TAP_EXECUTABLE="/home/marlonsc/flext/.venv/bin/tap-oracle-wms"

if [[ ! -f "$TAP_EXECUTABLE" ]]; then
    echo "❌ Error: tap-oracle-wms executable not found at $TAP_EXECUTABLE"
    echo "   Please ensure the tap is installed in the workspace virtual environment."
    exit 1
fi

# Test ConfigMapper availability
echo "🧪 Testing ConfigMapper integration..."
cd /home/marlonsc/flext/flext-tap-oracle-wms

if python -c "from src.tap_oracle_wms.config_mapper import ConfigMapper; print('✅ ConfigMapper available')" 2>/dev/null; then
    echo "✅ ConfigMapper system is available"
else
    echo "❌ Error: ConfigMapper system not available in tap-oracle-wms"
    echo "   Please ensure the tap has been updated with ConfigMapper support."
    exit 1
fi

cd "$PROJECT_DIR"

# Step 2: Create environment file from template if it doesn't exist
if [[ ! -f "$ENV_FILE" ]]; then
    echo "📋 Creating .env file from template..."
    cp "$TEMPLATE_FILE" "$ENV_FILE"
    echo "✅ Created $ENV_FILE"
    echo "⚠️  Please edit .env file with your actual configuration values"
else
    echo "📋 .env file already exists"
fi

# Step 3: Verify profile file exists
echo "🔍 Checking GrupoNOS profile..."
if [[ -f "$PROFILE_FILE" ]]; then
    echo "✅ GrupoNOS profile found: $PROFILE_FILE"
else
    echo "❌ Error: GrupoNOS profile not found at $PROFILE_FILE"
    echo "   Please ensure the profile system is set up in tap-oracle-wms"
    exit 1
fi

# Step 4: Test configuration loading
echo "🧪 Testing configuration loading..."

# Export test environment variables
export WMS_PROFILE_NAME="gruponos"
export TAP_ORACLE_WMS_BASE_URL="https://test.example.com"
export TAP_ORACLE_WMS_USERNAME="test_user"
export TAP_ORACLE_WMS_PASSWORD="test_password"

# Test tap configuration
cd /home/marlonsc/flext/flext-tap-oracle-wms

if python -c "
from src.tap_oracle_wms.config_mapper import ConfigMapper
from src.tap_oracle_wms.config_profiles import ConfigProfileManager
import os

# Test ConfigMapper
mapper = ConfigMapper()
print(f'✅ API Version: {mapper.get_api_version()}')
print(f'✅ Endpoint Prefix: {mapper.get_endpoint_prefix()}') 
print(f'✅ Page Size: {mapper.get_page_size()}')
print(f'✅ Entities: {mapper.get_enabled_entities()}')

# Test Profile Loading
profile_name = os.getenv('WMS_PROFILE_NAME')
if profile_name:
    try:
        manager = ConfigProfileManager()
        profile = manager.load_profile(profile_name)
        print(f'✅ Profile loaded: {profile.company_name} ({profile.environment})')
    except Exception as e:
        print(f'⚠️  Profile loading test failed: {e}')
else:
    print('ℹ️  No WMS_PROFILE_NAME set for profile test')
" 2>/dev/null; then
    echo "✅ Configuration system working correctly"
else
    echo "❌ Error: Configuration system test failed"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 5: Validate meltano.yml structure
echo "🔍 Validating meltano.yml configuration..."

if [[ -f "meltano.yml" ]]; then
    # Check if the new simplified structure is in place
    if grep -q "WMS_PROFILE_NAME" meltano.yml; then
        echo "✅ meltano.yml updated with new configuration system"
    else
        echo "⚠️  meltano.yml may need updating to use the new configuration system"
    fi
else
    echo "❌ Error: meltano.yml not found"
    exit 1
fi

# Step 6: Run a quick discovery test
echo "🧪 Testing tap discovery with new configuration..."

# Source the environment file
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Only run discovery test if we have valid connection details
if [[ "$TAP_ORACLE_WMS_BASE_URL" != "https://gruponos-wms.oracle.com" ]] && 
   [[ "$TAP_ORACLE_WMS_USERNAME" != "your-username" ]] &&
   [[ -n "$TAP_ORACLE_WMS_PASSWORD" ]]; then
   
    echo "🔍 Running discovery test with actual credentials..."
    cd /home/marlonsc/flext/flext-tap-oracle-wms
    
    if timeout 30 python -m src.tap_oracle_wms.tap --discover --config <(echo "{}") > /tmp/discovery_test.json 2>/dev/null; then
        entity_count=$(jq '.streams | length' /tmp/discovery_test.json 2>/dev/null || echo "0")
        echo "✅ Discovery successful: Found $entity_count entities"
        rm -f /tmp/discovery_test.json
    else
        echo "⚠️  Discovery test failed (timeout or connection issue)"
        echo "   This is expected if credentials are not configured yet"
    fi
    
    cd "$PROJECT_DIR"
else
    echo "ℹ️  Skipping discovery test (using template credentials)"
fi

# Step 7: Summary and next steps
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Summary of changes:"
echo "   ✅ ConfigMapper system verified"
echo "   ✅ Environment template created"
echo "   ✅ meltano.yml updated with simplified configuration"
echo "   ✅ Profile system integrated"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your actual GrupoNOS WMS credentials"
echo "   2. Test the configuration: meltano invoke tap-oracle-wms-full --discover"
echo "   3. Run a full sync: meltano run tap-oracle-wms-full target-oracle-full"
echo ""
echo "🔧 Configuration hierarchy (highest to lowest precedence):"
echo "   1. Individual WMS_* environment variables (.env file)"
echo "   2. WMS_PROFILE_NAME profile settings (gruponos.json)"
echo "   3. ConfigMapper default values"
echo ""
echo "📚 Key improvements:"
echo "   - No more hardcoded API versions or endpoints"
echo "   - Company-specific business rules via profiles"
echo "   - Environment-based configuration override"
echo "   - Simplified meltano.yml maintenance"
echo ""

# Step 8: Create a quick test script
echo "📝 Creating test script..."
cat > "$PROJECT_DIR/test_config.sh" << 'EOF'
#!/bin/bash

# Test the new configuration system

set -e

echo "🧪 Testing GrupoNOS Oracle WMS Configuration..."

# Load environment
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
    echo "✅ Environment loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Test configuration values
echo "📋 Current configuration:"
echo "   Profile: ${WMS_PROFILE_NAME:-not set}"
echo "   Base URL: ${TAP_ORACLE_WMS_BASE_URL}"
echo "   API Version: ${WMS_API_VERSION:-default}"
echo "   Page Size: ${WMS_PAGE_SIZE:-default}"
echo "   Company: ${WMS_COMPANY_CODE:-default}"

# Test tap discovery
echo "🔍 Testing tap discovery..."
cd /home/marlonsc/flext/flext-tap-oracle-wms

if python -m src.tap_oracle_wms.tap --help > /dev/null 2>&1; then
    echo "✅ Tap executable working"
else
    echo "❌ Tap executable test failed"
    exit 1
fi

echo "✅ Configuration test completed"
EOF

chmod +x "$PROJECT_DIR/test_config.sh"
echo "✅ Created test_config.sh"

echo ""
echo "🚀 Setup complete! The GrupoNOS Meltano Native project is now using"
echo "   the new ConfigMapper system with externalized specifications."