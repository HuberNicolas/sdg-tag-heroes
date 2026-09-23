#!/bin/bash
# Run from / (like the repository root locally) so relative paths such as data/pipeline/... resolve.
# Dependencies are installed system-wide in the image (virtualenvs.create false), so no `poetry run` is needed.
cd /
exec uvicorn pipeline.app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /pipeline
