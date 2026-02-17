"""
SQLite Cache Manager - Cache persistente com banco de dados.

Substitui o cache em memória por um cache persistente usando SQLite.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SQLiteCacheManager:
    """
    Gerenciador de cache persistente com SQLite.

    - Cache sobrevive a reinicializações
    - TTL automático
    - Limpeza de expirados
    """

    def __init__(self, db_path: str = None):
        # Define caminho padrão: web_api/data/cache.db
        if db_path is None:
            # Obtém caminho da pasta web_api (2 níveis acima de src/)
            current_file = Path(__file__)  # .../src/infrastructure/cache/sqlite_cache_manager.py
            web_api_root = current_file.parent.parent.parent.parent  # .../web_api/
            db_path = str(web_api_root / "data" / "cache.db")

        self.db_path = db_path

        # Cria diretório se não existir
        try:
            data_dir = Path(db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Pasta de dados verificada: {data_dir}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar pasta de dados: {e}")
            raise

        logger.info(f"📦 SQLiteCacheManager inicializado: {db_path}")

    def init_tables(self):
        """
        Cria tabelas de cache se não existirem.

        Chamado explicitamente pelo script init_cache.py no startup.
        É IDEMPOTENTE: pode ser executado múltiplas vezes.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabela principal de cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índice para otimizar busca por expiração
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON cache(expires_at)
            """)

            conn.commit()
            conn.close()

            logger.info("✅ Tabelas de cache criadas/verificadas")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de cache: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """
        Busca valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor cacheado ou None se não existir/expirado
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
            (key, datetime.now())
        )

        result = cursor.fetchone()
        conn.close()

        if result:
            logger.debug(f"✅ Cache HIT: {key}")
            return json.loads(result[0])
        else:
            logger.debug(f"❌ Cache MISS: {key}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 21600) -> None:
        """
        Salva valor no cache.

        Args:
            key: Chave do cache
            value: Valor a ser cacheado
            ttl_seconds: Tempo de vida em segundos (padrão: 6 horas)
        """
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), expires_at)
        )

        conn.commit()
        conn.close()

        logger.debug(f"💾 Cache SET: {key} (TTL: {ttl_seconds}s)")

    def has(self, key: str) -> bool:
        """
        Verifica se chave existe no cache (e não expirou).

        Args:
            key: Chave do cache

        Returns:
            True se existe e válido, False caso contrário
        """
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Remove uma chave do cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))

        conn.commit()
        conn.close()

        logger.debug(f"🗑️ Cache DELETE: {key}")

    def clear(self) -> None:
        """Limpa todo o cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache")

        conn.commit()
        conn.close()

        logger.info("🗑️ Cache limpo completamente")

    def clear_expired(self) -> int:
        """
        Remove entradas expiradas.

        Returns:
            Número de entradas removidas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM cache WHERE expires_at < ?",
            (datetime.now(),)
        )

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted > 0:
            logger.info(f"🗑️ {deleted} entradas expiradas removidas")

        return deleted

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache.

        Returns:
            Dicionário com estatísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total de chaves
        cursor.execute("SELECT COUNT(*) FROM cache")
        total_keys = cursor.fetchone()[0]

        # Chaves expiradas
        cursor.execute(
            "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
            (datetime.now(),)
        )
        expired_keys = cursor.fetchone()[0]

        conn.close()

        return {
            "total_keys": total_keys,
            "valid_keys": total_keys - expired_keys,
            "expired_keys": expired_keys
        }


# Instância global do cache (singleton)
_cache_instance: Optional[SQLiteCacheManager] = None


def get_cache() -> SQLiteCacheManager:
    """
    Retorna instância global do cache (singleton).

    Returns:
        SQLiteCacheManager instance
    """
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = SQLiteCacheManager()

    return _cache_instance


def get_cache_manager() -> SQLiteCacheManager:
    """
    Alias para get_cache().

    Usado pelo script init_cache.py para manter consistência
    com get_database() do módulo database.

    Returns:
        SQLiteCacheManager instance
    """
    return get_cache()


