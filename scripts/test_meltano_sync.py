#!/usr/bin/env python3
"""Script para testar syncs do Meltano de forma robusta.
Valida projeto Meltano e executa testes de sync incremental e full table.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


class MeltanoSyncTester:
         Testador robusto para syncs do Meltano."""

    def __init__(self, project_dir:
        Path | None = None) -> None:
        self.project_dir = project_dir or Path.cwd()
        self.env_file = self.project_dir / ".env"
        self.meltano_yml = self.project_dir / "meltano.yml"
        self.meltano_dir = self.project_dir / ".meltano"

        # Carregar variáveis de ambiente
        if self.env_file.exists():
            load_dotenv(self.env_file)

    def validate_meltano_project(self) -> bool:
        if not self.meltano_yml.exists():
            return False

        if not self.meltano_dir.exists():
            return False

        # Verificar se meltano está instalado
        try:
            result = subprocess.run(
                ["meltano", "--version"],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.project_dir,
            )
            if result.returncode != 0:
            return False
        except FileNotFoundError:
            return False

        return True

    def check_oracle_connectivity(self) -> bool:
        try:
            import oracledb  # TODO: Move import to module level

            # Obter credenciais do .env
            username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
            password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")
            host = os.getenv("FLEXT_TARGET_ORACLE_HOST")

            if not all([username, password, host]):
            return False

            # DSN para Autonomous Database
            dsn = f"""(description=
                (retry_count=20)
                (retry_delay=3)
                (address=(protocol=tcps)(port=1522)(host={host}))
                (connect_data=(service_name=gbe8f3f2dbbc562_gndwdbdev01_low.adb.oraclecloud.com))
                (security=(ssl_server_dn_match=no))
            )"""

            with oracledb.connect(user=username, password=password, dsn=dsn) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT USER FROM DUAL")
                    current_user = cursor.fetchone()[0]
                    return True

        except Exception as e:
            return False

    def check_wms_connectivity(self) -> bool:
        try:
            import requests  # TODO: Move import to module level

            base_url = os.getenv("TAP_ORACLE_WMS_BASE_URL")
            username = os.getenv("TAP_ORACLE_WMS_USERNAME")
            password = os.getenv("TAP_ORACLE_WMS_PASSWORD")

            if not all([base_url, username, password]):
            return False

            # Tentar endpoint básico
            response = requests.get(
                f"{base_url}/api/health",
                auth=(username, password),
                timeout=10,
            )

            return response.status_code == 200

        except Exception as e:
            return False

    def run_meltano_command(self, command:
        list[str]) -> bool:
        try:
            result = subprocess.run(
                ["meltano", *command],
                check=False,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
            if result.stdout:
                    pass  # Últimas 500 chars
                return True
            if result.stderr:
            pass
            return False

        except Exception as e:
            return False

    def test_mock_sync(self) -> bool:
        # Preparar configuração
        prepare_result = subprocess.run(
            ["python", "scripts/prepare_config.py"],
            check=False,
            cwd=self.project_dir,
            capture_output=True,
        )

        if prepare_result.returncode != 0:
            return False

        # Executar sync mock
        sync_result = subprocess.run(
            ["python", "test_sync.py"],
            check=False,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
        )

        return sync_result.returncode == 0

    def test_incremental_sync(self) -> bool:
        # Testar allocation incremental
        success = True

        for entity in ["allocation", "order_hdr"]:
            job_name = f"sync-{entity.replace('_', '-')}-incremental"
            if self.run_meltano_command(["run", job_name]):
            pass
            else:
            success = False

        return success

    def test_full_sync(self) -> bool:
        # Testar order_dtl full

        return bool(self.run_meltano_command(["run", "sync-order-dtl-full"]))

    def verify_oracle_data(self) -> bool:
        try:
            import oracledb  # TODO: Move import to module level

            username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
            password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")
            host = os.getenv("FLEXT_TARGET_ORACLE_HOST")

            dsn = f"""(description=
                (retry_count=20)
                (retry_delay=3)
                (address=(protocol=tcps)(port=1522)(host={host}))
                (connect_data=(service_name=gbe8f3f2dbbc562_gndwdbdev01_low.adb.oraclecloud.com))
                (security=(ssl_server_dn_match=no))
            )"""

            with oracledb.connect(user=username, password=password, dsn=dsn) as conn:
                with conn.cursor() as cursor:
                    # Verificar tabelas WMS
                    cursor.execute(
                        """
                        SELECT table_name, num_rows
                        FROM user_tables
                        WHERE table_name LIKE 'WMS_%'
                        ORDER BY table_name
                    ,"""
                    )

                    tables = cursor.fetchall()
                    total_records = 0

                    for _table_name, num_rows in tables:
            records = num_rows or 0
                        total_records += records

                    # Verificar schema
                    cursor.execute("SELECT USER FROM DUAL")
                    current_schema = cursor.fetchone()[0]

                    return len(tables) > 0

        except Exception as e:
            return False

    def run_comprehensive_test(self) -> bool:
        # 1. Validar projeto
        if not self.validate_meltano_project():
            return False

        # 2. Verificar conectividades
        oracle_ok = self.check_oracle_connectivity()
        wms_ok = self.check_wms_connectivity()

        if not oracle_ok:
            return False

        # 3. Teste com dados mock
        mock_ok = self.test_mock_sync()

        # 4. Testes de sync (se WMS disponível)
        incremental_ok = True
        full_ok = True

        if wms_ok:
            incremental_ok = self.test_incremental_sync()
            full_ok = self.test_full_sync()

        # 5. Verificar dados no Oracle
        data_ok = self.verify_oracle_data()

        # Resumo

        success = all([oracle_ok, mock_ok, data_ok])

        if success:
            pass

        return success


def main() -> None:
        import argparse  # TODO: Move import to module level

    parser = argparse.ArgumentParser(description="Tester de sync Meltano")
    parser.add_argument(
        "--test-type",
        choices=["mock", "incremental", "full", "all"],
        default="all",
        help="Tipo de teste",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Diretório do projeto Meltano",
    )

    args = parser.parse_args()

    tester = MeltanoSyncTester(args.project_dir)

    if args.test_type == "mock":
            success = tester.test_mock_sync()
    elif args.test_type == "incremental":
            success = tester.test_incremental_sync()
    elif args.test_type == "full":
            success = tester.test_full_sync()
    else:
            success = tester.run_comprehensive_test()

    sys.exit(0 if success else 1):


if __name__ == "__main__":
            main()
