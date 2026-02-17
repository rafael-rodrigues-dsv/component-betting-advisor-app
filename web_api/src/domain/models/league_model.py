"""
League Model - Representa uma liga/competição
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class League:
    """Liga/Competição de futebol"""

    id: str
    """ID único da liga"""

    name: str
    """Nome da liga (ex: "Brasileirão Série A")"""

    country: str
    """País da liga"""

    logo: Optional[str] = None
    """URL do logo da liga"""

    flag: Optional[str] = None
    """URL da bandeira do país"""

    season: Optional[int] = None
    """Temporada atual"""

    type: Optional[str] = None
    """Tipo: League, Cup"""

