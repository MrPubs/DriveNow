import asyncio
import re
import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer
from app.api.main import app
from httpx import AsyncClient
from alembic.config import Config
from alembic import command


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def postgres_container():
    """Spin up ephemeral Postgres container, yield both sync and async URLs"""
    with PostgresContainer("postgres:16") as postgres:
        raw_url = postgres.get_connection_url()

        # Sync URL for Alembic (psycopg2)
        sync_url = re.sub(r"^postgresql(\+\w+)?://", "postgresql+psycopg2://", raw_url)

        # Async URL for SQLAlchemy AsyncEngine
        async_url = re.sub(r"^postgresql(\+\w+)?://", "postgresql+asyncpg://", raw_url)

        yield {"sync": sync_url, "async": async_url}


@pytest_asyncio.fixture(scope="session")
def run_migrations(postgres_container):
    """Run Alembic migrations once per session by injecting DATABASE_URL env var"""

    # Temporarily override DATABASE_URL so env.py picks it up
    original = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = postgres_container["sync"]

    try:
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "app", "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
    finally:
        # Always restore original state — don't pollute other processes
        if original is None:
            del os.environ["DATABASE_URL"]
        else:
            os.environ["DATABASE_URL"] = original


@pytest_asyncio.fixture
async def db_session(postgres_container, run_migrations):
    """Provides an isolated async DB session per test, wrapped in a rollback"""
    engine = create_async_engine(postgres_container["async"], future=True, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Wrap each test in a transaction that gets rolled back — true isolation
    async with engine.connect() as conn:
        await conn.begin()
        async with async_session(bind=conn) as session:
            yield session
        await conn.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """Provides AsyncClient wired to the ephemeral test DB session"""
    from app.core.database import get_db_session
    from httpx import ASGITransport

    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac

    app.dependency_overrides.clear()