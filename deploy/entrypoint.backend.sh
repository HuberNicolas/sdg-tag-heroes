#!/bin/bash

# Truncate tables, remove if we have real data
poetry run python -m backend.manage trunc_and_reset_django_tables

# Run migrations to ensure the database is up to date
poetry run python -m backend.manage migrate

# Finally, start the server
exec poetry run python -m backend.manage runserver 0.0.0.0:8002

