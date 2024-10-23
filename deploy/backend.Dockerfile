FROM docker.io/python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    inotify-tools \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && apt-get clean

COPY ./backend/poetry.lock ./backend/pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

COPY ./backend /backend
COPY ./db /db
COPY ./models /models
COPY ./schemas /schemas
COPY ./env /env
COPY ./utils /utils
COPY ./settings /settings
COPY deploy/entrypoint.backend.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8002
CMD [ "bash", "/entrypoint.sh" ]
