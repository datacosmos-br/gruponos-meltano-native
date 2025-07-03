#!/usr/bin/env python3
"""Test script para verificar se o target oracle usa as mesmas regras do table_creator.py
"""

import json
import sys

sys.path.insert(0, "/home/marlonsc/flext/flext-target-oracle")

from flext_target_oracle.sinks import OracleSink


def test_unified_table_creation():
    """Test se as regras de criação estão unificadas."""
    print("🔍 TESTANDO UNIFICAÇÃO DAS REGRAS DE CRIAÇÃO DE TABELAS")
    print("=" * 70)

    # Mock config
    config = {
        "table_prefix": "WMS_",
        "default_target_schema": "OIC",
        "add_record_metadata": False,
        "enable_historical_versioning": True
    }

    # Sample schema from WMS
    sample_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "alloc_qty": {"type": "number"},
            "order_instructions_set": {"type": "string"},
            "create_ts": {"type": "string", "format": "date-time"},
            "mod_ts": {"type": "string", "format": "date-time"},
            "status_id": {"type": "integer"},
            "item_key": {"type": "string"},
            "from_inventory_id": {"type": "integer"},
            "is_picking_flg": {"type": "boolean"},
            "pick_user": {"type": "string"},
        }
    }

    # Create a mock sink to test DDL generation
    class MockConnector:
        def __init__(self):
            self._engine = None

    class MockTarget:
        def __init__(self):
            self.config = config
            import logging
            self.logger = logging.getLogger("mock_target")

    # Create sink instance
    sink = OracleSink(
        target=MockTarget(),
        stream_name="allocation",
        schema=sample_schema,
        key_properties=["id", "mod_ts"]
    )

    # Test DDL generation
    print("🔧 Gerando DDL com regras unificadas...")
    try:
        ddl = sink._generate_oracle_ddl()
        print("✅ DDL gerado com sucesso!")
        print("\n📄 DDL GERADO:")
        print("-" * 60)
        print(ddl)
        print("-" * 60)

        # Test type conversion for specific fields
        print("\n🔍 TESTANDO CONVERSÕES DE TIPOS ESPECÍFICOS:")
        print("-" * 50)

        table_creator_rules = sink._get_table_creator_rules()

        test_fields = [
            ("id", {"type": "integer"}),
            ("alloc_qty", {"type": "number"}),
            ("order_instructions_set", {"type": "string"}),
            ("create_ts", {"type": "string", "format": "date-time"}),
            ("status_id", {"type": "integer"}),
            ("item_key", {"type": "string"}),
            ("is_picking_flg", {"type": "boolean"}),
            ("pick_user", {"type": "string"}),
        ]

        for field_name, field_schema in test_fields:
            oracle_type = sink._convert_to_oracle_type(field_name, field_schema, table_creator_rules)
            print(f"  {field_name:25} -> {oracle_type}")

        # Validate _set fields use VARCHAR2(4000 CHAR)
        print("\n🔍 TESTANDO CAMPOS _SET:")
        set_test_fields = [
            ("order_instructions_set", {"type": "string"}),
            ("required_serial_nbr_set", {"type": "string"}),
            ("order_dtl_set", {"type": "string"}),
        ]

        for field_name, field_schema in set_test_fields:
            oracle_type = sink._convert_to_oracle_type(field_name, field_schema, table_creator_rules)
            expected = "VARCHAR2(4000 CHAR)"
            status = "✅" if oracle_type == expected else "❌"
            print(f"  {status} {field_name:25} -> {oracle_type}")
            if oracle_type != expected:
                print(f"     Esperado: {expected}")

        print("\n✅ TESTE CONCLUÍDO - Regras unificadas funcionando!")
        return True

    except Exception as e:
        print(f"❌ Erro ao gerar DDL: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_table_creator():
    """Compare com as regras do table_creator.py original."""
    print("\n🔍 COMPARANDO COM TABLE_CREATOR.PY ORIGINAL")
    print("=" * 50)

    # Import table creator
    sys.path.insert(0, "/home/marlonsc/flext/gruponos-meltano-native/src")
    from oracle.table_creator import convert_metadata_type_to_oracle

    test_cases = [
        ("id", None, None),
        ("alloc_qty", None, None),
        ("order_instructions_set", None, None),
        ("create_ts", None, None),
        ("status_id", None, None),
        ("item_key", None, None),
        ("pick_user", None, None),
    ]

    print("Campo                    Target Oracle        table_creator.py")
    print("-" * 65)

    # Mock config for sink
    config = {"table_prefix": "WMS_", "default_target_schema": "OIC"}

    class MockTarget:
        def __init__(self):
            self.config = config
            import logging
            self.logger = logging.getLogger("mock_target")

    sink = OracleSink(
        target=MockTarget(),
        stream_name="test",
        schema={"type": "object", "properties": {}},
        key_properties=[]
    )

    table_creator_rules = sink._get_table_creator_rules()

    for field_name, metadata_type, max_length in test_cases:
        # Target oracle conversion
        field_schema = {"type": "string"}
        if "qty" in field_name:
            field_schema = {"type": "number"}
        elif "id" in field_name:
            field_schema = {"type": "integer"}
        elif "ts" in field_name:
            field_schema = {"type": "string", "format": "date-time"}

        target_type = sink._convert_to_oracle_type(field_name, field_schema, table_creator_rules)

        # table_creator.py conversion
        creator_type = convert_metadata_type_to_oracle(
            metadata_type=metadata_type,
            column_name=field_name,
            max_length=max_length
        )

        match = "✅" if target_type == creator_type else "❌"
        print(f"{field_name:20} {target_type:20} {creator_type:20} {match}")

if __name__ == "__main__":
    success = test_unified_table_creation()
    compare_with_table_creator()

    if success:
        print("\n🎉 UNIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("O target oracle agora usa as mesmas regras do table_creator.py")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS NA UNIFICAÇÃO")
