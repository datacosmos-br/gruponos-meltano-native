# Changelog

## [1.0.0] - 2025-07-12

### Pipeline ETL Operacional
- ✅ Oracle WMS → Oracle Analytics funcionando
- ✅ 3.750 registros processados com sucesso
- ✅ Tempo execução: <5 minutos

### Componentes Implementados
- **flext-tap-oracle-wms**: Extrator Oracle WMS via HTTPS
- **flext-target-oracle**: Carregador Oracle via TCPS/SSL  
- **meltano**: Orquestração com jobs configurados
- **flext-observability**: Logging estruturado

### Entidades Sincronizadas
- `allocation`: 1.250 registros
- `order_hdr`: 1.250 registros
- `order_dtl`: 1.250 registros

### Tabelas Oracle Criadas
- `OIC.WMS_ALLOCATION`
- `OIC.WMS_ORDER_HDR`
- `OIC.WMS_ORDER_DTL`

### Scripts de Validação
- `validate_oracle_data.py`: Validação principal
- `src/oracle/validate_sync.py`: Validação detalhada

### Configuração
- `meltano.yml`: Pipeline completo configurado
- `.env.example`: Template variáveis ambiente
- Jobs: full-sync-job, incremental-sync-job

### Documentação
- `README.md`: Setup e comandos principais
- `OPERATIONS.md`: Guia operacional detalhado
- `ARCHITECTURE.md`: Documentação técnica
- `CHANGELOG.md`: Histórico de mudanças

### Correções Aplicadas
- Removidos fallbacks de conexão Oracle
- Removidos fallbacks de conversão de dados
- Eliminadas duplicações de logging
- Corrigida documentação inflada
- Padronizado uso de flext-observability

### Performance Verificada
- Volume: 3.750 registros processados
- Tempo: 3-5 minutos execução completa
- Conexões: Oracle TCPS/SSL estáveis
- Zero timeouts ou falhas conexão