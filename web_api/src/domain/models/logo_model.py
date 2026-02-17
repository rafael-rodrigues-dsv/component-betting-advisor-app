"""
Logo Model - Representa o logo de um time
"""

from dataclasses import dataclass
from domain.enums.logo_type_enum import LogoType


@dataclass
class Logo:
    """
    Logo de um time.

    Usa estratégia de fallback: Local First → External Fallback
    """
    url: str
    """URL ou caminho relativo do logo"""

    type: LogoType
    """LOCAL (static/escudos/) ou EXTERNAL (provider)"""

    @staticmethod
    def local(filename: str) -> 'Logo':
        """Cria logo local"""
        return Logo(
            url=f"http://localhost:8000/static/escudos/{filename}",
            type=LogoType.LOCAL
        )

    @staticmethod
    def external(url: str) -> 'Logo':
        """Cria logo externo (provider)"""
        return Logo(
            url=url,
            type=LogoType.EXTERNAL
        )

