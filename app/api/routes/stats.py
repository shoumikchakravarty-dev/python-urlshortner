"""API routes for statistics."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database, get_url_shortener_service
from app.models.schemas import StatsResponse, URLStatsResponse, TopURLResponse
from app.services.url_shortener import URLShortenerService
from app.config import settings

router = APIRouter()


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get overall statistics",
    description="Get overall URL shortener statistics including total URLs, redirects, and top URLs"
)
async def get_overall_stats(
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Get overall statistics."""
    stats = await service.get_stats(db)

    # Convert top URLs to response schema
    top_urls = [
        TopURLResponse(
            short_code=url.short_code,
            access_count=url.access_count,
            original_url=url.original_url,
        )
        for url in stats["top_urls"]
    ]

    return StatsResponse(
        total_urls=stats["total_urls"],
        active_urls=stats["active_urls"],
        total_redirects=stats["total_redirects"],
        urls_created_today=stats["urls_created_today"],
        top_urls=top_urls,
    )


@router.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
    summary="Get URL statistics",
    description="Get statistics for a specific shortened URL"
)
async def get_url_statistics(
    short_code: str,
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Get statistics for a specific URL."""
    url_record = await service.get_url_stats(short_code, db)

    return URLStatsResponse(
        short_code=url_record.short_code,
        access_count=url_record.access_count,
        created_at=url_record.created_at,
        last_accessed_at=url_record.last_accessed_at,
    )
