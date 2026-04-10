"""Custom exceptions for the URL shortener application."""


class URLShortenerException(Exception):
    """Base exception for all URL shortener errors."""
    pass


class InvalidURLException(URLShortenerException):
    """Raised when a URL is malformed or invalid."""
    pass


class ShortCodeExistsException(URLShortenerException):
    """Raised when a custom short code already exists."""
    pass


class ShortCodeNotFoundException(URLShortenerException):
    """Raised when a short code is not found in the database."""
    pass


class URLExpiredException(URLShortenerException):
    """Raised when trying to access an expired URL."""
    pass


class InvalidShortCodeException(URLShortenerException):
    """Raised when a short code has an invalid format."""
    pass


class DatabaseException(URLShortenerException):
    """Raised for database-related errors."""
    pass


class CollisionRetriesExceededException(URLShortenerException):
    """Raised when maximum collision retries are exceeded."""
    pass
