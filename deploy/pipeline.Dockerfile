FROM docker.io/python:3.10.15-slim-bookworm

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

WORKDIR /pipeline

COPY ./pipeline/poetry.lock ./pipeline/pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root

RUN apt-get update && apt-get install -y inotify-tools

COPY ./pipeline /pipeline
COPY deploy/entrypoint.pipeline.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8000
CMD [ "bash", "/entrypoint.sh" ]
