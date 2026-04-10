"""Dependency injection for API routes."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.url_shortener import URLShortenerService


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_db():
        yield session


def get_url_shortener_service() -> URLShortenerService:
    """Get URL shortener service instance."""
    return URLShortenerService()
