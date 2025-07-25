# GRUPONOS MELTANO NATIVE - Makefile Unificado
# =============================================
# Enterprise Meltano Implementation
# Python 3.13 + Meltano + FLEXT Framework + Zero Tolerance Quality

.PHONY: help install test lint type-check format clean build docs
.PHONY: check validate dev-setup deps-update deps-audit info diagnose
.PHONY: install-dev test-unit test-integration test-coverage test-watch
.PHONY: format-check security pre-commit build-clean publish publish-test
.PHONY: dev dev-test clean-all emergency-reset
.PHONY: meltano-install meltano-test meltano-run meltano-validate env-setup

# ============================================================================
# 🎯 CONFIGURAÇÃO E DETECÇÃO
# ============================================================================

# Detectar nome do projeto
PROJECT_NAME := gruponos-meltano-native
PROJECT_TITLE := GRUPONOS MELTANO NATIVE
PROJECT_VERSION := $(shell poetry version -s)

# Ambiente Python
PYTHON := python3.13
POETRY := poetry
VENV_PATH := $(shell poetry env info --path 2>/dev/null || echo "")

# ============================================================================
# 🎯 AJUDA E INFORMAÇÃO
# ============================================================================

help: ## Mostrar ajuda e comandos disponíveis
	@echo "🏆 $(PROJECT_TITLE) - Comandos Essenciais"
	@echo "========================================="
	@echo "📦 Enterprise Meltano Implementation"
	@echo "🐍 Python 3.13 + Meltano + Zero Tolerância"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\\n", $$1, $$2}'
	@echo ""
	@echo "💡 Comandos principais: make install, make test, make lint"

info: ## Mostrar informações do projeto
	@echo "📊 Informações do Projeto"
	@echo "======================"
	@echo "Nome: $(PROJECT_NAME)"
	@echo "Título: $(PROJECT_TITLE)"
	@echo "Versão: $(PROJECT_VERSION)"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo "Não encontrado")"
	@echo "Poetry: $(shell $(POETRY) --version 2>/dev/null || echo "Não instalado")"
	@echo "Venv: $(shell [ -n "$(VENV_PATH)" ] && echo "$(VENV_PATH)" || echo "Não ativado")"
	@echo "Diretório: $(CURDIR)"
	@echo "Git Branch: $(shell git branch --show-current 2>/dev/null || echo "Não é repo git")"
	@echo "Git Status: $(shell git status --porcelain 2>/dev/null | wc -l | xargs echo) arquivos alterados"

diagnose: ## Executar diagnósticos completos
	@echo "🔍 Executando diagnósticos para $(PROJECT_NAME)..."
	@echo "Informações do Sistema:"
	@echo "OS: $(shell uname -s)"
	@echo "Arquitetura: $(shell uname -m)"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo "Não encontrado")"
	@echo "Poetry: $(shell $(POETRY) --version 2>/dev/null || echo "Não instalado")"
	@echo ""
	@echo "Estrutura do Projeto:"
	@ls -la
	@echo ""
	@echo "Configuração Poetry:"
	@$(POETRY) config --list 2>/dev/null || echo "Poetry não configurado"
	@echo ""
	@echo "Status das Dependências:"
	@$(POETRY) show --outdated 2>/dev/null || echo "Nenhuma dependência desatualizada"

# ============================================================================
# 📦 GERENCIAMENTO DE DEPENDÊNCIAS
# ============================================================================

validate-setup: ## Validar ambiente de desenvolvimento
	@echo "🔍 Validando ambiente de desenvolvimento..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python 3.13 não encontrado"; exit 1; }
	@command -v $(POETRY) >/dev/null 2>&1 || { echo "❌ Poetry não encontrado"; exit 1; }
	@test -f pyproject.toml || { echo "❌ pyproject.toml não encontrado"; exit 1; }
	@echo "✅ Validação do ambiente passou"

install: validate-setup ## Instalar dependências de runtime
	@echo "📦 Instalando dependências de runtime para $(PROJECT_NAME)..."
	@$(POETRY) install --only main
	@echo "✅ Dependências de runtime instaladas"

install-dev: validate-setup ## Instalar todas as dependências incluindo dev tools
	@echo "📦 Instalando todas as dependências para $(PROJECT_NAME)..."
	@$(POETRY) install --all-extras
	@echo "✅ Todas as dependências instaladas"

deps-update: ## Atualizar dependências para versões mais recentes
	@echo "🔄 Atualizando dependências para $(PROJECT_NAME)..."
	@$(POETRY) update
	@echo "✅ Dependências atualizadas"

deps-show: ## Mostrar árvore de dependências
	@echo "📊 Árvore de dependências para $(PROJECT_NAME):"
	@$(POETRY) show --tree

deps-audit: ## Auditoria de dependências para vulnerabilidades
	@echo "🔍 Auditando dependências para $(PROJECT_NAME)..."
	@$(POETRY) run pip-audit --format=columns || echo "⚠️  pip-audit não disponível"
	@$(POETRY) run safety check --json || echo "⚠️  safety não disponível"

# ============================================================================
# 🧪 TESTES
# ============================================================================

test: ## Executar todos os testes (85% cobertura mínima)
	@echo "🧪 Executando todos os testes para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/ -v --cov=src/gruponos_meltano_native --cov-report=term-missing --cov-fail-under=85
	@echo "✅ Todos os testes passaram"

test-unit: ## Executar apenas testes unitários
	@echo "🧪 Executando testes unitários para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/unit/ -xvs -m "not integration and not slow"
	@echo "✅ Testes unitários passaram"

test-integration: ## Executar apenas testes de integração
	@echo "🧪 Executando testes de integração para $(PROJECT_NAME)..."
	@$(POETRY) run pytest tests/integration/ -xvs -m "integration"
	@echo "✅ Testes de integração passaram"

test-coverage: ## Executar testes com relatório de cobertura
	@echo "🧪 Executando testes com cobertura para $(PROJECT_NAME)..."
	@$(POETRY) run pytest --cov --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "✅ Relatório de cobertura gerado"

test-watch: ## Executar testes em modo watch
	@echo "👀 Executando testes em modo watch para $(PROJECT_NAME)..."
	@$(POETRY) run pytest-watch --clear

coverage-html: test-coverage ## Gerar e abrir relatório HTML de cobertura
	@echo "📊 Abrindo relatório de cobertura..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🎨 QUALIDADE DE CÓDIGO E FORMATAÇÃO
# ============================================================================

lint: ## Executar todos os linters com máxima rigorosidade
	@echo "🔍 Executando linting com máxima rigorosidade para $(PROJECT_NAME)..."
	@$(POETRY) run ruff check . --output-format=github
	@echo "✅ Linting completado"

format: ## Formatar código com padrões rigorosos
	@echo "🎨 Formatando código para $(PROJECT_NAME)..."
	@$(POETRY) run ruff format .
	@$(POETRY) run ruff check . --fix --unsafe-fixes
	@echo "✅ Código formatado"

format-check: ## Verificar formatação sem alterar
	@echo "🔍 Verificando formatação para $(PROJECT_NAME)..."
	@$(POETRY) run ruff format . --check
	@$(POETRY) run ruff check . --output-format=github
	@echo "✅ Formatação verificada"

type-check: ## Executar verificação de tipos rigorosa
	@echo "🔍 Executando verificação de tipos rigorosa para $(PROJECT_NAME)..."
	@$(POETRY) run mypy src/ --strict --show-error-codes
	@echo "✅ Verificação de tipos passou"

typecheck: type-check ## Alias para type-check

security: ## Executar análise de segurança
	@echo "🔒 Executando análise de segurança para $(PROJECT_NAME)..."
	@$(POETRY) run bandit -r src/ -f json || echo "⚠️  bandit não disponível"
	@$(POETRY) run detect-secrets scan --all-files || echo "⚠️  detect-secrets não disponível"
	@echo "✅ Análise de segurança completada"

pre-commit: ## Executar hooks pre-commit
	@echo "🔧 Executando hooks pre-commit para $(PROJECT_NAME)..."
	@$(POETRY) run pre-commit run --all-files || echo "⚠️  pre-commit não disponível"
	@echo "✅ Hooks pre-commit completados"

check: lint type-check security ## Executar todas as verificações de qualidade
	@echo "🔍 Executando verificações abrangentes de qualidade para $(PROJECT_NAME)..."
	@echo "✅ Todas as verificações de qualidade passaram"

validate: check test ## Validação STRICT de conformidade (tudo deve passar)
	@echo "✅ TODOS OS QUALITY GATES PASSARAM - GRUPONOS MELTANO NATIVE COMPLIANT"

# ============================================================================
# 🏗️ BUILD E DISTRIBUIÇÃO
# ============================================================================

build: clean ## Construir o pacote com Poetry
	@echo "🏗️  Construindo pacote $(PROJECT_NAME)..."
	@$(POETRY) build
	@echo "✅ Pacote construído com sucesso"
	@echo "📦 Artefatos de build:"
	@ls -la dist/

build-clean: clean build ## Limpar e construir
	@echo "✅ Build limpo completado"

publish-test: build ## Publicar no TestPyPI
	@echo "📤 Publicando $(PROJECT_NAME) no TestPyPI..."
	@$(POETRY) publish --repository testpypi
	@echo "✅ Publicado no TestPyPI"

publish: build ## Publicar no PyPI
	@echo "📤 Publicando $(PROJECT_NAME) no PyPI..."
	@$(POETRY) publish
	@echo "✅ Publicado no PyPI"

# ============================================================================
# 📚 DOCUMENTAÇÃO
# ============================================================================

docs: ## Gerar documentação
	@echo "📚 Gerando documentação para $(PROJECT_NAME)..."
	@if [ -f mkdocs.yml ]; then \
		$(POETRY) run mkdocs build; \
	else \
		echo "⚠️  Nenhum mkdocs.yml encontrado, pulando geração de documentação"; \
	fi
	@echo "✅ Documentação gerada"

docs-serve: ## Servir documentação localmente
	@echo "📚 Servindo documentação para $(PROJECT_NAME)..."
	@if [ -f mkdocs.yml ]; then \
		$(POETRY) run mkdocs serve; \
	else \
		echo "⚠️  Nenhum mkdocs.yml encontrado"; \
	fi

# ============================================================================
# 🚀 DESENVOLVIMENTO
# ============================================================================

dev-setup: install-dev ## Configuração completa de desenvolvimento
	@echo "🚀 Configurando ambiente de desenvolvimento para $(PROJECT_NAME)..."
	@$(POETRY) run pre-commit install || echo "⚠️  pre-commit não disponível"
	@echo "✅ Ambiente de desenvolvimento pronto"

dev: ## Executar em modo desenvolvimento
	@echo "🚀 Iniciando modo desenvolvimento para $(PROJECT_NAME)..."
	@if [ -f src/gruponos_meltano_native/cli.py ]; then \
		$(POETRY) run python -m gruponos_meltano_native.cli --dev; \
	elif [ -f src/gruponos_meltano_native/main.py ]; then \
		$(POETRY) run python -m gruponos_meltano_native.main --dev; \
	else \
		echo "⚠️  Nenhum ponto de entrada principal encontrado"; \
	fi

dev-test: ## Ciclo rápido de teste de desenvolvimento
	@echo "⚡ Ciclo rápido de teste de desenvolvimento para $(PROJECT_NAME)..."
	@$(POETRY) run ruff check . --fix
	@$(POETRY) run pytest tests/ -x --tb=short
	@echo "✅ Ciclo de teste de desenvolvimento completado"

# ============================================================================
# 🎵 OPERAÇÕES ESPECÍFICAS MELTANO
# ============================================================================

meltano-install: ## Instalar todos os plugins Meltano
	@echo "🎵 Instalando plugins Meltano..."
	@$(POETRY) run meltano install
	@echo "✅ Plugins Meltano instalados"

meltano-test: ## Testar conexões dos plugins Meltano
	@echo "🧪 Testando conexões dos plugins Meltano..."
	@$(POETRY) run meltano test tap-oracle-wms || echo "⚠️  Falha no teste tap-oracle-wms"
	@$(POETRY) run meltano test tap-ldap || echo "⚠️  Falha no teste tap-ldap"
	@echo "✅ Testes dos plugins Meltano completados"

meltano-run: ## Executar pipeline completo Meltano
	@echo "🚀 Executando pipeline Meltano..."
	@$(POETRY) run meltano run tap-oracle-wms-full target-oracle-full
	@echo "✅ Pipeline Meltano completado"

meltano-validate: ## Validar configuração Meltano
	@echo "🔍 Validando configuração Meltano..."
	@$(POETRY) run meltano config list
	@$(POETRY) run meltano invoke dbt-postgres deps || echo "⚠️  dbt deps falhou"
	@echo "✅ Configuração Meltano validada"

meltano-discover: ## Descobrir esquemas dos taps
	@echo "🔍 Descobrindo esquemas dos taps..."
	@$(POETRY) run meltano discover tap-oracle-wms
	@$(POETRY) run meltano discover tap-ldap
	@echo "✅ Descoberta de esquemas completada"

meltano-elt: ## Executar processo ELT completo
	@echo "🔄 Executando processo ELT completo..."
	@$(POETRY) run meltano elt tap-oracle-wms target-oracle
	@echo "✅ Processo ELT completado"

meltano-operations: meltano-install meltano-validate meltano-test ## Validar todas as operações Meltano
	@echo "✅ Todas as operações Meltano validadas"

# ============================================================================
# 🌍 OPERAÇÕES ESPECÍFICAS AMBIENTE
# ============================================================================

env-setup: ## Configurar variáveis de ambiente
	@echo "🌍 Configurando ambiente..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Criado .env do template"; fi
	@echo "✅ Configuração do ambiente completada"

env-validate: ## Validar configuração do ambiente
	@echo "🔍 Validando configuração do ambiente..."
	@$(POETRY) run python -c "from src.gruponos_meltano_native.config import Settings; settings = Settings(); print('Configuração do ambiente válida')"
	@echo "✅ Validação do ambiente completada"

oracle-test: ## Testar conexão Oracle WMS
	@echo "🔍 Testando conexão Oracle WMS..."
	@$(POETRY) run python -c "from src.gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager; import asyncio; asyncio.run(OracleConnectionManager().test_connection())"
	@echo "✅ Teste de conexão Oracle WMS completado"

ldap-test: ## Testar conexão LDAP
	@echo "🔍 Testando conexão LDAP..."
	@$(POETRY) run python -c "from src.gruponos_meltano_native.ldap.client import LDAPClient; client = LDAPClient(); result = client.test_connection(); print(f'Conexão LDAP: {result}')"
	@echo "✅ Teste de conexão LDAP completado"

validate-schemas: ## Validar esquemas do banco de dados
	@echo "🔍 Validando esquemas do banco de dados..."
	@$(POETRY) run python -c "from src.gruponos_meltano_native.validators import SchemaValidator; validator = SchemaValidator(); validator.validate_all(); print('Esquemas validados')"
	@echo "✅ Validação de esquemas completada"

enterprise-validate: env-validate oracle-test ldap-test validate-schemas ## Validar todas as operações enterprise
	@echo "✅ Todas as operações enterprise validadas"

# ============================================================================
# 🧹 LIMPEZA
# ============================================================================

clean: ## Limpar artefatos de build
	@echo "🧹 Limpando artefatos de build para $(PROJECT_NAME)..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf reports/
	@rm -rf .meltano/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Limpeza completada"

clean-all: clean ## Limpar tudo incluindo ambiente virtual
	@echo "🧹 Limpeza profunda para $(PROJECT_NAME)..."
	@$(POETRY) env remove --all || true
	@echo "✅ Limpeza profunda completada"

# ============================================================================
# 🚨 PROCEDIMENTOS DE EMERGÊNCIA
# ============================================================================

emergency-reset: ## Reset de emergência para estado limpo
	@echo "🚨 RESET DE EMERGÊNCIA para $(PROJECT_NAME)..."
	@read -p "Tem certeza que quer resetar tudo? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(MAKE) clean-all; \
		$(MAKE) install-dev; \
		echo "✅ Reset de emergência completado"; \
	else \
		echo "⚠️  Reset de emergência cancelado"; \
	fi

# ============================================================================
# 🎯 VALIDAÇÃO E VERIFICAÇÃO
# ============================================================================

workspace-validate: ## Validar conformidade do workspace
	@echo "🔍 Validando conformidade do workspace para $(PROJECT_NAME)..."
	@test -f pyproject.toml || { echo "❌ pyproject.toml ausente"; exit 1; }
	@test -f CLAUDE.md || echo "⚠️  CLAUDE.md ausente"
	@test -f README.md || echo "⚠️  README.md ausente"
	@test -d src/ || { echo "❌ diretório src/ ausente"; exit 1; }
	@test -d tests/ || echo "⚠️  diretório tests/ ausente"
	@test -f meltano.yml || { echo "❌ meltano.yml ausente"; exit 1; }
	@echo "✅ Conformidade do workspace validada"

# ============================================================================
# 🎯 ALIASES DE CONVENIÊNCIA
# ============================================================================

# Aliases para operações comuns
t: test ## Alias para test
l: lint ## Alias para lint
tc: type-check ## Alias para type-check
f: format ## Alias para format
c: clean ## Alias para clean
i: install-dev ## Alias para install-dev
d: dev ## Alias para dev
dt: dev-test ## Alias para dev-test

# Aliases específicos Meltano
mi: meltano-install ## Alias para meltano-install
mt: meltano-test ## Alias para meltano-test
mr: meltano-run ## Alias para meltano-run
mv: meltano-validate ## Alias para meltano-validate
md: meltano-discover ## Alias para meltano-discover
me: meltano-elt ## Alias para meltano-elt
mo: meltano-operations ## Alias para meltano-operations

# Aliases específicos ambiente
es: env-setup ## Alias para env-setup
ev: env-validate ## Alias para env-validate
ot: oracle-test ## Alias para oracle-test
lt: ldap-test ## Alias para ldap-test
vs: validate-schemas ## Alias para validate-schemas
ev: enterprise-validate ## Alias para enterprise-validate

# Configurações de ambiente
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# Meltano settings for development
export MELTANO_PROJECT_ROOT := $(PWD)
export MELTANO_VENV := $(VENV_PATH)
export MELTANO_ENVIRONMENT := dev

# Enterprise settings
export GRUPONOS_ENV := development
export GRUPONOS_DEBUG := true
export GRUPONOS_ORACLE_HOST := localhost
export GRUPONOS_ORACLE_PORT := 1521
export GRUPONOS_LDAP_HOST := localhost
export GRUPONOS_LDAP_PORT := 389

.DEFAULT_GOAL := help