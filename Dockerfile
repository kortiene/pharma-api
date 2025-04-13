FROM python:3.12-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.4.2

RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION && \
    chgrp -R 0 $POETRY_HOME && \
    chmod -R g+rwX $POETRY_HOME

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN poetry config virtualenvs.create false && \
    poetry install --without test,dev --no-root

COPY . /app

RUN poetry build && \
    poetry install --without test,dev --no-interaction --no-ansi

EXPOSE 9090