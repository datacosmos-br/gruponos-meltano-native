# GRUPONOS MELTANO NATIVE - GENERICIZATION SUMMARY

## Overview

This document summarizes the complete transformation of gruponos-meltano-native to use generic flext-tap-oracle-wms and flext-target-oracle modules, removing all hardcoded values and enforcing critical schema discovery rules.

## Critical Schema Discovery Enforcement

### 🚨 NON-NEGOTIABLE RULES

1. **TAP_ORACLE_WMS_USE_METADATA_ONLY=true** - MUST always be true
2. **TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE=0** - MUST always be 0

These settings ensure schema discovery uses ONLY API metadata, NEVER samples. Any attempt to change these values will cause immediate abort.

### Enforcement Mechanisms

1. **Environment Variables**: Set in `.env.example` with clear warnings
2. **Critical Settings Script**: `config/critical_settings.sh` validates before every run
3. **Makefile Integration**: All tap commands source critical settings first
4. **Code Enforcement**: tap.py validates and aborts if values are incorrect

## Configuration Architecture

### 1. Environment-Based Configuration

All hardcoded values have been moved to environment variables:

```bash
# Core Settings (required)
TAP_ORACLE_WMS_BASE_URL
TAP_ORACLE_WMS_USERNAME
TAP_ORACLE_WMS_PASSWORD
FLEXT_TARGET_ORACLE_HOST
FLEXT_TARGET_ORACLE_SERVICE_NAME
FLEXT_TARGET_ORACLE_USERNAME
FLEXT_TARGET_ORACLE_PASSWORD

# Optional Overrides
WMS_PROFILE_NAME          # Company-specific profile
WMS_PAGE_SIZE            # Performance tuning
WMS_API_VERSION          # API version selection
WMS_REQUEST_TIMEOUT      # Request timeout (0 = unlimited)
```

### 2. ConfigMapper System

The tap now uses a sophisticated configuration mapping system:

```
Priority Order:
1. Individual environment variables (highest)
2. Company profile (WMS_PROFILE_NAME)
3. ConfigMapper defaults (lowest)
```

### 3. Project Configuration Files

```
config/
├── critical_settings.sh      # Enforces metadata-only discovery
├── project.yml              # Generic project metadata
├── wms_integration.yml      # WMS-specific settings
└── profiles/                # Company-specific profiles
    └── gruponos.json       # GrupoNOS business rules
```

## Key Changes Made

### 1. meltano.yml

- Removed ALL hardcoded values
- Added critical settings variables
- Uses environment variables for all configurations
- Page size now configurable via `$WMS_PAGE_SIZE`

### 2. .env.example

- Cleaned up to contain only essential settings
- Added critical schema discovery settings with warnings
- Removed all artificial limitations
- Clear documentation of each variable

### 3. Makefile Updates

- All tap commands now source `critical_settings.sh`
- Added `validate-integration` command
- Updated help documentation
- Critical settings validation before every sync

### 4. New Scripts

- `scripts/configure_project.py` - Dynamic configuration generator
- `scripts/validate_integration.py` - Comprehensive validation
- `config/critical_settings.sh` - Enforces metadata-only discovery

### 5. Removed Hardcoded References

All references to gruponos-specific values have been genericized:
- Company name → `${COMPANY_NAME}`
- Project name → `${PROJECT_NAME}`
- Business rules → Profile-based configuration

## Validation

Run complete validation with:

```bash
make validate-integration
```

This checks:
1. ✅ Critical environment variables
2. ✅ Generic module installation
3. ✅ Configuration profiles
4. ✅ Meltano configuration
5. ✅ Schema discovery (metadata only)
6. ✅ Critical settings enforcement

## Usage

### Quick Start

1. Copy `.env.example` to `.env`
2. Set required connection variables
3. Run validation: `make validate-integration`
4. Start sync: `make full-sync`

### Company-Specific Configuration

To use company-specific business rules:

```bash
export WMS_PROFILE_NAME=gruponos
```

### Performance Tuning

Override default settings via environment:

```bash
export WMS_PAGE_SIZE=1000        # Higher throughput
export WMS_REQUEST_TIMEOUT=0     # No timeout
export WMS_MAX_RETRIES=10        # More resilient
```

## Benefits

1. **Generic Modules**: Can be used by any project
2. **No Hardcoded Values**: Everything configurable
3. **Enforced Best Practices**: Metadata-only discovery
4. **Company Profiles**: Business rules without code changes
5. **Performance Flexibility**: Tune without modifying code

## Critical Notes

1. **NEVER** change `TAP_ORACLE_WMS_USE_METADATA_ONLY` from `true`
2. **NEVER** change `TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE` from `0`
3. **ALWAYS** run `make validate-integration` after configuration changes
4. **USE** environment variables for all customization

## Migration Guide

For other projects wanting to use these generic modules:

1. Copy `.env.example` and customize
2. Create company profile in `config/profiles/`
3. Set `WMS_PROFILE_NAME` to your profile
4. Run `make validate-integration`
5. Start using generic tap and target!

---

**Status**: ✅ COMPLETE - All hardcoded values removed, critical settings enforced
**Modules**: 100% generic and reusable
**Configuration**: Fully dynamic via environment and profiles