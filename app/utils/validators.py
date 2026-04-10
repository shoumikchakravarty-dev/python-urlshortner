"""URL validation utilities."""

import re
from urllib.parse import urlparse
from app.config import settings
from app.utils.exceptions import InvalidURLException, InvalidShortCodeException


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: The URL string to validate

    Returns:
        True if valid

    Raises:
        InvalidURLException: If the URL is invalid
    """
    if not url or len(url) > settings.max_url_length:
        raise InvalidURLException(f"URL must be between 1 and {settings.max_url_length} characters")

    try:
        result = urlparse(url)
        # Check if scheme and netloc are present
        if not all([result.scheme, result.netloc]):
            raise InvalidURLException("URL must have a valid scheme (http/https) and domain")

        # Only allow http and https schemes
        if result.scheme not in ['http', 'https']:
            raise InvalidURLException("URL must use http or https scheme")

        return True
    except Exception as e:
        if isinstance(e, InvalidURLException):
            raise
        raise InvalidURLException(f"Invalid URL format: {str(e)}")


def validate_short_code(short_code: str, is_custom: bool = False) -> bool:
    """
    Validate if a short code has a valid format.

    Args:
        short_code: The short code to validate
        is_custom: Whether this is a custom code (has different length requirements)

    Returns:
        True if valid

    Raises:
        InvalidShortCodeException: If the short code is invalid
    """
    if not short_code:
        raise InvalidShortCodeException("Short code cannot be empty")

    # Check length based on whether it's custom or not
    if is_custom:
        min_length = settings.custom_code_min_length
        max_length = settings.custom_code_max_length
        if len(short_code) < min_length or len(short_code) > max_length:
            raise InvalidShortCodeException(
                f"Custom short code must be between {min_length} and {max_length} characters"
            )
    else:
        if len(short_code) != settings.short_code_length:
            raise InvalidShortCodeException(
                f"Short code must be exactly {settings.short_code_length} characters"
            )

    # Check if code contains only alphanumeric characters
    if not re.match(r'^[a-zA-Z0-9]+$', short_code):
        raise InvalidShortCodeException(
            "Short code must contain only alphanumeric characters (a-z, A-Z, 0-9)"
        )

    return True
