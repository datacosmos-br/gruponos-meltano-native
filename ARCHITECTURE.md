# FLEXT Architecture Documentation

## FLEXT Ecosystem Integration

Enterprise data pipeline using FLEXT Singer/Meltano components within the FLEXT workspace ecosystem.

## FLEXT Components Architecture

### 1. FLEXT Singer TAP (flext-tap-oracle-wms)
- **FLEXT Module**: `/home/marlonsc/flext/flext-tap-oracle-wms/`
- **Protocol**: HTTPS REST API with FLEXT patterns
- **Singer Spec**: Full Singer protocol compliance
- **Configuration**: FLEXT environment variable namespacing

### 2. FLEXT Singer TARGET (flext-target-oracle)
- **FLEXT Module**: `/home/marlonsc/flext/flext-target-oracle/`
- **Connection**: FLEXT Oracle connection pooling patterns
- **Schema**: Automatic table creation with FLEXT standards
- **Metadata**: Singer metadata with FLEXT observability

### 3. FLEXT Orchestration (Meltano + FLEXT patterns)
- **Framework**: Meltano with FLEXT integration patterns
- **State**: FLEXT Singer state management
- **Logging**: flext-observability structured logging
- **Coordination**: FLEXT workspace `.token` coordination

## FLEXT Data Flow Pattern

```
1. FLEXT TAP discovers WMS entity schemas (FLEXT discovery patterns)
2. FLEXT TAP extracts data via HTTPS API (FLEXT connection patterns)
3. FLEXT TAP sends Singer messages (SCHEMA, RECORD, STATE) 
4. FLEXT TARGET receives Singer protocol messages
5. FLEXT TARGET creates Oracle tables (FLEXT Oracle patterns)
6. FLEXT TARGET inserts data with Singer metadata (FLEXT observability)
7. FLEXT observability logs all operations (structured logging)
```

## FLEXT Integration Patterns

### FLEXT Singer Protocol Implementation
- **Message Flow**: SCHEMA → RECORD → STATE (Singer specification)
- **State Management**: Incremental sync with FLEXT state persistence
- **Error Handling**: FLEXT error patterns with structured logging
- **Metadata**: Singer metadata injection with FLEXT standards

## Mensagens Singer

### SCHEMA
Define estrutura das tabelas Oracle:
```json
{
  "type": "SCHEMA",
  "stream": "allocation",
  "schema": {
    "properties": {
      "id": {"type": "integer"},
      "mod_ts": {"type": "string", "format": "date-time"}
    }
  }
}
```

### RECORD
Dados extraídos do WMS:
```json
{
  "type": "RECORD", 
  "stream": "allocation",
  "record": {
    "id": 12345,
    "mod_ts": "2025-07-12T10:00:00Z"
  }
}
```

### STATE
Controle incremental:
```json
{
  "type": "STATE",
  "value": {
    "allocation": {
      "replication_key_value": "2025-07-12T10:00:00Z"
    }
  }
}
```

## Mapeamento de Tipos

### WMS API → Oracle
- `string` → `VARCHAR2(4000)`
- `integer` → `NUMBER(38)`
- `number` → `NUMBER(38,10)` 
- `boolean` → `NUMBER(1)`
- `date-time` → `TIMESTAMP`

### Metadata Singer
- `_SDC_EXTRACTED_AT` → `TIMESTAMP` (quando extraído)
- `_SDC_BATCHED_AT` → `TIMESTAMP` (quando processado)
- `_SDC_RECEIVED_AT` → `TIMESTAMP` (quando recebido)

## Performance

### Configurações Críticas
```yaml
# meltano.yml
tap-oracle-wms-full:
  config:
    page_size: 500          # Registros por requisição API
    request_timeout: 600    # Timeout HTTP (segundos)
    ordering: "-id"         # Ordenação para paginação

target-oracle-full:
  config:
    batch_size: 1000        # Registros por batch Oracle
    max_parallelism: 5      # Threads paralelas
```

### Otimizações
- **Paginação**: API WMS usa cursor-based pagination
- **Batching**: TARGET processa em lotes para eficiência
- **Conexão**: Pool de conexões Oracle reutilizadas
- **Estado**: Incremental via replication_key (mod_ts)

## Tabelas Oracle

### Naming Convention
- Prefixo: `WMS_` (configurável)
- Schema: `OIC` (configurável)
- Exemplo: `OIC.WMS_ALLOCATION`

### Estrutura Padrão
```sql
CREATE TABLE "OIC"."WMS_ALLOCATION" (
  "ID" NUMBER(38) NOT NULL,
  "MOD_TS" TIMESTAMP,
  -- ... campos da entidade WMS
  "_SDC_EXTRACTED_AT" TIMESTAMP,
  "_SDC_BATCHED_AT" TIMESTAMP, 
  "_SDC_RECEIVED_AT" TIMESTAMP
);
```

## Configuração Incremental

### Replication Key
- Campo: `mod_ts` (modification timestamp)
- Tipo: `timestamp`
- Estratégia: Extrai registros com mod_ts > último valor

### Estado Persistido
- Armazenamento: Meltano system database
- Formato: JSON com último valor por stream
- Recuperação: Automática em caso de falha

## Monitoramento

### Logs Estruturados
- **flext-observability**: Logging padronizado
- **Níveis**: DEBUG, INFO, WARNING, ERROR
- **Contexto**: run_id, stream, timestamp

### Métricas Disponíveis
- Registros extraídos por stream
- Tempo de execução total
- Erros de conexão/timeout
- Performance de batches

## Dependências

### Core
- `meltano` - Orquestração
- `flext-tap-oracle-wms` - Extrator
- `flext-target-oracle` - Carregador
- `oracledb` - Driver Oracle Python

### Auxiliares  
- `flext-observability` - Logging
- `pydantic` - Validação configuração
- `requests` - HTTP client
- `singer-sdk` - Singer protocol

## Segurança

### Credenciais
- Variáveis de ambiente (.env)
- Não commitadas no git
- Criptografia TLS/SSL para todas conexões

### Conexões Oracle
- Protocolo TCPS (TLS)
- Certificados validados
- Configuração ssl_server_dn_match

### API WMS
- HTTPS obrigatório
- Basic Authentication
- Timeouts configurados