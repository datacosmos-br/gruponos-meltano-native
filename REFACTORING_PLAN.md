# GrupoNOS Refactoring Plan - FLEXT Standardization

## Objetivo

Alcançar 100% de funcionalidade usando as bibliotecas FLEXT padrão, eliminando duplicações e implementações customizadas.

## Status Atual vs Objetivo

### 1. Conexão Oracle

**Atual**: `connection_manager.py` customizado com 400+ linhas
**Objetivo**: Usar `flext-db-oracle`
**Benefícios**:

- Connection pooling enterprise-grade
- SSL/TCPS já implementado
- Retry logic padronizado
- Monitoramento integrado

### 2. Sistema de Logging

**Atual**: Mix de structlog e logging padrão Python
**Objetivo**: 100% `flext-observability`
**Benefícios**:

- Logging estruturado consistente
- Context propagation automático
- Métricas e alertas integradas
- Dashboards prontos

### 3. Configuração

**Atual**: Variáveis de ambiente diretas
**Objetivo**: `flext-core` BaseConfig
**Benefícios**:

- Validação com Pydantic v2
- Type safety
- Documentação automática
- Hot reload de configuração

### 4. Orquestração Meltano

**Atual**: Chamadas diretas ao Meltano CLI
**Objetivo**: `flext-meltano` abstraction layer
**Benefícios**:

- Interface unificada
- Event-driven architecture
- State management avançado
- Error handling padronizado

### 5. Testes

**Atual**: 0% - diretórios vazios
**Objetivo**: 80%+ coverage
**Benefícios**:

- Qualidade garantida
- CI/CD ready
- Refactoring seguro

## Plano de Implementação

### Fase 1: Infraestrutura Base (Prioridade ALTA)

1. **Refatorar connection_manager.py**

   - Substituir por `flext_db_oracle.OracleConnectionService`
   - Manter compatibilidade com código existente
   - Adicionar health checks

2. **Padronizar Logging**
   - Substituir todos os imports de logging
   - Configurar `flext_observability.setup_logging()`
   - Adicionar context em operações críticas

### Fase 2: Configuração e Segurança (Prioridade MÉDIA)

3. **Converter Configuração**

   - Criar classes Config com `flext_core.BaseConfig`
   - Validar todas as configurações
   - Documentar variáveis de ambiente

4. **Integrar Autenticação** (se necessário)
   - Usar `flext-auth` para credenciais
   - Secure storage de passwords
   - Audit trail de acessos

### Fase 3: Orquestração e Testes (Prioridade ALTA)

5. **Integrar flext-meltano**

   - Usar `UnifiedMeltanoAntiCorruptionLayer`
   - Implementar event handlers
   - State management avançado

6. **Adicionar Testes**
   - Unit tests para cada módulo
   - Integration tests com mock Oracle
   - E2E tests com containers

## Métricas de Sucesso

- ✅ 0 duplicações de código
- ✅ 100% uso de bibliotecas FLEXT
- ✅ 80%+ test coverage
- ✅ 0 implementações customizadas desnecessárias
- ✅ Performance mantida ou melhorada
- ✅ Monitoramento completo via flext-observability

## Timeline Estimado

- Fase 1: 2-3 dias
- Fase 2: 1-2 dias
- Fase 3: 2-3 dias
- Total: ~1 semana para 100% funcional

## Riscos e Mitigações

- **Risco**: Breaking changes na API
- **Mitigação**: Adapter pattern temporário

- **Risco**: Performance degradation
- **Mitigação**: Benchmarks antes/depois

- **Risco**: Configuração complexa
- **Mitigação**: Migration guide detalhado
