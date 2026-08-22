import logging
from typing import AsyncGenerator, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

logger = logging.getLogger(__name__)

# Create Async SQLAlchemy Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Base class for SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass


class DevInMemoryResult:
    def __init__(self, items: Optional[List[Any]] = None):
        self._items = items or []

    def scalar_one_or_none(self):
        return self._items[0] if self._items else None

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


class DevInMemorySession:
    """Lightweight in-memory session proxy used as non-Docker fallback when DB is offline."""
    def __init__(self):
        self._store: List[Any] = []

    def add(self, instance: Any) -> None:
        if not hasattr(instance, "id") or instance.id is None:
            import uuid
            try:
                instance.id = uuid.uuid4()
            except Exception:
                pass
        self._store.append(instance)

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def execute(self, stmt: Any) -> DevInMemoryResult:
        return DevInMemoryResult([])


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session for FastAPI endpoints with dev fallback."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            try:
                await session.commit()
            except Exception as commit_err:
                if settings.ENVIRONMENT.lower() == "dev":
                    logger.warning("Database commit skipped in dev mode: %s", commit_err)
                else:
                    raise
        except Exception:
            try:
                await session.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                await session.close()
            except Exception:
                pass
