"""Pydantic schemas for API request and response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class URLCreateRequest(BaseModel):
    """Request schema for creating a shortened URL."""
    url: str = Field(..., description="The original URL to shorten", min_length=1, max_length=2048)
    custom_code: Optional[str] = Field(None, description="Optional custom short code", min_length=3, max_length=20)
    expires_in_days: Optional[int] = Field(None, description="Optional expiration in days", gt=0)


class URLResponse(BaseModel):
    """Response schema for URL information."""
    short_code: str = Field(..., description="The short code for the URL")
    short_url: str = Field(..., description="The complete shortened URL")
    original_url: str = Field(..., description="The original URL")
    created_at: datetime = Field(..., description="When the URL was created")
    expires_at: Optional[datetime] = Field(None, description="When the URL expires")
    access_count: int = Field(0, description="Number of times the URL was accessed")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")
    is_active: bool = Field(True, description="Whether the URL is active")

    class Config:
        from_attributes = True


class URLDetailsResponse(URLResponse):
    """Extended response schema with additional details."""
    id: int = Field(..., description="Database ID")


class StatsResponse(BaseModel):
    """Response schema for overall statistics."""
    total_urls: int = Field(..., description="Total number of URLs")
    active_urls: int = Field(..., description="Number of active URLs")
    total_redirects: int = Field(..., description="Total number of redirects")
    urls_created_today: int = Field(..., description="URLs created today")
    top_urls: List["TopURLResponse"] = Field([], description="Top accessed URLs")


class TopURLResponse(BaseModel):
    """Response schema for top URL information."""
    short_code: str = Field(..., description="The short code")
    access_count: int = Field(..., description="Number of accesses")
    original_url: str = Field(..., description="The original URL")

    class Config:
        from_attributes = True


class URLStatsResponse(BaseModel):
    """Response schema for individual URL statistics."""
    short_code: str = Field(..., description="The short code")
    access_count: int = Field(..., description="Number of times accessed")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
