#!/bin/bash
cd /api
exec poetry run uvicorn api.app.main:app --host 0.0.0.0 --port 8001 --reload \
  --reload-dir /api \
  --reload-dir /models \
  --reload-dir /db \
  --reload-dir /request_models \
  --reload-dir /schemas \
  --reload-dir /enums \
  --reload-dir /settings \
  --reload-dir /services \
  --reload-dir /utils
