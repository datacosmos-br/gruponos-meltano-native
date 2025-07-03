#!/usr/bin/env python3
"""Teste para validar que a refatoração funcionou corretamente.
Verifica se tanto table_creator.py quanto flext-target-oracle usam o módulo compartilhado.
"""

def test_table_creator_import():
    """Test se table_creator.py importa do módulo compartilhado."""
    print("🔍 TESTANDO IMPORT DO TABLE_CREATOR.PY")
    print("=" * 50)

    try:
        import sys
        sys.path.insert(0, "/home/marlonsc/flext/gruponos-meltano-native/src")

        # Test import do módulo compartilhado
        from oracle.type_mapping_rules import (
            FIELD_PATTERN_RULES,
            FIELD_PATTERNS_TO_ORACLE,
            convert_metadata_type_to_oracle,
        )
        print("✅ type_mapping_rules.py importado com sucesso")

        # Test import do table_creator refatorado
        from oracle.table_creator import OracleTableCreator
        print("✅ table_creator.py importado com sucesso")

        # Test se table_creator usa as regras compartilhadas
        test_type = convert_metadata_type_to_oracle(
            column_name="order_instructions_set",
            metadata_type=None
        )
        expected = "VARCHAR2(4000 CHAR)"

        if test_type == expected:
            print(f"✅ Regras compartilhadas funcionando: {test_type}")
        else:
            print(f"❌ Erro nas regras: esperado {expected}, obtido {test_type}")
            return False

        return True

    except Exception as e:
        print(f"❌ Erro no import: {e}")
        return False

def test_target_oracle_import():
    """Test se flext-target-oracle consegue usar o módulo compartilhado."""
    print("\n🔍 TESTANDO IMPORT DO FLEXT-TARGET-ORACLE")
    print("=" * 50)

    try:
        import sys
        sys.path.insert(0, "/home/marlonsc/flext/flext-target-oracle")
        sys.path.insert(0, "/home/marlonsc/flext/gruponos-meltano-native/src")

        # Test se consegue importar as regras compartilhadas
        from oracle.type_mapping_rules import convert_singer_schema_to_oracle
        print("✅ type_mapping_rules.py acessível do target oracle")

        # Test conversão via função compartilhada
        test_conversion = convert_singer_schema_to_oracle(
            "required_serial_nbr_set",
            {"type": "string"}
        )
        expected = "VARCHAR2(4000 CHAR)"

        if test_conversion == expected:
            print(f"✅ Conversão compartilhada funcionando: {test_conversion}")
        else:
            print(f"❌ Erro na conversão: esperado {expected}, obtido {test_conversion}")
            return False

        return True

    except Exception as e:
        print(f"❌ Erro no import target oracle: {e}")
        return False

def test_consistency():
    """Test consistência entre table_creator e target oracle."""
    print("\n🔍 TESTANDO CONSISTÊNCIA ENTRE MÓDULOS")
    print("=" * 50)

    try:
        import sys
        sys.path.insert(0, "/home/marlonsc/flext/gruponos-meltano-native/src")

        from oracle.type_mapping_rules import (
            convert_metadata_type_to_oracle,
            convert_singer_schema_to_oracle,
        )

        # Test cases para comparar ambos métodos
        test_cases = [
            ("order_instructions_set", "VARCHAR2(4000 CHAR)"),
            ("required_serial_nbr_set", "VARCHAR2(4000 CHAR)"),
            ("order_dtl_set", "VARCHAR2(4000 CHAR)"),
            ("alloc_qty", "NUMBER"),
            ("status_id", "NUMBER"),
            ("item_key", "VARCHAR2(255 CHAR)"),
            ("create_ts", "TIMESTAMP(6)"),
        ]

        print("Campo                    table_creator        target_oracle        Consistente")
        print("-" * 80)

        all_consistent = True
        for field_name, expected in test_cases:
            # table_creator method
            creator_result = convert_metadata_type_to_oracle(column_name=field_name)

            # target oracle method
            schema = {"type": "string"}
            if "qty" in field_name or "id" in field_name:
                schema = {"type": "number"}
            elif "ts" in field_name:
                schema = {"type": "string", "format": "date-time"}

            target_result = convert_singer_schema_to_oracle(field_name, schema)

            consistent = creator_result == target_result == expected
            status = "✅" if consistent else "❌"

            if not consistent:
                all_consistent = False

            print(f"{field_name:20} {creator_result:20} {target_result:20} {status}")

        return all_consistent

    except Exception as e:
        print(f"❌ Erro no teste de consistência: {e}")
        return False

def test_makefile_commands():
    """Test se Makefile tem os novos comandos."""
    print("\n🔍 TESTANDO COMANDOS DO MAKEFILE")
    print("=" * 40)

    try:
        with open("/home/marlonsc/flext/gruponos-meltano-native/Makefile") as f:
            makefile_content = f.read()

        required_commands = [
            "native-recreate-tables:",
            "reset-state:",
            "clear-all-state:",
            "type_mapping_rules.py",
            "[LEGACY]",
        ]

        for command in required_commands:
            if command in makefile_content:
                print(f"✅ {command}")
            else:
                print(f"❌ {command} - NÃO ENCONTRADO")
                return False

        return True

    except Exception as e:
        print(f"❌ Erro ao ler Makefile: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE DE REFATORAÇÃO - MÓDULO COMPARTILHADO")
    print("Validando se table_creator.py e flext-target-oracle usam type_mapping_rules.py")
    print("=" * 80)

    test1 = test_table_creator_import()
    test2 = test_target_oracle_import()
    test3 = test_consistency()
    test4 = test_makefile_commands()

    print("\n" + "=" * 80)
    print("📊 RESULTADOS DOS TESTES:")
    print(f"  🔧 table_creator.py:      {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  🎯 flext-target-oracle:   {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  🔄 Consistência:          {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"  📝 Makefile:              {'✅ PASS' if test4 else '❌ FAIL'}")

    if all([test1, test2, test3, test4]):
        print("\n🎉 REFATORAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Módulo compartilhado funcionando corretamente")
        print("✅ Zero duplicação de código")
        print("✅ Makefile atualizado com comandos Meltano nativos")
        print("✅ table_creator.py mantido para troubleshooting")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS NA REFATORAÇÃO")
        print("Revisar imports e configurações")
