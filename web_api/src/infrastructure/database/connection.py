"""
Database Connection - Gerenciamento de conexão SQLite para tickets.

Usa SQLite puro (sem ORM) para simplicidade.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Gerenciador de conexão com SQLite.

    Responsável por:
    - Criar conexão com banco
    - Inicializar tabelas
    - Fornecer contexto de transação
    """

    def __init__(self, db_path: str = None):
        # Define caminho padrão: web_api/data/tickets.db
        if db_path is None:
            current_file = Path(__file__)
            web_api_root = current_file.parent.parent.parent.parent
            db_path = str(web_api_root / "data" / "tickets.db")

        self.db_path = db_path

        # Cria diretório se não existir
        try:
            data_dir = Path(db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Pasta de dados verificada: {data_dir}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar pasta de dados: {e}")
            raise

        logger.info(f"📦 DatabaseConnection inicializado: {db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Retorna uma nova conexão com o banco.

        Returns:
            Conexão SQLite
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn

    def init_tables(self):
        """
        Cria tabelas se não existirem.

        Tabelas:
        - tickets: Bilhetes de apostas
        - bets: Apostas individuais (foreign key para tickets)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela de tickets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                stake REAL NOT NULL,
                bookmaker_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de bets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                match_id TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                league TEXT NOT NULL,
                market TEXT NOT NULL,
                predicted_outcome TEXT NOT NULL,
                odds REAL NOT NULL,
                confidence REAL NOT NULL,
                result TEXT,
                final_score TEXT,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
            )
        """)

        # Índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_status 
            ON tickets(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_created_at 
            ON tickets(created_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bets_ticket_id 
            ON bets(ticket_id)
        """)

        conn.commit()
        conn.close()

        logger.info("✅ Tabelas de tickets criadas")


# Instância global (singleton)
_db_instance: Optional[DatabaseConnection] = None


def get_database() -> DatabaseConnection:
    """
    Retorna instância global do banco (singleton).

    Returns:
        DatabaseConnection instance
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.init_tables()

    return _db_instance

