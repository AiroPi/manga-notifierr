# syntax=docker/dockerfile-upstream:master-labs

FROM python:3.13-alpine AS python-base

FROM python-base AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
RUN --mount=type=cache,target=/var/cache/apk \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    : \
    && apk update && apk add git \
    && uv sync --no-default-groups --locked \
    && :

FROM python-base AS base
COPY --parents --from=build /app/.venv /
WORKDIR /app
COPY ./src ./
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=0

FROM base 
CMD ["python",  "./main.py"]

