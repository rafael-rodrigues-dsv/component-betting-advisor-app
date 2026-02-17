from abc import ABC, abstractmethod
from typing import Dict, Any
class OddsProviderInterface(ABC):
    """Interface abstrata para providers de odds"""
    @abstractmethod
    async def get_odds_for_fixture(self, fixture_id: int) -> Dict[str, Any]:
        """Busca odds de um fixture específico"""
        pass
    @abstractmethod
    async def get_odds_for_fixtures(self, fixture_ids: list) -> Dict[int, Dict[str, Any]]:
        """Busca odds de múltiplos fixtures"""
        pass
