"""
Preload Service - Pré-carregamento de fixtures das ligas principais.

Executado automaticamente no startup do FastAPI (1x por dia).

ATUALIZADO: Usa APIFootballService conforme arquitetura.
"""

from datetime import date, timedelta
from typing import List
import logging

from infrastructure.cache.cache_manager import get_cache
from infrastructure.external.api_football.service import APIFootballService
from domain.constants.constants import MAIN_LEAGUES

logger = logging.getLogger(__name__)


class PreloadService:
    """
    Serviço de pré-carregamento de dados.

    Busca fixtures das ligas principais ao iniciar o backend,
    apenas se não houver carga do dia atual.

    Dados mockados mas realistas são gerados e cacheados em memória.
    """


    def __init__(self):
        self.cache = get_cache()
        self.api_service = APIFootballService()
        self.last_preload_date = None

    def _get_week_dates(self) -> List[date]:
        """
        Retorna lista de datas desde hoje até o próximo domingo (mínimo 7 dias).

        Se hoje é domingo, vai até o próximo domingo.

        Returns:
            Lista de dates (hoje + próximos dias até domingo)
        """
        today = date.today()
        dates = [today]

        # Adiciona dias até completar pelo menos 1 semana OU até domingo
        current = today
        days_added = 0
        max_days = 7  # Garante pelo menos 1 semana

        while days_added < max_days or current.weekday() != 6:  # 6 = Domingo
            current += timedelta(days=1)
            dates.append(current)
            days_added += 1

            # Limite de segurança (máximo 14 dias)
            if days_added >= 14:
                break

        return dates

    async def has_todays_cache(self) -> bool:
        """
        Verifica se já tem cache de fixtures do dia atual.

        Returns:
            True se já tiver carga de hoje, False caso contrário
        """
        # Verifica se tem pelo menos uma liga cacheada de hoje
        today = date.today()
        cache_key = f"preload:last_date"

        last_date = self.cache.get(cache_key)

        if last_date and last_date == today.isoformat():
            logger.info(f"✅ Cache de hoje ({today}) encontrado")
            return True

        logger.info(f"❌ Cache de hoje não encontrado (last: {last_date})")
        return False

    async def preload_fixtures(self, league_ids: List[int]):
        """
        Pré-carrega fixtures de múltiplas ligas para a semana completa.

        PRO PLAN: Carrega hoje até domingo (até 7 dias).

        Distribuição realista:
        - Ligas nacionais: Sábado, Domingo e Segunda
        - Copa do Brasil: Quarta e Quinta

        Args:
            league_ids: Lista de IDs das ligas
        """
        dates = self._get_week_dates()
        total_days = len(dates)

        logger.info(f"🚀 Iniciando pré-carregamento de {len(league_ids)} ligas × {total_days} dias...")
        logger.info(f"📅 Período: {dates[0]} até {dates[-1]} ({total_days} dias)")
        logger.info(f"📆 Datas carregadas: {[d.isoformat() for d in dates]}")

        total_fixtures = 0
        total_odds = 0

        for league_id in league_ids:
            league_fixtures = 0
            try:
                for fixture_date in dates:
                    # Sempre tenta gerar - scenarios.py verifica match_days do JSON
                    fixtures_count = await self.preload_league(league_id, fixture_date)
                    total_fixtures += fixtures_count
                    total_odds += fixtures_count  # 1 odd por fixture
                    league_fixtures += fixtures_count

                logger.info(f"  ✅ Liga {league_id}: {league_fixtures} fixtures carregados")
            except Exception as e:
                logger.error(f"  ❌ Erro ao pré-carregar liga {league_id}: {e}")

        # Marca data do pré-carregamento
        self.cache.set("preload:last_date", date.today().isoformat())

        logger.info(f"✅ Pré-carregamento concluído!")
        logger.info(f"📊 Total: {total_fixtures} fixtures + {total_odds} odds carregados")
        logger.info(f"💾 Cache em memória pronto para uso")


    async def preload_league(self, league_id: int, fixture_date: date) -> int:
        """
        Pré-carrega fixtures de uma liga específica.

        Args:
            league_id: ID da liga
            fixture_date: Data dos fixtures

        Returns:
            Número de fixtures carregados
        """
        logger.debug(f"  📥 Buscando fixtures: Liga {league_id} - {fixture_date}")

        # Busca fixtures via APIFootballService (já cacheia automaticamente)
        fixtures = await self.api_service.get_fixtures(league_id, fixture_date)

        if not fixtures:
            logger.debug(f"  ⚠️ Nenhum fixture para liga {league_id} em {fixture_date}")
            return 0

        # Para cada fixture, busca odds (já cacheia automaticamente)
        for fixture in fixtures:
            fixture_id = int(fixture["id"])
            await self.api_service.get_odds(fixture_id)

        logger.debug(f"  💾 {len(fixtures)} fixtures + odds salvos no cache")

        return len(fixtures)

    async def preload_main_leagues(self):
        """
        Pré-carrega as ligas principais configuradas.

        Atalho para pré-carregar MAIN_LEAGUES.
        """
        await self.preload_fixtures(MAIN_LEAGUES)



