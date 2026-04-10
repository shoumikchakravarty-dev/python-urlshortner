"""API routes for URL shortening operations."""

from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_database, get_url_shortener_service
from app.models.schemas import URLCreateRequest, URLResponse, URLDetailsResponse
from app.services.url_shortener import URLShortenerService
from app.config import settings

router = APIRouter()


@router.post(
    "/urls/",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create shortened URL",
    description="Create a new shortened URL with optional custom code and expiration"
)
async def create_short_url(
    request: URLCreateRequest,
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Create a new shortened URL."""
    url_record = await service.shorten_url(
        original_url=request.url,
        db=db,
        custom_code=request.custom_code,
        expires_in_days=request.expires_in_days,
    )

    return URLResponse(
        short_code=url_record.short_code,
        short_url=f"{settings.base_url}/{url_record.short_code}",
        original_url=url_record.original_url,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        access_count=url_record.access_count,
        last_accessed_at=url_record.last_accessed_at,
        is_active=url_record.is_active,
    )


@router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    description="Redirect to the original URL and track access"
)
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Redirect to the original URL."""
    url_record = await service.get_url(short_code, db, increment_access=True)
    return RedirectResponse(url=url_record.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get(
    "/urls/{short_code}",
    response_model=URLDetailsResponse,
    summary="Get URL details",
    description="Get detailed information about a shortened URL without redirecting"
)
async def get_url_details(
    short_code: str,
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Get details about a shortened URL without redirecting."""
    url_record = await service.get_url(short_code, db, increment_access=False)

    return URLDetailsResponse(
        id=url_record.id,
        short_code=url_record.short_code,
        short_url=f"{settings.base_url}/{url_record.short_code}",
        original_url=url_record.original_url,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        access_count=url_record.access_count,
        last_accessed_at=url_record.last_accessed_at,
        is_active=url_record.is_active,
    )


@router.delete(
    "/urls/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate URL",
    description="Deactivate (soft delete) a shortened URL"
)
async def deactivate_url(
    short_code: str,
    db: AsyncSession = Depends(get_database),
    service: URLShortenerService = Depends(get_url_shortener_service),
):
    """Deactivate a shortened URL."""
    await service.deactivate_url(short_code, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
