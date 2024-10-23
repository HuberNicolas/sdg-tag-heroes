#!/bin/bash
cd /pipeline
exec poetry run uvicorn pipeline.app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /pipeline
