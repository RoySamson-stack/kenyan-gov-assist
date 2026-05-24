# Curriculum Translation Backend

This directory is a copied standalone integration of the local `/home/unknwn/Translation_Backend` project.

It keeps the original backend's FastAPI package name (`app`) and runtime layout intact, so it runs as a separate service from the main `kenyan-gov-assist/backend` API. This avoids import conflicts with the existing main assistant backend, which also uses an `app` Python package.

## Runtime

From the repository root:

```bash
docker-compose up -d curriculum-translation-backend curriculum-celery-worker curriculum-flower
```

The curriculum translation API is exposed on:

```text
http://localhost:8002
http://localhost:8002/docs
```

The original copied API documentation is preserved in `README.original.md`.

## Included From Translation_Backend

- FastAPI application and routers
- SQLAlchemy models and migrations
- PDF, Word, Excel, and text translation services
- Celery ingestion and translation tasks
- Seed script and admin creation script
- Dockerfile and Python requirements

## Not Copied

- The source project's `.git` directory
- The source project's `.env`
- Local uploaded/generated files from `storage/`
- Local caches and generated debug image/PDF artifacts
