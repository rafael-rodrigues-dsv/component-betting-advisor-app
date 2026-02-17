"""
Init Database - Inicializa o banco de dados.

Este script é chamado automaticamente pela main.py no startup.
Cria as tabelas do SQLite se ainda não existirem.

NÃO é um sistema de migrations, apenas inicialização.
"""

import sys
from pathlib import Path

# Adiciona src/ ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.database.connection import get_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """
    Inicializa o banco de dados.

    - Cria pasta data/ se não existir
    - Cria arquivo tickets.db se não existir
    - Cria tabelas (tickets, bets) se não existirem
    - Cria índices para performance

    É IDEMPOTENTE: pode ser executado múltiplas vezes sem problemas.
    """
    logger.info("🔧 Inicializando banco de dados...")

    try:
        # Obtém instância do banco (cria se não existir)
        db = get_database()

        # Inicializa tabelas (cria se não existirem)
        db.init_tables()

        logger.info("✅ Banco de dados inicializado com sucesso!")
        logger.info(f"📁 Localização: {db.db_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
        return False


if __name__ == "__main__":
    """Permite executar diretamente: python scripts/init_database.py"""
    success = init_database()
    sys.exit(0 if success else 1)

