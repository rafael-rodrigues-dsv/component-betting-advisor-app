"""
Team Model - Representa um time de futebol
"""

from dataclasses import dataclass
from typing import Optional
from domain.models.logo_model import Logo
import re


@dataclass
class Team:
    """Time de futebol"""

    id: str
    """ID único do time"""

    name: str
    """Nome do time"""

    logo: Logo
    """Logo do time (local ou externo)"""

    country: Optional[str] = None
    """País do time"""

    def slug(self) -> str:
        """
        Gera slug para buscar logo local.

        Exemplos:
        - "Flamengo" → "flamengo.png"
        - "São Paulo" → "sao-paulo.png"
        - "Atlético-MG" → "atletico-mg.png"
        """
        slug = self.name.lower()

        # Remove acentos
        slug = re.sub(r'[àáâãäå]', 'a', slug)
        slug = re.sub(r'[èéêë]', 'e', slug)
        slug = re.sub(r'[ìíîï]', 'i', slug)
        slug = re.sub(r'[òóôõö]', 'o', slug)
        slug = re.sub(r'[ùúûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)

        # Substitui caracteres especiais por -
        slug = re.sub(r'[^a-z0-9-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')

        return f"{slug}.png"

