"""
Settings - Configurações centralizadas do sistema usando Pydantic.

Carrega variáveis do arquivo .env e fornece valores padrão seguros.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional
from datetime import datetime, date as date_type
from zoneinfo import ZoneInfo



class Settings(BaseSettings):
    """
    Configurações do sistema.

    Carrega automaticamente de .env se existir, caso contrário usa valores padrão.

    OBRIGATÓRIO:
    - API_FOOTBALL_KEY: Chave da API-Football

    Para produção: copie .env.production e adicione API key real
    """

    # API-Football
    API_FOOTBALL_KEY: Optional[str] = None
    """Chave da API-Football (obrigatória)"""

    API_FOOTBALL_BASE_URL: str = "https://v3.football.api-sports.io"
    """URL base da API-Football"""

    # Cache TTLs (em segundos)
    CACHE_TTL_FIXTURES: int = 21600  # 6 horas
    """TTL para fixtures no cache"""

    CACHE_TTL_ODDS: int = 1800  # 30 minutos
    """TTL para odds no cache"""

    CACHE_TTL_LEAGUES: int = 604800  # 7 dias
    """TTL para ligas no cache"""

    # Database
    DATABASE_PATH: str = "data/cache.db"
    """Caminho do banco SQLite de cache"""

    TICKETS_DATABASE_PATH: str = "data/tickets.db"
    """Caminho do banco SQLite de tickets"""

    # Servidor
    HOST: str = "0.0.0.0"
    """Host do servidor"""

    PORT: int = 8000
    """Porta do servidor"""

    DEBUG: bool = False
    """Modo debug"""

    # CORS (string simples - será parseada quando necessário)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    """Origens permitidas para CORS (separadas por vírgula)"""

    # Ligas principais (string simples - será parseada quando necessário)
    MAIN_LEAGUES: str = "71,73,39,140,78,61,135"
    """IDs das ligas principais (separados por vírgula)"""

    # Casas de apostas suportadas (string simples - será parseada quando necessário)
    SUPPORTED_BOOKMAKERS: str = "bet365,betano"
    """IDs das casas de apostas suportadas (separados por vírgula)"""

    # Timezone do sistema (padrão: America/Sao_Paulo)
    TIMEZONE: str = "America/Sao_Paulo"
    """Timezone usada para calcular 'hoje' e períodos de datas"""

    @property
    def cors_origins_list(self):
        """Retorna CORS_ORIGINS como lista"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]

    @property
    def main_leagues_list(self):
        """Retorna MAIN_LEAGUES como lista de inteiros"""
        return [int(league_id.strip()) for league_id in self.MAIN_LEAGUES.split(',') if league_id.strip()]

    @property
    def supported_bookmakers_set(self):
        """Retorna SUPPORTED_BOOKMAKERS como set de strings"""
        return {b.strip() for b in self.SUPPORTED_BOOKMAKERS.split(',') if b.strip()}

    @property
    def tz(self) -> ZoneInfo:
        """Retorna o objeto timezone configurado."""
        return ZoneInfo(self.TIMEZONE)

    def today(self) -> date_type:
        """Retorna a data de 'hoje' na timezone configurada."""
        return datetime.now(self.tz).date()

    def now(self) -> datetime:
        """Retorna data/hora atual na timezone configurada."""
        return datetime.now(self.tz)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Instância global (singleton)
settings = Settings()

