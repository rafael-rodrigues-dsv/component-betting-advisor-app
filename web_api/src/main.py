"""
Betting Advisor API - Backend Mockado
"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from web.controllers.match_controller import router as match_router
from web.controllers.prediction_controller import router as prediction_router
from web.controllers.ticket_controller import router as ticket_router
from web.controllers.preload_controller import router as preload_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Betting Advisor API",
    description="API para análise e sugestão de apostas esportivas (MOCK)",
    version="1.0.0"
)

# Configurar diretório de arquivos estáticos
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Montar arquivos estáticos (escudos dos times)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(match_router, prefix="/api/v1", tags=["Matches"])
app.include_router(prediction_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(ticket_router, prefix="/api/v1", tags=["Tickets"])
app.include_router(preload_router, prefix="/api/v1", tags=["Preload"])


@app.on_event("startup")
async def startup_event():
    """
    Evento executado ao iniciar o backend.

    1. Cria pasta data/ se não existir
    2. Inicializa banco de dados (cria tabelas se não existirem)
    3. Pré-carrega fixtures das ligas principais (1x por dia)
    """
    logger.info("🚀 Betting Advisor API iniciando...")

    # 0. Cria pasta data/ proativamente
    try:
        from pathlib import Path
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Pasta de dados pronta: {data_dir}")
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta data/: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # 1. Inicializa banco de dados
    try:
        from infrastructure.database.connection import get_database

        logger.info("🔧 Inicializando banco de dados...")
        db = get_database()
        db.init_tables()  # Cria tabelas se não existirem
        logger.info(f"✅ Banco de dados pronto: {db.db_path}")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # 2. Inicializa cache
    try:
        from infrastructure.cache.sqlite_cache_manager import get_cache_manager

        logger.info("🔧 Inicializando cache...")
        cache = get_cache_manager()
        cache.init_tables()  # Cria tabelas se não existirem
        logger.info(f"✅ Cache pronto: {cache.db_path}")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cache: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # 3. Pré-carrega fixtures
    try:
        from application.services.preload_service import PreloadService

        preload = PreloadService()

        # Verifica se já tem cache de hoje
        if await preload.has_todays_cache():
            logger.info("✅ Cache do dia já existe. Pré-carregamento ignorado.")
        else:
            logger.info("📥 Pré-carregando ligas principais...")
            await preload.preload_main_leagues()
            logger.info("✅ Pré-carregamento concluído!")

    except Exception as e:
        logger.error(f"❌ Erro no pré-carregamento: {e}")
        logger.warning("⚠️ Sistema iniciará sem pré-carga (modo fallback)")

    logger.info("✅ Betting Advisor API pronta!")



@app.get("/health")
async def health():
    return {"status": "ok", "mode": "mock"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
