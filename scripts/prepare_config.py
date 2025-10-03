#!/usr/bin/env python3
"""Prepara configurações do Meltano substituindo variáveis de ambiente.

Centraliza todas as configurações em um lugar usando arquivos .env.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from flext_core import FlextTypes


def substitute_env_vars(
    config_dict: FlextTypes.Dict,
    env_vars: FlextTypes.StringDict,
) -> FlextTypes.Dict:
    """Substitui variáveis de ambiente na configuração."""
    result: FlextTypes.Dict = {}
    for key, value in config_dict.items():
        if isinstance(value, dict):
            result[key] = substitute_env_vars(value, env_vars)
        elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            # Formato ${VAR_NAME}
            var_name = value[2:-1]
            result[key] = env_vars.get(var_name, value)
        elif isinstance(value, str) and value.startswith("$"):
            # Formato $VAR_NAME
            var_name = value[1:]
            result[key] = env_vars.get(var_name, value)
        else:
            result[key] = value
    return result


def _load_config_template() -> FlextTypes.Dict:
    """Load configuration template from file or use default."""
    template_file = Path("target_config.json")
    if template_file.exists():
        with template_file.open(encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    # Fallback para template básico se arquivo não existir
    return {
        "username": "${FLEXT_TARGET_ORACLE_USERNAME}",
        "password": "${FLEXT_TARGET_ORACLE_PASSWORD}",
        "host": "${FLEXT_TARGET_ORACLE_HOST}",
        "port": "${FLEXT_TARGET_ORACLE_PORT}",
        "service_name": "${FLEXT_TARGET_ORACLE_SERVICE_NAME}",
        "protocol": "${FLEXT_TARGET_ORACLE_PROTOCOL}",
        "batch_size": "${FLEXT_TARGET_ORACLE_BATCH_SIZE}",
        "pool_size": "${FLEXT_TARGET_ORACLE_POOL_SIZE}",
        "load_method": "append-only",
    }


def _generate_autonomous_dsn(
    resolved_config: FlextTypes.Dict,
) -> FlextTypes.Dict:
    """Generate DSN for Autonomous Database if configuration allows."""
    if not all(key in resolved_config for key in ["host", "port", "service_name"]):
        return resolved_config
    host = resolved_config["host"]
    port = resolved_config["port"]
    service_name = resolved_config["service_name"]
    protocol = resolved_config.get("protocol", "tcps")
    if protocol == "tcps":
        autonomous_dsn = f"""(description=
    (retry_count=20)
    (retry_delay=3)
    (address=(protocol=tcps)(port={port})(host={host}))
    (connect_data=(service_name={service_name}))
    (security=(ssl_server_dn_match=no))
)"""
        resolved_config["dsn"] = autonomous_dsn
        # Remove campos individuais quando usando DSN
        for key in ["host", "port", "service_name", "protocol"]:
            resolved_config.pop(key, None)
    return resolved_config


def prepare_target_config(env_file: str = ".env") -> None:
    """Prepara configuração do target Oracle."""
    # Carrega variáveis de ambiente
    load_dotenv(env_file)
    env_vars = dict(os.environ)
    # Lê template de configuração
    target_config_template = _load_config_template()
    # Substitui variáveis
    resolved_config = substitute_env_vars(target_config_template, env_vars)
    # Gerar DSN para Autonomous Database
    resolved_config = _generate_autonomous_dsn(resolved_config)
    # Implementa lógica padrão do Oracle: schema = username quando não especificado
    if "schema" not in resolved_config or not resolved_config.get("schema"):
        username = resolved_config.get("username")
        if username:
            pass
            # Não adicionamos o campo schema - deixamos o target Oracle usar o padrão
    # Converte tipos conforme necessário
    for field, default_value in [("port", 1521), ("batch_size", 500), ("pool_size", 1)]:
        if field in resolved_config:
            try:
                value = resolved_config[field]
                if isinstance(value, (str, int, float)):
                    resolved_config[field] = int(value)
                else:
                    resolved_config[field] = default_value
            except (ValueError, TypeError):
                resolved_config[field] = default_value
    # Converte booleanos
    for field in ["ssl_server_dn_match", "add_record_metadata", "validate_records"]:
        if field in resolved_config:
            value = resolved_config[field]
            if isinstance(value, str):
                resolved_config[field] = value.lower() in {"true", "1", "yes", "on"}
    # Salva configuração resolvida
    output_file = Path("target_config_resolved.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(resolved_config, f, indent=2)
    # Mostra resumo
    if "dsn" in resolved_config:
        pass


def main() -> int:
    """Função principal."""
    parser = argparse.ArgumentParser(description="Prepara configurações do Meltano")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Arquivo de variáveis de ambiente (padrão: .env)",
    )
    args = parser.parse_args()
    try:
        prepare_target_config(args.env_file)
    except (FileNotFoundError, ValueError, KeyError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
