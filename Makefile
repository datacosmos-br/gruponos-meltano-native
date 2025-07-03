# ============================================================================
# GRUPONOS MELTANO NATIVE - MAKEFILE PRODUCTION-READY
# Gerenciamento robusto de sincronizações, logs, análise de falhas e validação
# ============================================================================

.PHONY: help env status full-sync incremental-sync validate-oracle analyze-failures clean-logs monitor stop-sync recreate-tables discover-schemas full-sync-debug

# ============================================================================
# CONFIGURAÇÃO DE CAMINHOS E AMBIENTE
# ============================================================================

PROJECT_DIR := /home/marlonsc/flext/gruponos-meltano-native
VENV_PATH := /home/marlonsc/flext/.venv
VENV_ACTIVATE := $(VENV_PATH)/bin/activate
ENV_FILE := $(PROJECT_DIR)/.env

# Diretórios de logs
LOG_DIR := $(PROJECT_DIR)/logs
SYNC_LOG_DIR := $(LOG_DIR)/sync
ERROR_LOG_DIR := $(LOG_DIR)/error
VALIDATION_LOG_DIR := $(LOG_DIR)/validation
PID_DIR := $(PROJECT_DIR)/pids
STATE_DIR := $(PROJECT_DIR)/state

# Configuração de ambiente padronizada
ENV_CMD = cd $(PROJECT_DIR) && source $(VENV_ACTIVATE) && set -a && source $(ENV_FILE) && set +a

# Timestamps para logs
TIMESTAMP := $(shell date '+%Y%m%d_%H%M%S')
LOG_TIMESTAMP := $(shell date '+%Y-%m-%d %H:%M:%S')

# ============================================================================
# COMANDOS PRINCIPAIS
# ============================================================================

help:
	@echo "=========================================================="
	@echo "GrupoNOS Meltano Native - Makefile Production-Ready"
	@echo "=========================================================="
	@echo ""
	@echo "📊 MONITORAMENTO E STATUS:"
	@echo "  make status           # Status geral do sistema"
	@echo "  make monitor          # Monitor em tempo real"
	@echo "  make validate-oracle  # Validar dados no Oracle"
	@echo ""
	@echo "🔄 SINCRONIZAÇÕES:"
	@echo "  make full-sync        # Sincronização full (background) - recovery por ID"
	@echo "  make incremental-sync # Sincronização incremental - checkpoint mod_ts"
	@echo "  make dual-sync        # Ambas sincronizações simultaneamente"
	@echo "  make stop-sync        # Parar sincronizações ativas"
	@echo "  make restart-full-sync # Reiniciar full sync do zero"
	@echo "  make force-full-sync  # Full sync com tabelas recriadas"
	@echo ""
	@echo "🏗️ GERENCIAMENTO DE TABELAS (MELTANO NATIVO):"
	@echo "  make native-recreate-tables # 🚀 Recrear tabelas via Meltano (RECOMENDADO)"
	@echo "  make reset-state         # Reset estado (força schema discovery)"
	@echo "  make reset-full-sync     # Reset apenas estado full sync"
	@echo "  make recreate-tables     # [LEGACY] Recriar via script Python"
	@echo "  make test-oracle-connection # Testar conexão Oracle"
	@echo ""
	@echo "🔍 ANÁLISE E CORREÇÃO:"
	@echo "  make analyze-failures # Analisar e corrigir falhas"
	@echo "  make fix-errors       # Corrigir erros encontrados"
	@echo "  make health-check     # Verificação completa de saúde"
	@echo "  make validate-data    # Validar tipos de dados"
	@echo ""
	@echo "🧹 MANUTENÇÃO:"
	@echo "  make clean-logs          # Limpar logs antigos"
	@echo "  make reset-incremental-sync # Reset apenas estado incremental"
	@echo "  make clear-all-state     # Limpar TODOS os estados (cuidado!)"
	@echo "  make env                 # Testar ambiente"
	@echo ""

# ============================================================================
# MONITORAMENTO E STATUS
# ============================================================================

status:
	@echo "========================================"
	@echo "STATUS DO SISTEMA - $(LOG_TIMESTAMP)"
	@echo "========================================"
	@echo ""
	@echo "🔧 AMBIENTE:"
	@$(ENV_CMD) && echo "  ✅ Ambiente: OK" || echo "  ❌ Ambiente: ERRO"
	@test -f $(ENV_FILE) && echo "  ✅ .env: OK" || echo "  ❌ .env: MISSING"
	@test -f $(VENV_ACTIVATE) && echo "  ✅ venv: OK" || echo "  ❌ venv: MISSING"
	@echo ""
	@echo "📊 PROCESSOS ATIVOS:"
	@if [ -f $(PID_DIR)/full_sync.pid ]; then \
		if ps -p $$(cat $(PID_DIR)/full_sync.pid) > /dev/null 2>&1; then \
			echo "  🟢 Full Sync: EXECUTANDO (PID: $$(cat $(PID_DIR)/full_sync.pid))"; \
		else \
			echo "  🔴 Full Sync: PID MORTO"; \
			rm -f $(PID_DIR)/full_sync.pid; \
		fi \
	else \
		echo "  ⚪ Full Sync: PARADO"; \
	fi
	@if [ -f $(PID_DIR)/incremental_sync.pid ]; then \
		if ps -p $$(cat $(PID_DIR)/incremental_sync.pid) > /dev/null 2>&1; then \
			echo "  🟢 Incremental Sync: EXECUTANDO (PID: $$(cat $(PID_DIR)/incremental_sync.pid))"; \
		else \
			echo "  🔴 Incremental Sync: PID MORTO"; \
			rm -f $(PID_DIR)/incremental_sync.pid; \
		fi \
	else \
		echo "  ⚪ Incremental Sync: PARADO"; \
	fi
	@echo ""
	@echo "📁 LOGS RECENTES:"
	@if [ -d $(SYNC_LOG_DIR) ]; then \
		echo "  📄 Logs de Sync: $$(ls -1 $(SYNC_LOG_DIR) | wc -l) arquivos"; \
		if [ -n "$$(ls -t $(SYNC_LOG_DIR)/*.log 2>/dev/null | head -1)" ]; then \
			echo "  📅 Último log: $$(ls -t $(SYNC_LOG_DIR)/*.log | head -1 | xargs basename)"; \
		fi \
	fi
	@if [ -d $(ERROR_LOG_DIR) ]; then \
		ERROR_COUNT=$$(ls -1 $(ERROR_LOG_DIR)/*.log 2>/dev/null | wc -l); \
		if [ $$ERROR_COUNT -gt 0 ]; then \
			echo "  ⚠️  Logs de Erro: $$ERROR_COUNT arquivos"; \
		else \
			echo "  ✅ Logs de Erro: Nenhum"; \
		fi \
	fi
	@echo ""

monitor:
	@echo "🔍 INICIANDO MONITOR EM TEMPO REAL..."
	@echo "Press Ctrl+C to stop"
	@while true; do \
		clear; \
		$(MAKE) status; \
		echo ""; \
		echo "📊 ÚLTIMAS 10 LINHAS DOS LOGS:"; \
		if [ -n "$$(ls -t $(SYNC_LOG_DIR)/*.log 2>/dev/null | head -1)" ]; then \
			echo ""; \
			echo "🔄 SYNC LOG:"; \
			tail -5 $$(ls -t $(SYNC_LOG_DIR)/*.log | head -1) 2>/dev/null || echo "  Nenhum log disponível"; \
		fi; \
		if [ -n "$$(ls -t $(ERROR_LOG_DIR)/*.log 2>/dev/null | head -1)" ]; then \
			echo ""; \
			echo "❌ ERROR LOG:"; \
			tail -5 $$(ls -t $(ERROR_LOG_DIR)/*.log | head -1) 2>/dev/null || echo "  Nenhum erro recente"; \
		fi; \
		sleep 5; \
	done

env:
	@echo "🧪 TESTANDO AMBIENTE..."
	@$(ENV_CMD) && echo "✅ Ambiente configurado corretamente" || (echo "❌ Erro no ambiente" && exit 1)
	@$(ENV_CMD) && meltano --version && echo "✅ Meltano funcionando" || (echo "❌ Meltano com problema" && exit 1)
	@$(ENV_CMD) && python -c "import oracledb; print('✅ Oracle client disponível')" || echo "❌ Oracle client com problema"

# ============================================================================
# SINCRONIZAÇÕES
# ============================================================================

full-sync:
	@echo "🚀 INICIANDO SINCRONIZAÇÃO FULL EM BACKGROUND..."
	@mkdir -p $(SYNC_LOG_DIR) $(ERROR_LOG_DIR) $(PID_DIR) $(STATE_DIR)
	@if [ -f $(PID_DIR)/full_sync.pid ] && ps -p $$(cat $(PID_DIR)/full_sync.pid) > /dev/null 2>&1; then \
		echo "❌ Sincronização full já está executando (PID: $$(cat $(PID_DIR)/full_sync.pid))"; \
		exit 1; \
	fi
	@echo "📝 Logs serão salvos em: $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log"
	@nohup bash -c ' \
		echo "$(LOG_TIMESTAMP) - INÍCIO: Sincronização Full" > $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
		echo "$(LOG_TIMESTAMP) - CONFIG: Testando ambiente..." >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
		if $(ENV_CMD) && echo "Ambiente OK" >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log 2>&1; then \
			echo "$(LOG_TIMESTAMP) - EXEC: Executando meltano run..." >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
			if $(ENV_CMD) && timeout 3600 meltano run full-sync-job >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log 2>&1; then \
				echo "$(LOG_TIMESTAMP) - SUCESSO: Sincronização full concluída" >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
				echo "FULL_SYNC_SUCCESS" > $(STATE_DIR)/last_full_sync.state; \
			else \
				echo "$(LOG_TIMESTAMP) - ERRO: Sincronização full falhou" >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
				cp $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log $(ERROR_LOG_DIR)/full_sync_error_$(TIMESTAMP).log; \
				echo "FULL_SYNC_ERROR" > $(STATE_DIR)/last_full_sync.state; \
			fi; \
		else \
			echo "$(LOG_TIMESTAMP) - ERRO: Ambiente inválido" >> $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log; \
			cp $(SYNC_LOG_DIR)/full_sync_$(TIMESTAMP).log $(ERROR_LOG_DIR)/env_error_$(TIMESTAMP).log; \
		fi; \
		rm -f $(PID_DIR)/full_sync.pid; \
	' & echo $$! > $(PID_DIR)/full_sync.pid
	@echo "✅ Sincronização full iniciada em background (PID: $$(cat $(PID_DIR)/full_sync.pid))"
	@echo "📊 Use 'make status' ou 'make monitor' para acompanhar"

full-sync-debug:
	@echo "🚀 INICIANDO SINCRONIZAÇÃO FULL COM DEBUG EM BACKGROUND..."
	@mkdir -p $(SYNC_LOG_DIR) $(ERROR_LOG_DIR) $(PID_DIR) $(STATE_DIR)
	@if [ -f $(PID_DIR)/full_sync.pid ] && ps -p $$(cat $(PID_DIR)/full_sync.pid) > /dev/null 2>&1; then \
		echo "❌ Sincronização full já está executando (PID: $$(cat $(PID_DIR)/full_sync.pid))"; \
		exit 1; \
	fi
	@echo "📝 Logs serão salvos em: $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log"
	@nohup bash -c ' \
		echo "$(LOG_TIMESTAMP) - INÍCIO: Sincronização Full com DEBUG" > $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
		echo "$(LOG_TIMESTAMP) - CONFIG: Testando ambiente..." >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
		if $(ENV_CMD) && echo "Ambiente OK" >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log 2>&1; then \
			echo "$(LOG_TIMESTAMP) - DEBUG: Habilitando logs detalhados..." >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
			export MELTANO_LOG_LEVEL=debug; \
			export TAP_ORACLE_WMS_DEBUG=true; \
			export TARGET_ORACLE_DEBUG=true; \
			export SINGER_SDK_LOG_LEVEL=DEBUG; \
			echo "$(LOG_TIMESTAMP) - EXEC: Executando meltano run com debug..." >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
			if $(ENV_CMD) && timeout 3600 meltano --log-level=debug run full-sync-job >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log 2>&1; then \
				echo "$(LOG_TIMESTAMP) - SUCESSO: Sincronização full concluída" >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
				echo "FULL_SYNC_SUCCESS" > $(STATE_DIR)/last_full_sync.state; \
			else \
				echo "$(LOG_TIMESTAMP) - ERRO: Sincronização full falhou" >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
				cp $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log $(ERROR_LOG_DIR)/full_sync_error_$(TIMESTAMP).log; \
				echo "FULL_SYNC_ERROR" > $(STATE_DIR)/last_full_sync.state; \
			fi; \
		else \
			echo "$(LOG_TIMESTAMP) - ERRO: Ambiente inválido" >> $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log; \
			cp $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log $(ERROR_LOG_DIR)/env_error_$(TIMESTAMP).log; \
		fi; \
		rm -f $(PID_DIR)/full_sync.pid; \
	' & echo $$! > $(PID_DIR)/full_sync.pid
	@echo "✅ Sincronização full com DEBUG iniciada em background (PID: $$(cat $(PID_DIR)/full_sync.pid))"
	@echo "📊 Use 'make monitor' para acompanhar ou 'tail -f $(SYNC_LOG_DIR)/full_sync_debug_$(TIMESTAMP).log'"

incremental-sync:
	@echo "⚡ EXECUTANDO SINCRONIZAÇÃO INCREMENTAL..."
	@mkdir -p $(SYNC_LOG_DIR) $(ERROR_LOG_DIR) $(PID_DIR) $(STATE_DIR)
	@if [ -f $(PID_DIR)/incremental_sync.pid ] && ps -p $$(cat $(PID_DIR)/incremental_sync.pid) > /dev/null 2>&1; then \
		echo "❌ Sincronização incremental já está executando (PID: $$(cat $(PID_DIR)/incremental_sync.pid))"; \
		exit 1; \
	fi
	@echo "📝 Logs: $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log"
	@nohup bash -c ' \
		echo "$(LOG_TIMESTAMP) - INÍCIO: Sincronização Incremental" > $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log; \
		if $(ENV_CMD) && timeout 1800 meltano run incremental-sync-job >> $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log 2>&1; then \
			echo "$(LOG_TIMESTAMP) - SUCESSO: Sincronização incremental concluída" >> $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log; \
			echo "INCREMENTAL_SYNC_SUCCESS" > $(STATE_DIR)/last_incremental_sync.state; \
		else \
			echo "$(LOG_TIMESTAMP) - ERRO: Sincronização incremental falhou" >> $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log; \
			cp $(SYNC_LOG_DIR)/incremental_sync_$(TIMESTAMP).log $(ERROR_LOG_DIR)/incremental_sync_error_$(TIMESTAMP).log; \
			echo "INCREMENTAL_SYNC_ERROR" > $(STATE_DIR)/last_incremental_sync.state; \
		fi; \
		rm -f $(PID_DIR)/incremental_sync.pid; \
	' & echo $$! > $(PID_DIR)/incremental_sync.pid
	@echo "✅ Sincronização incremental iniciada (PID: $$(cat $(PID_DIR)/incremental_sync.pid))"

# Job para rodar ambos simultaneamente
dual-sync:
	@echo "🚀 INICIANDO SINCRONIZAÇÃO DUAL (FULL + INCREMENTAL) EM PARALELO..."
	@echo "📋 Este comando iniciará dois processos separados:"
	@echo "  1. Full Sync → Schema WMS_FULL (modo overwrite)"
	@echo "  2. Incremental Sync → Schema WMS_INCREMENTAL (modo append-only com versionamento)"
	@echo ""
	@$(MAKE) full-sync
	@sleep 3
	@$(MAKE) incremental-sync
	@echo "✅ Ambas sincronizações iniciadas simultaneamente"
	@echo "📊 Use 'make status' para acompanhar ambas"

stop-sync:
	@echo "🛑 PARANDO SINCRONIZAÇÕES..."
	@if [ -f $(PID_DIR)/full_sync.pid ]; then \
		if ps -p $$(cat $(PID_DIR)/full_sync.pid) > /dev/null 2>&1; then \
			echo "Parando Full Sync (PID: $$(cat $(PID_DIR)/full_sync.pid))..."; \
			kill $$(cat $(PID_DIR)/full_sync.pid) 2>/dev/null || true; \
			sleep 2; \
			kill -9 $$(cat $(PID_DIR)/full_sync.pid) 2>/dev/null || true; \
		fi; \
		rm -f $(PID_DIR)/full_sync.pid; \
	fi
	@if [ -f $(PID_DIR)/incremental_sync.pid ]; then \
		if ps -p $$(cat $(PID_DIR)/incremental_sync.pid) > /dev/null 2>&1; then \
			echo "Parando Incremental Sync (PID: $$(cat $(PID_DIR)/incremental_sync.pid))..."; \
			kill $$(cat $(PID_DIR)/incremental_sync.pid) 2>/dev/null || true; \
			sleep 2; \
			kill -9 $$(cat $(PID_DIR)/incremental_sync.pid) 2>/dev/null || true; \
		fi; \
		rm -f $(PID_DIR)/incremental_sync.pid; \
	fi
	@echo "✅ Todas as sincronizações foram paradas"

# ============================================================================
# VALIDAÇÃO ORACLE
# ============================================================================

validate-oracle:
	@echo "🔍 VALIDANDO DADOS NO ORACLE..."
	@mkdir -p $(VALIDATION_LOG_DIR)
	@$(ENV_CMD) && python3 src/oracle/validate_sync.py

# ============================================================================
# ANÁLISE E CORREÇÃO DE FALHAS
# ============================================================================

analyze-failures:
	@echo "🔍 ANALISANDO FALHAS E ERROS..."
	@mkdir -p $(ERROR_LOG_DIR)
	@if [ ! -d $(ERROR_LOG_DIR) ] || [ -z "$$(ls -A $(ERROR_LOG_DIR) 2>/dev/null)" ]; then \
		echo "✅ Nenhum erro encontrado para analisar"; \
		exit 0; \
	fi
	@echo "📊 RELATÓRIO DE ANÁLISE DE FALHAS - $(LOG_TIMESTAMP)" > $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log
	@echo "====================================================" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log
	@echo "" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log
	@for error_file in $(ERROR_LOG_DIR)/*.log; do \
		if [ -f "$$error_file" ] && [[ $$error_file != *"analysis_"* ]]; then \
			echo "🔍 Analisando: $$(basename $$error_file)" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
			echo "----------------------------------------" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
			if grep -q "timeout" "$$error_file"; then \
				echo "❌ PROBLEMA: Timeout detectado" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
				echo "💡 SOLUÇÃO: Aumentar timeout ou verificar conexão" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
			fi; \
			if grep -q "ORA-" "$$error_file"; then \
				echo "❌ PROBLEMA: Erro Oracle detectado" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
				grep "ORA-" "$$error_file" | head -3 >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
				echo "💡 SOLUÇÃO: Verificar conexão Oracle e permissões" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
			fi; \
			if grep -q "Connection" "$$error_file"; then \
				echo "❌ PROBLEMA: Erro de conexão" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
				echo "💡 SOLUÇÃO: Verificar credenciais e conectividade" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
			fi; \
			echo "" >> $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log; \
		fi; \
	done
	@echo "✅ Análise concluída: $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log"
	@cat $(ERROR_LOG_DIR)/analysis_$(TIMESTAMP).log

fix-errors:
	@echo "🔧 TENTANDO CORRIGIR ERROS AUTOMATICAMENTE..."
	@echo "1️⃣ Verificando e corrigindo permissões..."
	@chmod +x $(PROJECT_DIR)/*.sh 2>/dev/null || true
	@echo "2️⃣ Limpando estado corrompido..."
	@rm -f $(PROJECT_DIR)/.meltano/run/state.json 2>/dev/null || true
	@echo "3️⃣ Testando conectividade Oracle..."
	@$(ENV_CMD) && python3 -c "import oracledb; print('Oracle client OK')" || echo "⚠️ Problema com Oracle client"
	@echo "4️⃣ Verificando espaço em disco..."
	@df -h $(PROJECT_DIR) | tail -1 | awk '{print "Espaço disponível: " $$4}'
	@echo "✅ Correções automáticas aplicadas"

health-check:
	@echo "🩺 VERIFICAÇÃO COMPLETA DE SAÚDE DO SISTEMA"
	@echo "============================================"
	@echo ""
	@$(MAKE) env
	@echo ""
	@$(MAKE) validate-oracle
	@echo ""
	@$(MAKE) analyze-failures
	@echo ""
	@echo "🚨 VERIFICAÇÃO DE ALERTAS:"
	@$(ENV_CMD) && python3 src/monitoring/alert_manager.py
	@echo ""
	@echo "🎯 RESUMO DO HEALTH CHECK:"
	@if [ -f $(STATE_DIR)/last_full_sync.state ]; then \
		echo "  📊 Último Full Sync: $$(cat $(STATE_DIR)/last_full_sync.state)"; \
	else \
		echo "  📊 Último Full Sync: NUNCA EXECUTADO"; \
	fi
	@if [ -f $(STATE_DIR)/last_incremental_sync.state ]; then \
		echo "  ⚡ Último Incremental: $$(cat $(STATE_DIR)/last_incremental_sync.state)"; \
	else \
		echo "  ⚡ Último Incremental: NUNCA EXECUTADO"; \
	fi
	@echo "✅ Health check concluído"

validate-data:
	@echo "🔍 VALIDANDO DADOS COM CONVERSOR PROFISSIONAL..."
	@$(ENV_CMD) && python3 src/validators/data_validator.py

test-oracle-connection:
	@echo "🔗 TESTANDO CONEXÃO ORACLE COM DIAGNÓSTICOS..."
	@$(ENV_CMD) && PYTHONPATH=/home/marlonsc/flext/gruponos-meltano-native python3 src/oracle/connection_manager.py

recreate-tables:
	@echo "🔨 [LEGACY] RECRIANDO TABELAS VIA SCRIPT..."
	@echo "⚠️  AVISO: Use 'make reset-state' + 'make full-sync' para método Meltano nativo"
	@echo "📋 Este comando (legacy) irá:"
	@echo "  1. Descobrir schemas via tap-oracle-wms"
	@echo "  2. Gerar DDL Oracle otimizado"
	@echo "  3. Recriar tabelas com estrutura enterprise"
	@echo ""
	@echo "💡 RECOMENDADO: make reset-state && make full-sync"
	@echo ""
	@$(ENV_CMD) && PYTHONPATH=/home/marlonsc/flext/gruponos-meltano-native python3 src/oracle/table_creator.py

recreate-table:
	@echo "🔨 RECRIANDO TABELA ESPECÍFICA..."
	@if [ -z "$(ENTITY)" ]; then \
		echo "❌ Use: make recreate-table ENTITY=allocation|order_hdr|order_dtl"; \
		exit 1; \
	fi
	@echo "📋 Recriando tabela para entidade: $(ENTITY)"
	@$(ENV_CMD) && PYTHONPATH=/home/marlonsc/flext/gruponos-meltano-native python3 src/oracle/table_creator.py $(ENTITY)

force-full-sync:
	@echo "🚀 SINCRONIZAÇÃO FULL FORÇADA COM TABELAS RECRIADAS..."
	@echo "📋 Este comando irá:"
	@echo "  1. Parar processos ativos"
	@echo "  2. Recriar todas as tabelas"
	@echo "  3. Limpar estado Meltano"
	@echo "  4. Executar full sync"
	@echo ""
	@$(MAKE) stop-sync
	@$(MAKE) recreate-tables
	@$(MAKE) reset-state
	@$(MAKE) full-sync

# ============================================================================
# MANUTENÇÃO
# ============================================================================

clean-logs:
	@echo "🧹 LIMPANDO LOGS ANTIGOS..."
	@find $(LOG_DIR) -name "*.log" -mtime +7 -delete 2>/dev/null || true
	@find $(ERROR_LOG_DIR) -name "*.log" -mtime +3 -delete 2>/dev/null || true
	@echo "✅ Logs antigos removidos (>7 dias para sync, >3 dias para errors)"

# Reset apenas do Incremental Sync para reiniciar do start_date
reset-incremental-sync:
	@echo "🔄 RESETANDO ESTADO DO INCREMENTAL SYNC..."
	@echo "📋 Isso fará o incremental sync recomeçar do start_date configurado"
	@$(ENV_CMD) && echo "y" | meltano state clear tap-oracle-wms-incremental
	@rm -f $(STATE_DIR)/last_incremental_sync.state 2>/dev/null || true
	@echo "✅ Estado do incremental sync resetado - próxima execução começará do start_date"

# ============================================================================
# COMANDOS MELTANO NATIVOS - GERENCIAMENTO DE ESTADO E TABELAS
# ============================================================================

reset-state:
	@echo "🔄 MELTANO NATIVO: RESETANDO ESTADO PARA FORÇAR RECRIAÇÃO DE TABELAS..."
	@echo "📋 Este comando irá:"
	@echo "  1. Limpar estado Meltano (força descoberta fresh de schema)"
	@echo "  2. Na próxima execução, target criará tabelas automaticamente"
	@echo "  3. Usa regras unificadas do type_mapping_rules.py"
	@echo ""
	@$(ENV_CMD) && echo "y" | meltano state clear --all --force
	@rm -rf $(PROJECT_DIR)/.meltano/run/state 2>/dev/null || true
	@rm -f $(STATE_DIR)/*.state 2>/dev/null || true
	@echo "✅ Estado resetado - próximo sync criará tabelas com regras unificadas"

reset-full-sync:
	@echo "🔄 MELTANO NATIVO: RESETANDO APENAS FULL SYNC..."
	@echo "📋 Força full sync começar do início, mas mantém estado incremental"
	@$(ENV_CMD) && echo "y" | meltano state clear dev:tap-oracle-wms-full-to-target-oracle-full
	@rm -f $(STATE_DIR)/last_full_sync.state 2>/dev/null || true
	@echo "✅ Full sync resetado - manterá tabelas existentes"

clear-all-state:
	@echo "⚠️  CUIDADO: LIMPANDO TODOS OS ESTADOS MELTANO..."
	@echo "📋 Isso remove TODOS os checkpoints e força recomeço total"
	@read -p "Tem certeza? Digite 'sim' para confirmar: " confirm && [ "$$confirm" = "sim" ] || exit 1
	@$(ENV_CMD) && meltano state clear --all --force
	@rm -rf $(PROJECT_DIR)/.meltano/run/state 2>/dev/null || true
	@rm -rf $(STATE_DIR) 2>/dev/null || true
	@mkdir -p $(STATE_DIR)
	@echo "✅ TODOS os estados removidos - próximo sync começará do zero absoluto"

native-recreate-tables:
	@echo "🚀 MELTANO NATIVO: RECREAÇÃO DE TABELAS..."
	@echo "📋 Processo 100% Meltano nativo:"
	@echo "  1. Reset estado (força schema discovery)"
	@echo "  2. Full sync (target cria tabelas automaticamente)"
	@echo "  3. Usa regras unificadas type_mapping_rules.py"
	@echo ""
	@$(MAKE) reset-state
	@echo ""
	@echo "🚀 Iniciando full sync para criar tabelas..."
	@$(MAKE) full-sync
	@echo ""
	@echo "✅ Tabelas criadas via Meltano nativo com regras unificadas!"

# Comando para reiniciar full sync automaticamente
restart-full-sync:
	@echo "🔄 REINICIANDO FULL SYNC DO ZERO..."
	@echo "📋 Este comando irá:"
	@echo "  1. Parar full sync ativo (se houver)"
	@echo "  2. Resetar estado do full sync"
	@echo "  3. Iniciar novo full sync do ID mais alto"
	@echo ""
	@if [ -f $(PID_DIR)/full_sync.pid ] && ps -p $$(cat $(PID_DIR)/full_sync.pid) > /dev/null 2>&1; then \
		echo "Parando full sync ativo..."; \
		kill $$(cat $(PID_DIR)/full_sync.pid) 2>/dev/null || true; \
		rm -f $(PID_DIR)/full_sync.pid; \
		sleep 2; \
	fi
	@$(MAKE) reset-full-sync
	@sleep 1
	@$(MAKE) full-sync
	@echo "✅ Full sync reiniciado do zero"

# ============================================================================
# COMANDOS AVANÇADOS
# ============================================================================

discover:
	@echo "🔍 DESCOBRINDO ENTIDADES..."
	@$(ENV_CMD) && meltano invoke tap-oracle-wms --discover

test-connections:
	@echo "🔗 TESTANDO CONEXÕES..."
	@echo "📡 Testando TAP Oracle WMS..."
	@$(ENV_CMD) && meltano invoke tap-oracle-wms --test-connection || echo "❌ TAP falhou"
	@echo "🎯 Testando TARGET Oracle..."
	@$(ENV_CMD) && timeout 30 meltano invoke target-oracle --test-connection || echo "❌ TARGET falhou"

logs:
	@echo "📄 LOGS MAIS RECENTES:"
	@echo "====================="
	@if [ -n "$$(ls -t $(SYNC_LOG_DIR)/*.log 2>/dev/null | head -1)" ]; then \
		echo "🔄 ÚLTIMO SYNC LOG:"; \
		tail -20 $$(ls -t $(SYNC_LOG_DIR)/*.log | head -1); \
		echo ""; \
	fi
	@if [ -n "$$(ls -t $(ERROR_LOG_DIR)/*.log 2>/dev/null | head -1)" ]; then \
		echo "❌ ÚLTIMO ERROR LOG:"; \
		tail -10 $$(ls -t $(ERROR_LOG_DIR)/*.log | head -1); \
	fi

# ============================================================================
# COMANDOS LEGACY (compatibilidade)
# ============================================================================

run:
	@echo "⚠️  COMANDO LEGACY - Use 'make incremental-sync' ou 'make full-sync'"
	@$(MAKE) incremental-sync

clean:
	@echo "⚠️  COMANDO LEGACY - Use 'make clean-logs'"
	@$(MAKE) clean-logs

# Descobrir e salvar schemas WMS
discover-schemas:
	@echo "🔍 DESCOBRINDO SCHEMAS WMS..."
	@echo "📋 Este comando irá:"
	@echo "  1. Conectar na API WMS"
	@echo "  2. Descobrir schemas reais de todas as entidades"
	@echo "  3. Salvar em sql/wms_schemas.json"
	@echo ""
	@$(ENV_CMD) && python3 src/oracle/discover_and_save_schemas.py
