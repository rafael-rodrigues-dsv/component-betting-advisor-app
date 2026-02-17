"""
Cache Manager - Gerenciamento de cache.

ATUALIZADO: Agora usa SQLite para persistência.
"""

# Re-exporta o SQLiteCacheManager como padrão
from infrastructure.cache.sqlite_cache_manager import SQLiteCacheManager, get_cache

__all__ = ['SQLiteCacheManager', 'get_cache']


