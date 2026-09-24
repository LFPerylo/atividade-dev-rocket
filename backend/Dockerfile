FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev \
    && useradd --create-home --uid 1000 claquete \
    && mkdir -p /data \
    && chown -R claquete /data \
    && chmod +x docker-entrypoint.sh

USER claquete

ENV ENVIRONMENT=production \
    DATABASE_URL=sqlite+aiosqlite:////data/rocketlab.db

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=60s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["./docker-entrypoint.sh"]
