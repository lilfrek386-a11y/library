import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.db import db_helper
from src.core.models import Base
from src.main import app


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:Qazqwerty2006@localhost:5432/library_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def init_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


@pytest.fixture(scope="function")
async def db_session():

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def ac(db_session):

    app.dependency_overrides[db_helper.session_dependency] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
