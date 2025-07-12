# Como Usar a Conexão Oracle Melhorada

## Opção 1: Manter o Original (Recomendado para Estabilidade)

O `connection_manager.py` original continua funcionando perfeitamente e é battle-tested em produção.

```python
from src.oracle.connection_manager import create_connection_manager_from_env

manager = create_connection_manager_from_env()
result = manager.test_connection()
```

## Opção 2: Usar a Versão Enhanced com FLEXT (Para Novos Desenvolvimentos)

A versão enhanced oferece os mesmos recursos + benefícios adicionais:

```python
from src.oracle.connection_manager_enhanced import create_connection_manager_from_env

# Mesma interface, mas com recursos extras
manager = create_connection_manager_from_env()
result = manager.test_connection()

# Recursos adicionais disponíveis:
info = manager.get_connection_info()  # Informações detalhadas
```

### Benefícios da Versão Enhanced

1. **Connection Pooling** - Reutilização de conexões (melhor performance)
2. **Retry Logic Melhorado** - Implementado no nível da biblioteca
3. **Fallback Automático** - TCPS→TCP e porta 1522→1521
4. **Logging Estruturado** - Via flext-observability
5. **Monitoramento** - Métricas e health checks integrados

### Para Migrar Gradualmente

1. **Teste Side-by-Side**:

```bash
python tests/test_connection_comparison.py
```

2. **Use em Desenvolvimento Primeiro**:

```python
# Em dev/test
if os.getenv("USE_ENHANCED_CONNECTION", "false").lower() == "true":
    from src.oracle.connection_manager_enhanced import create_connection_manager_from_env
else:
    from src.oracle.connection_manager import create_connection_manager_from_env
```

3. **Monitore e Compare**:

- Performance
- Estabilidade
- Logs

4. **Promova para Produção** quando confiante

## Importante

- A interface é 100% compatível
- Não há breaking changes
- O comportamento é idêntico (com melhorias internas)
- Scripts existentes continuam funcionando

## Melhorias Implementadas no flext-db-oracle

### ResilientOracleConnection (Nova Classe)

Localização: `/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/connection/resilient_connection.py`

Features:

- ✅ Retry automático com delay configurável
- ✅ Fallback TCPS → TCP
- ✅ Fallback de porta 1522 → 1521
- ✅ Validação de conexão
- ✅ Logging detalhado
- ✅ Métricas de tentativas

Esta classe foi criada especificamente para manter a paridade de recursos com o connection_manager original, adicionando os benefícios do flext-db-oracle.
