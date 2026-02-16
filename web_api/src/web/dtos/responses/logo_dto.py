"""
DTOs para Logo (Escudos/Imagens)
"""
from pydantic import BaseModel, Field
from enum import Enum


class LogoTypeEnum(str, Enum):
    """Tipo de logo"""
    LOCAL = "LOCAL"  # Arquivo estático local (web_api/static/escudos/)
    EXT = "EXT"      # URL externa (internet)


class LogoDTO(BaseModel):
    """DTO para logo de time/liga"""
    url: str = Field(..., description="URL do logo (pode ser relativa ou absoleta)")
    type: LogoTypeEnum = Field(..., description="Tipo do logo: LOCAL ou EXT")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "url": "/static/escudos/flamengo.png",
                    "type": "LOCAL"
                },
                {
                    "url": "https://media.api-sports.io/football/teams/123.png",
                    "type": "EXT"
                }
            ]
        }

    def get_full_url(self, base_url: str = "http://localhost:8000") -> str:
        """
        Retorna URL completa baseada no tipo

        Args:
            base_url: URL base do backend (para tipo LOCAL)

        Returns:
            URL completa do logo
        """
        if self.type == LogoTypeEnum.EXT:
            return self.url

        # LOCAL: monta URL completa
        if self.url.startswith('http'):
            return self.url

        return f"{base_url}{self.url}"

