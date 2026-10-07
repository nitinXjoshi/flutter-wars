"""Cloudflare Python Worker entrypoint.

Wraps the FastAPI app with the official Workers ASGI adapter. This file is the
only place that may import the `workers` package, so the app stays runnable under
plain uvicorn locally.

The adapter drives the ASGI lifespan cycle per request, so nothing expensive may
live in a FastAPI lifespan/startup hook here.
"""

from workers import asgi

from app import app

Default = asgi.entrypoint(app)
