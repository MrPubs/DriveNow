from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Create factory
engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI endpoints
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        async with session.begin():  # opens transaction, commits on success, rolls back on exception
            yield session