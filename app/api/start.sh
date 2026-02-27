#!/bin/sh
set -e

# wait for Postgres to be ready through docker orchestration
 

# run migrations
alembic -c /app/alembic.ini upgrade head

# start the API
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
