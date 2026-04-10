# URL Shortener API

A modern, production-ready URL shortener built with FastAPI, SQLAlchemy, and SQLite. This project transforms a simple in-memory URL shortener into a fully-featured web API with database persistence, comprehensive testing, and automatic documentation.

## Features

- **Fast & Async**: Built with FastAPI and async/await for high performance
- **Database Persistence**: SQLite with SQLAlchemy ORM for reliable data storage
- **RESTful API**: Clean, intuitive API design with automatic OpenAPI documentation
- **Custom Short Codes**: Optional custom short codes for branded links
- **URL Expiration**: Set expiration dates for temporary links
- **Access Tracking**: Track redirect counts and access timestamps
- **Statistics**: Overall and per-URL analytics
- **Soft Delete**: URLs can be deactivated while preserving data
- **Type Safety**: Full type hints throughout the codebase
- **Tested**: Comprehensive test suite with pytest

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/
│   │   └── url_shortener.py    # Business logic
│   ├── api/
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routes/
│   │       ├── urls.py         # URL endpoints
│   │       └── stats.py        # Statistics endpoints
│   ├── database/
│   │   └── session.py          # Database session
│   └── utils/
│       ├── exceptions.py       # Custom exceptions
│       └── validators.py       # URL validation
├── tests/
│   ├── conftest.py             # Test fixtures
│   └── test_api/
│       └── test_urls.py        # API tests
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Setup

1. Clone the repository:
```bash
cd url-shortener
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Create a `.env` file (optional - defaults work fine):
```bash
cp .env.example .env
```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Usage

### Create a Shortened URL

**POST** `/api/v1/urls/`

```bash
curl -X POST "http://localhost:8000/api/v1/urls/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

Response:
```json
{
  "short_code": "aBc123X",
  "short_url": "http://localhost:8000/aBc123X",
  "original_url": "https://www.example.com/very/long/url",
  "created_at": "2026-04-09T10:30:00",
  "expires_at": null,
  "access_count": 0,
  "last_accessed_at": null,
  "is_active": true
}
```

### Create with Custom Code

```bash
curl -X POST "http://localhost:8000/api/v1/urls/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com", "custom_code": "mylink"}'
```

### Create with Expiration

```bash
curl -X POST "http://localhost:8000/api/v1/urls/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com", "expires_in_days": 30}'
```

### Redirect to Original URL

**GET** `/{short_code}`

```bash
curl -L "http://localhost:8000/aBc123X"
```

This will redirect (307) to the original URL and increment the access count.

### Get URL Details

**GET** `/api/v1/urls/{short_code}`

```bash
curl "http://localhost:8000/api/v1/urls/aBc123X"
```

Response includes full details without redirecting.

### Deactivate a URL

**DELETE** `/api/v1/urls/{short_code}`

```bash
curl -X DELETE "http://localhost:8000/api/v1/urls/aBc123X"
```

Returns 204 No Content on success.

### Get Overall Statistics

**GET** `/api/v1/stats`

```bash
curl "http://localhost:8000/api/v1/stats"
```

Response:
```json
{
  "total_urls": 42,
  "active_urls": 40,
  "total_redirects": 1523,
  "urls_created_today": 5,
  "top_urls": [
    {
      "short_code": "aBc123X",
      "access_count": 345,
      "original_url": "https://www.example.com"
    }
  ]
}
```

### Get URL Statistics

**GET** `/api/v1/stats/{short_code}`

```bash
curl "http://localhost:8000/api/v1/stats/aBc123X"
```

## Configuration

Configuration is managed via environment variables or the `.env` file:

```bash
# Application
APP_NAME="URL Shortener API"
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000
BASE_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./url_shortener.db

# URL Shortening
SHORT_CODE_LENGTH=7
ALLOW_CUSTOM_CODES=True
CUSTOM_CODE_MIN_LENGTH=3
CUSTOM_CODE_MAX_LENGTH=20
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific tests:

```bash
pytest tests/test_api/test_urls.py
```

## Development

### Code Formatting

```bash
black app tests
isort app tests
```

### Type Checking

```bash
mypy app
```

### Linting

```bash
flake8 app
```

## Architecture

### URL Shortening Algorithm

The service uses a random character generation approach (preserving the original implementation):
- Generates 7-character codes from alphanumeric characters (a-z, A-Z, 0-9)
- Provides 3.5 trillion possible combinations (62^7)
- Collision detection with retry mechanism (max 5 attempts)
- Duplicate URL detection returns existing short code

### Database Schema

**urls** table:
- `id`: Primary key
- `short_code`: Unique short code (indexed)
- `original_url`: Original URL
- `created_at`: Creation timestamp
- `expires_at`: Optional expiration timestamp
- `access_count`: Number of accesses
- `last_accessed_at`: Last access timestamp
- `is_active`: Soft delete flag

### Error Handling

The API returns consistent error responses:

- **400 Bad Request**: Invalid URL or short code format
- **404 Not Found**: Short code doesn't exist or is inactive
- **409 Conflict**: Custom short code already exists
- **410 Gone**: URL has expired
- **500 Internal Server Error**: Database or collision errors

## Migration from Original Implementation

This project evolved from a simple in-memory URL shortener (`/Users/V598970/Code/python/urlshortner`) to a production-ready API:

**Preserved**:
- Core random code generation algorithm
- Duplicate URL detection logic
- Simple, clean interface

**Enhanced**:
- Database persistence (SQLite)
- RESTful API with FastAPI
- Custom short codes
- URL expiration
- Access tracking and analytics
- Comprehensive error handling
- Type hints and validation
- Async/await for performance
- Automated testing

## Future Enhancements

Potential improvements for the future:
- User authentication and API keys
- Rate limiting
- Custom domains
- QR code generation
- Analytics dashboard
- Redis caching for frequently accessed URLs
- PostgreSQL support for production scale
- Geolocation tracking
- Bulk URL shortening

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please ensure:
- Tests pass: `pytest`
- Code is formatted: `black app tests`
- Types are correct: `mypy app`
- Coverage remains high: `pytest --cov=app`

## Support

For issues or questions, please open an issue in the repository.
