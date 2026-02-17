"""
Logo Type Enum - Tipo da origem do logo
"""

from enum import Enum


class LogoType(Enum):
    """Tipo de origem do logo do time"""

    LOCAL = "LOCAL"
    """Logo armazenado localmente em /static/escudos/"""

    EXTERNAL = "EXTERNAL"
    """Logo externo (URL do provider)"""

