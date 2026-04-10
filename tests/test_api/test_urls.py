"""Tests for URL API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_short_url(client: AsyncClient, sample_urls):
    """Test creating a shortened URL."""
    response = await client.post(
        "/api/v1/urls/",
        json={"url": sample_urls[0]},
    )

    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["original_url"] == sample_urls[0]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_short_url_with_custom_code(client: AsyncClient, sample_urls):
    """Test creating a shortened URL with custom code."""
    custom_code = "test123"
    response = await client.post(
        "/api/v1/urls/",
        json={"url": sample_urls[0], "custom_code": custom_code},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == custom_code


@pytest.mark.asyncio
async def test_duplicate_url_returns_same_code(client: AsyncClient, sample_urls):
    """Test that creating the same URL twice returns the same short code."""
    response1 = await client.post("/api/v1/urls/", json={"url": sample_urls[0]})
    response2 = await client.post("/api/v1/urls/", json={"url": sample_urls[0]})

    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["short_code"] == response2.json()["short_code"]


@pytest.mark.asyncio
async def test_redirect_to_original_url(client: AsyncClient, sample_urls):
    """Test redirecting to the original URL."""
    # Create short URL
    create_response = await client.post("/api/v1/urls/", json={"url": sample_urls[0]})
    short_code = create_response.json()["short_code"]

    # Test redirect
    redirect_response = await client.get(f"/api/v1/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == sample_urls[0]


@pytest.mark.asyncio
async def test_get_url_details(client: AsyncClient, sample_urls):
    """Test getting URL details."""
    # Create short URL
    create_response = await client.post("/api/v1/urls/", json={"url": sample_urls[0]})
    short_code = create_response.json()["short_code"]

    # Get details
    details_response = await client.get(f"/api/v1/urls/{short_code}")
    assert details_response.status_code == 200
    data = details_response.json()
    assert data["short_code"] == short_code
    assert data["original_url"] == sample_urls[0]


@pytest.mark.asyncio
async def test_deactivate_url(client: AsyncClient, sample_urls):
    """Test deactivating a URL."""
    # Create short URL
    create_response = await client.post("/api/v1/urls/", json={"url": sample_urls[0]})
    short_code = create_response.json()["short_code"]

    # Deactivate
    delete_response = await client.delete(f"/api/v1/urls/{short_code}")
    assert delete_response.status_code == 204

    # Try to access deactivated URL
    redirect_response = await client.get(f"/api/v1/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_url(client: AsyncClient):
    """Test creating URL with invalid format."""
    response = await client.post("/api/v1/urls/", json={"url": "not-a-valid-url"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_short_code_not_found(client: AsyncClient):
    """Test accessing non-existent short code."""
    response = await client.get("/api/v1/nonexistent", follow_redirects=False)
    assert response.status_code == 404
