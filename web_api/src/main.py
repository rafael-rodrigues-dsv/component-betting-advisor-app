"""
Betting Advisor API - Backend Mockado
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from web.controllers.match_controller import router as match_router
from web.controllers.prediction_controller import router as prediction_router
from web.controllers.ticket_controller import router as ticket_router

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


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "mock"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
