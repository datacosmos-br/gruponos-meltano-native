#!/bin/bash
# =============================================================================
# CRITICAL SETTINGS - NON-NEGOTIABLE - WILL ABORT IF CHANGED
# =============================================================================

# 🚨 SCHEMA DISCOVERY CRITICAL SETTINGS - MANDATORY
export TAP_ORACLE_WMS_USE_METADATA_ONLY=true
export TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE=0

# These values CANNOT be changed - the tap will ABORT if they are different
# Schema discovery MUST use ONLY the API describe metadata
# NO samples allowed - NO fallback schemas allowed - NO exceptions!

# Verify critical settings
if [ "$TAP_ORACLE_WMS_USE_METADATA_ONLY" != "true" ]; then
    echo "❌ CRITICAL ERROR: TAP_ORACLE_WMS_USE_METADATA_ONLY must be 'true' - ABORTING!"
    exit 1
fi

if [ "$TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE" != "0" ]; then
    echo "❌ CRITICAL ERROR: TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE must be '0' - ABORTING!"
    exit 1
fi

echo "✅ Critical settings verified - Schema discovery will use ONLY metadata"