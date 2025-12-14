import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api_v1.authors import router as authors_router
from src.api_v1.books import router as books_router


logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


async def database_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    if isinstance(exc, IntegrityError):
        logger.warning(f"Integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Conflict: Data already exists or constraint violation"},
        )

    logger.exception("Unexpected Database error occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error dealing with DB"},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=False,
    )
    FastAPICache.init(
        RedisBackend(redis),
        prefix=settings.cache.prefix,
    )
    try:
        await redis.ping()
        logger.info("Redis is connected")

        logger.info("Try to set a test key")
        await redis.set("test_startup_key", "working")
    except Exception as e:

        logger.warning(f"Redis is not connected", exc_info=e)
        raise e
    logger.info("Test set complete")
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SQLAlchemyError, database_exception_handler)


@app.get("/")
def root():
    return {"message": "Hello"}


app.include_router(books_router)
app.include_router(authors_router)
