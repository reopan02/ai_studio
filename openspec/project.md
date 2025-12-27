# Project Context

## Purpose
AI Video/Image Generator API that provides a unified interface for generating videos and images using external AI models (Sora, Veo, Seedance, etc.). The system includes user authentication, encrypted storage for user requests/responses, request logging, quota management, and a static web frontend for task creation and monitoring.

## Tech Stack
- **Backend Framework**: FastAPI (Python async web framework)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL (asyncpg) / SQLite (aiosqlite) for development
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic v2 with pydantic-settings
- **HTTP Client**: HTTPX (async)
- **Server**: Uvicorn with standard extras
- **Additional**: python-multipart, email-validator, tenacity (retry logic), tqdm (progress), python-dotenv

## Project Conventions

### Code Style
- Use async/await pattern throughout for I/O operations
- Type hints required for function signatures
- Snake_case for variables, functions, and file names
- PascalCase for class names
- Use absolute imports from `app.*` package
- Keep route handlers thin - delegate business logic to core modules
- Use dependency injection for database sessions and authentication

### Architecture Patterns
- **Layered Architecture**:
  - `app/api/v1/`: API route handlers organized by resource (auth, videos, images, storage, etc.)
  - `app/core/`: Business logic (backup, encryption, static file handling)
  - `app/models/`: Database models (database.py) and Pydantic schemas (schemas.py)
  - `app/db/`: Database session management and initialization
  - `app/middleware/`: Request/response middleware (CSRF, logging, auth redirects)
  - `app/clients/`: External API client integrations
  - `app/static/`: Frontend HTML/JS/CSS files
- **Resource-based routing**: `/api/v1/{resource}` pattern
- **Database models use UUIDs** as primary keys (string representation)
- **Encryption at rest**: Sensitive request/response data encrypted using `STORAGE_MASTER_KEY`
- **Lifespan management**: Database initialization and backup tasks managed via FastAPI lifespan
- **Middleware stack**: CORS → CSRF → RequestLogging → WebAuthRedirect

### Testing Strategy
- Currently no automated tests present (test directory exists: `js_tests/`)
- Manual testing through frontend interfaces
- Health check endpoint: `GET /health`

### Git Workflow
- Main branch: `main`
- Commit message style from recent commits: Descriptive imperative mood (e.g., "Transform Drawing History into a full repository system with pagination, search, filter, and CRUD operations")
- Recent pattern shows feature-complete commits rather than incremental WIP commits

## Domain Context
- **External AI Video/Image APIs**: System acts as a proxy/wrapper to external AI generation services
- **User quota management**: Each user has storage quota (default 1 GiB) tracked in `storage_used_bytes`
- **Encrypted storage**: Request/response payloads encrypted before database storage using Fernet symmetric encryption
- **Session management**: JWT tokens with configurable expiration (default 100 years for convenience)
- **CSRF protection**: Cookie-based auth requires `X-CSRF-Token` header for non-safe methods
- **Request logging**: All API requests logged to `api_request_logs` with sanitized sensitive fields
- **Backup system**: Optional automated database backups with configurable interval and retention

## Important Constraints
- **STORAGE_MASTER_KEY required**: Must be set for encrypted storage operations to work
- **JWT_SECRET_KEY required**: Must be set for authentication to work
- **Database migrations**: Currently using `Base.metadata.create_all()` - no migration framework
- **Static file caching**: Development mode uses `no-store`, production uses long-term caching
- **CORS**: Currently allows all origins (`allow_origins=["*"]`)
- **Cookie security**: Defaults to non-secure cookies (`COOKIE_SECURE=False`) - should be `True` in production with HTTPS

## External Dependencies
- **AI Generation APIs**: External services at configurable `API_BASE_URL` (default: https://api.gpt-best.com)
  - Sora: `/v2/videos/generations`
  - Veo: `/v1/video/veo/text-to-video` and `/v1/video/veo/tasks/{task_id}`
  - Seedance: `/v1/video/seedance/text-to-video` and `/v1/video/seedance/tasks/{task_id}`
  - Image models: Various endpoints under `/v1/images/`
- **Database**: PostgreSQL (production) or SQLite (development/testing)
- **Environment variables**: Requires `.env` file with API_KEY, DATABASE_URL, JWT_SECRET_KEY, STORAGE_MASTER_KEY
