FROM docker.io/python:3.12.6-slim

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.0 \
  WATCHFILES_FORCE_POLLING=true \
  PYTHONPATH=/

WORKDIR /api

COPY ./api/poetry.lock ./api/pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

RUN apt-get update && apt-get install -y inotify-tools

# Create log directory
RUN mkdir -p /logs && chmod -R 777 /logs

COPY ./api /api
COPY ./db /db
COPY ./models /models
COPY ./schemas /schemas
COPY ./env /env
COPY ./utils /utils
COPY ./settings /settings
COPY ./services /services
COPY ./prompts /prompts
COPY deploy/entrypoint.api.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8001
CMD [ "bash", "/entrypoint.sh" ]
