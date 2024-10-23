#!/bin/bash
cd /api
exec poetry run uvicorn api.app.main:app --host 0.0.0.0 --port 8001 --reload --reload-dir /api

