# gruponos-meltano-native - Meltano ETL Service
PROJECT_NAME := gruponos-meltano-native
COV_DIR := gruponos_meltano_native
MIN_COVERAGE := 85

# Cross-project PYTHONPATH
FLEXT_ROOT := $(abspath ..)

include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: meltano-install meltano-test meltano-run meltano-validate meltano-discover
.PHONY: meltano-elt meltano-operations
.PHONY: env-setup env-validate oracle-test ldap-test validate-schemas enterprise-validate
.PHONY: test-unit test-integration build docs docs-serve shell pre-commit
.PHONY: deps-audit diagnose doctor

# Meltano operations
meltano-install: ## Install Meltano plugins
	$(Q)$(POETRY) run meltano install

meltano-test: ## Test Meltano plugin connections
	$(Q)$(POETRY) run meltano test tap-oracle-wms || echo "Tap test failed"
	$(Q)$(POETRY) run meltano test tap-ldap || echo "LDAP test failed"

meltano-run: ## Execute full Meltano pipeline
	$(Q)$(POETRY) run meltano run tap-oracle-wms-full target-oracle-full

meltano-validate: ## Validate Meltano configuration
	$(Q)$(POETRY) run meltano config list
	$(Q)$(POETRY) run meltano invoke dbt-postgres deps || echo "DBT deps failed"

meltano-discover: ## Discover schemas from taps
	$(Q)$(POETRY) run meltano discover tap-oracle-wms
	$(Q)$(POETRY) run meltano discover tap-ldap

meltano-elt: ## Run ELT process
	$(Q)$(POETRY) run meltano elt tap-oracle-wms target-oracle

meltano-operations: meltano-install meltano-validate meltano-test ## Execute all Meltano operations

# GrupoNOS operations
env-setup: ## Setup environment variables
	$(Q)if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from template"; fi

env-validate: ## Validate environment configuration
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.config import Settings; settings = Settings(); print('Environment configuration valid')"

oracle-test: ## Test Oracle WMS connection
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager; import asyncio; asyncio.run(OracleConnectionManager().test_connection())"

ldap-test: ## Test LDAP connection
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.ldap.client import LDAPClient; client = LDAPClient(); result = client.test_connection(); print(f'LDAP connection: {result}')"

validate-schemas: ## Validate database schemas
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.validators import SchemaValidator; validator = SchemaValidator(); validator.validate_all(); print('Schemas validated')"

enterprise-validate: env-validate oracle-test ldap-test validate-schemas ## Validate all enterprise operations

# Testing
# Build and docs
docs: ## Build documentation
	$(Q)$(POETRY) run mkdocs build

docs-serve: ## Serve documentation
	$(Q)$(POETRY) run mkdocs serve

# Dependencies
deps-audit: ## Audit dependencies
	$(Q)$(POETRY) run pip-audit

# Development
pre-commit: ## Run pre-commit hooks
	$(Q)$(POETRY) run pre-commit run --all-files

# Diagnostics
diagnose: ## Project diagnostics
	$(Q)echo "Python: $$(python --version)"
	$(Q)echo "Poetry: $$($(POETRY) --version)"
	$(Q)echo "Meltano: $$($(POETRY) run meltano --version 2>/dev/null || echo 'Not available')"
	$(Q)$(POETRY) env info

doctor: diagnose check ## Health check

# Short aliases for Meltano
mi: meltano-install
mt: meltano-test
mr: meltano-run
mv: meltano-validate
md: meltano-discover
me: meltano-elt
mo: meltano-operations

.DEFAULT_GOAL := help
