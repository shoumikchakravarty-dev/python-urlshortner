"""URL Shortener service - refactored from original implementation with database persistence."""

import string
import random
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import URL
from app.utils.validators import validate_url, validate_short_code
from app.utils.exceptions import (
    ShortCodeExistsException,
    ShortCodeNotFoundException,
    URLExpiredException,
    CollisionRetriesExceededException,
    DatabaseException,
)


class URLShortenerService:
    """
    URL Shortener service with database persistence.
    Refactored from original in-memory implementation.
    """

    def __init__(self):
        """Initialize the URL shortener service."""
        self.characters = string.ascii_letters + string.digits

    def _generate_short_code(self, length: Optional[int] = None) -> str:
        """
        Generate a random short code.
        Preserves the original algorithm from the initial implementation.

        Args:
            length: Length of the short code (defaults to settings value)

        Returns:
            A random short code string
        """
        if length is None:
            length = settings.short_code_length

        return ''.join(random.choice(self.characters) for _ in range(length))

    async def shorten_url(
        self,
        original_url: str,
        db: AsyncSession,
        custom_code: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> URL:
        """
        Shorten a URL and store it in the database.

        Args:
            original_url: The URL to shorten
            db: Database session
            custom_code: Optional custom short code
            expires_in_days: Optional expiration in days

        Returns:
            The URL database model

        Raises:
            InvalidURLException: If URL is invalid
            ShortCodeExistsException: If custom code already exists
            CollisionRetriesExceededException: If too many collisions occur
        """
        # Validate the URL
        validate_url(original_url)

        # Check if URL already exists (like original implementation)
        stmt = select(URL).where(
            URL.original_url == original_url,
            URL.is_active == True
        )
        result = await db.execute(stmt)
        existing_url = result.scalar_one_or_none()

        if existing_url:
            # Return existing shortened URL (matches original behavior)
            return existing_url

        # Calculate expiration date if provided
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Handle custom code
        if custom_code:
            if not settings.allow_custom_codes:
                raise ShortCodeExistsException("Custom codes are not allowed")

            validate_short_code(custom_code, is_custom=True)

            # Check if custom code exists
            stmt = select(URL).where(URL.short_code == custom_code)
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise ShortCodeExistsException(f"Short code '{custom_code}' already exists")

            short_code = custom_code
        else:
            # Generate random short code with collision handling
            short_code = None
            for attempt in range(settings.max_collision_retries):
                candidate = self._generate_short_code()

                # Check if code already exists
                stmt = select(URL).where(URL.short_code == candidate)
                result = await db.execute(stmt)
                if not result.scalar_one_or_none():
                    short_code = candidate
                    break

            if not short_code:
                raise CollisionRetriesExceededException(
                    f"Failed to generate unique short code after {settings.max_collision_retries} attempts"
                )

        # Create new URL record
        try:
            url_record = URL(
                short_code=short_code,
                original_url=original_url,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                access_count=0,
                is_active=True,
            )

            db.add(url_record)
            await db.commit()
            await db.refresh(url_record)

            return url_record
        except Exception as e:
            await db.rollback()
            raise DatabaseException(f"Failed to create shortened URL: {str(e)}")

    async def get_url(
        self,
        short_code: str,
        db: AsyncSession,
        increment_access: bool = True
    ) -> URL:
        """
        Retrieve the original URL from a short code.
        Similar to get_original_url from the original implementation.

        Args:
            short_code: The short code to look up
            db: Database session
            increment_access: Whether to increment access count

        Returns:
            The URL database model

        Raises:
            ShortCodeNotFoundException: If short code doesn't exist
            URLExpiredException: If the URL has expired
        """
        # Clean short code (handle both full URLs and codes like original)
        short_code = short_code.strip().split('/')[-1]

        stmt = select(URL).where(URL.short_code == short_code)
        result = await db.execute(stmt)
        url_record = result.scalar_one_or_none()

        if not url_record:
            raise ShortCodeNotFoundException(f"Short code '{short_code}' not found")

        if not url_record.is_active:
            raise ShortCodeNotFoundException(f"Short code '{short_code}' is no longer active")

        # Check expiration
        if url_record.expires_at and url_record.expires_at < datetime.utcnow():
            raise URLExpiredException(f"URL with short code '{short_code}' has expired")

        # Increment access count if requested
        if increment_access:
            try:
                url_record.access_count += 1
                url_record.last_accessed_at = datetime.utcnow()
                await db.commit()
                await db.refresh(url_record)
            except Exception as e:
                await db.rollback()
                raise DatabaseException(f"Failed to update access count: {str(e)}")

        return url_record

    async def deactivate_url(self, short_code: str, db: AsyncSession) -> bool:
        """
        Deactivate (soft delete) a shortened URL.

        Args:
            short_code: The short code to deactivate
            db: Database session

        Returns:
            True if successful

        Raises:
            ShortCodeNotFoundException: If short code doesn't exist
        """
        stmt = select(URL).where(URL.short_code == short_code)
        result = await db.execute(stmt)
        url_record = result.scalar_one_or_none()

        if not url_record:
            raise ShortCodeNotFoundException(f"Short code '{short_code}' not found")

        try:
            url_record.is_active = False
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise DatabaseException(f"Failed to deactivate URL: {str(e)}")

    async def get_stats(self, db: AsyncSession) -> dict:
        """
        Get overall statistics.
        Enhanced version of the original get_stats method.

        Args:
            db: Database session

        Returns:
            Dictionary with statistics
        """
        try:
            # Total URLs
            total_stmt = select(func.count(URL.id))
            total_result = await db.execute(total_stmt)
            total_urls = total_result.scalar()

            # Active URLs
            active_stmt = select(func.count(URL.id)).where(URL.is_active == True)
            active_result = await db.execute(active_stmt)
            active_urls = active_result.scalar()

            # Total redirects
            redirects_stmt = select(func.sum(URL.access_count))
            redirects_result = await db.execute(redirects_stmt)
            total_redirects = redirects_result.scalar() or 0

            # URLs created today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_stmt = select(func.count(URL.id)).where(URL.created_at >= today_start)
            today_result = await db.execute(today_stmt)
            urls_created_today = today_result.scalar()

            # Top URLs
            top_stmt = select(URL).where(URL.is_active == True).order_by(URL.access_count.desc()).limit(10)
            top_result = await db.execute(top_stmt)
            top_urls = top_result.scalars().all()

            return {
                "total_urls": total_urls or 0,
                "active_urls": active_urls or 0,
                "total_redirects": total_redirects,
                "urls_created_today": urls_created_today or 0,
                "top_urls": top_urls,
            }
        except Exception as e:
            raise DatabaseException(f"Failed to fetch statistics: {str(e)}")

    async def get_url_stats(self, short_code: str, db: AsyncSession) -> URL:
        """
        Get statistics for a specific URL.

        Args:
            short_code: The short code to get stats for
            db: Database session

        Returns:
            The URL database model with statistics

        Raises:
            ShortCodeNotFoundException: If short code doesn't exist
        """
        # Use get_url but don't increment access count
        return await self.get_url(short_code, db, increment_access=False)
