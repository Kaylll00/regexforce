import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.db.base import Base
from app.db.session import engine
from engine.errors import EngineError

load_dotenv()

app = FastAPI(title="RegexForge API")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(router)


@app.exception_handler(EngineError)
async def engine_error_handler(_, exc: EngineError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": exc.code, "message": str(exc), "position": exc.position}},
    )


@app.get("/health")
def health():
    return {"status": "ok"}