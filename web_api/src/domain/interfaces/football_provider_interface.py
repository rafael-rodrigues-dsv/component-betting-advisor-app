from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date
class FootballProviderInterface(ABC):
    """Interface abstrata para providers de dados de futebol"""
    @abstractmethod
    async def get_fixtures(self, league_id: int, fixture_date: date) -> List[Dict[str, Any]]:
        """Busca fixtures de uma liga em uma data"""
        pass
    @abstractmethod
    async def get_odds(self, fixture_id: int) -> Dict[str, Any]:
        """Busca odds de um fixture"""
        pass
    @abstractmethod
    async def get_leagues(self) -> List[Dict[str, Any]]:
        """Lista ligas disponíveis"""
        pass
