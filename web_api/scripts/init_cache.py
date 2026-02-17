"""
Init Cache - Inicializa o banco de dados de cache.

Este script é chamado automaticamente pela main.py no startup.
Cria as tabelas do SQLite de cache se ainda não existirem.

NÃO é um sistema de migrations, apenas inicialização.
"""

import sys
from pathlib import Path

# Adiciona src/ ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.cache.sqlite_cache_manager import get_cache_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_cache():
    """
    Inicializa o banco de dados de cache.

    - Cria pasta data/ se não existir
    - Cria arquivo cache.db se não existir
    - Cria tabelas (cache) se não existirem
    - Cria índices para performance

    É IDEMPOTENTE: pode ser executado múltiplas vezes sem problemas.
    """
    logger.info("🔧 Inicializando banco de cache...")

    try:
        # Obtém instância do cache manager (cria se não existir)
        cache = get_cache_manager()

        # Inicializa tabelas (cria se não existirem)
        cache.init_tables()

        logger.info("✅ Banco de cache inicializado com sucesso!")
        logger.info(f"📁 Localização: {cache.db_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cache: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    """Permite executar diretamente: python scripts/init_cache.py"""
    success = init_cache()
    sys.exit(0 if success else 1)

