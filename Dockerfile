FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY uv.lock README.md pyproject.toml LICENSE .python-version /app/

COPY sylog/ /app/sylog/

RUN uv sync --locked

EXPOSE 8080

CMD ["uv", "run", "sylog/main.py"]
