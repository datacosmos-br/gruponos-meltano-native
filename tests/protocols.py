"""Test protocol definitions for gruponos-meltano-native.

Provides TestsGruponosMeltanoNativeProtocols, combining FlextTestsProtocols with
GruponosMeltanoNativeProtocols for test-specific protocol definitions.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from flext_tests.protocols import FlextTestsProtocols

from gruponos_meltano_native.protocols import GruponosMeltanoNativeProtocols


class TestsGruponosMeltanoNativeProtocols(
    FlextTestsProtocols, GruponosMeltanoNativeProtocols
):
    """Test protocols combining FlextTestsProtocols and GruponosMeltanoNativeProtocols.

    Provides access to:
    - tp.Tests.Docker.* (from FlextTestsProtocols)
    - tp.Tests.Factory.* (from FlextTestsProtocols)
    - tp.GruponosMeltanoNative.* (from GruponosMeltanoNativeProtocols)
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with GruponosMeltanoNative-specific protocols.
        """

        class GruponosMeltanoNative:
            """GruponosMeltanoNative-specific test protocols."""


# Runtime aliases
p = TestsGruponosMeltanoNativeProtocols
tp = TestsGruponosMeltanoNativeProtocols

__all__ = ["TestsGruponosMeltanoNativeProtocols", "p", "tp"]
