#!/usr/bin/env bash
# Purpose: run FastAPI with reload for local development

set -e  # exit immediately if a command exits with non-zero status
export PYTHONUNBUFFERED=1

uvicorn app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
