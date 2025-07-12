# FLEXT Operations Guide

## FLEXT Workspace Context

**Location**: `/home/marlonsc/flext/gruponos-meltano-native/`
**Shared Environment**: `/home/marlonsc/flext/.venv`
**Coordination**: Check `.token` file before operations

## FLEXT Pipeline Commands

### Core ETL Operations (FLEXT Singer Protocol)
```bash
# Full sync using FLEXT TAP/TARGET components
meltano run tap-oracle-wms-full target-oracle-full

# Incremental sync with FLEXT state management
meltano run tap-oracle-wms-incremental target-oracle-incremental

# Pre-configured FLEXT jobs
meltano job run full-sync-job
meltano job run incremental-sync-job
```

### FLEXT Validation & Monitoring
```bash
# Oracle validation with FLEXT observability
python validate_oracle_data.py

# Advanced validation using FLEXT connection patterns
PYTHONPATH=/home/marlonsc/flext/gruponos-meltano-native python src/oracle/validate_sync.py

# FLEXT Singer state inspection
meltano state list

# FLEXT structured logging
meltano logs
```

### FLEXT Component Testing
```bash
# Test FLEXT TAP component
meltano invoke tap-oracle-wms-full --test

# Test FLEXT TARGET component
meltano invoke target-oracle-full --test

# Debug with FLEXT observability
meltano --log-level=debug run tap-oracle-wms-full target-oracle-full
```

## Troubleshooting Comum

### Problema: Erro de conexão Oracle
**Sintoma**: `DPY-4011: the database or network closed the connection`
**Solução**:
1. Verificar variáveis de ambiente no .env
2. Testar conectividade de rede: `ping <oracle_host>`
3. Validar certificados SSL/TCPS

### Problema: Pipeline falha com timeout
**Sintoma**: Pipeline para de responder
**Solução**:
1. Aumentar `request_timeout` no meltano.yml
2. Reduzir `batch_size` para processar menos dados por vez
3. Verificar carga no servidor Oracle

### Problema: Dados não aparecem no Oracle
**Sintoma**: Pipeline executa mas tabelas vazias
**Solução**:
1. Executar `python validate_oracle_data.py`
2. Verificar esquema OIC no Oracle
3. Confirmar prefixo de tabelas (WMS_)

### Problema: Erros de tipo de dados
**Sintoma**: `'540' is not of type 'number'`
**Solução**:
1. Verificar configuração do data_validator
2. Executar com `--log-level=debug` para mais detalhes

## Configurações de Performance

### Ajustar Volume de Dados
```yaml
# meltano.yml - seção config do tap
page_size: 500          # Reduzir se houver timeouts
batch_size: 1000        # Ajustar conforme capacidade
request_timeout: 600    # Aumentar para operações longas
```

### Otimizar Conexões Oracle
```bash
# .env - configurações de conexão
FLEXT_TARGET_ORACLE_TIMEOUT=60
FLEXT_TARGET_ORACLE_RETRIES=3
FLEXT_TARGET_ORACLE_RETRY_DELAY=5
```

## Monitoramento de Performance

### Métricas Típicas
- **Extração**: ~1.250 registros por entidade
- **Carregamento**: ~3.750 registros totais
- **Tempo total**: 3-5 minutos
- **Tabelas criadas**: WMS_ALLOCATION, WMS_ORDER_HDR, WMS_ORDER_DTL

### Verificar Performance
```bash
# Contar registros por tabela
python validate_oracle_data.py

# Verificar timestamps de execução
meltano logs | grep -E "(Started|Completed)"

# Monitorar uso de recursos
top -p $(pgrep -f meltano)
```

## Manutenção

### Limpeza Periódica
```bash
# Limpar logs antigos
meltano logs --clear

# Limpar estado (resetar incremental)
meltano state clear tap-oracle-wms-full

# Limpar tabelas de teste (opcional)
python clean_and_test.py
```

### Backup de Configuração
```bash
# Backup essencial
cp .env .env.backup
cp meltano.yml meltano.yml.backup
cp pyproject.toml pyproject.toml.backup
```

## Cenários de Uso

### Carga Inicial (Setup)
1. Configurar .env com credenciais
2. Executar `meltano run tap-oracle-wms-full target-oracle-full`
3. Validar com `python validate_oracle_data.py`

### Operação Diária
1. Executar `meltano run tap-oracle-wms-incremental target-oracle-incremental`
2. Verificar logs para erros
3. Monitorar performance

### Recuperação de Falhas
1. Verificar logs: `meltano logs`
2. Limpar estado se necessário: `meltano state clear`
3. Re-executar pipeline
4. Validar dados carregados