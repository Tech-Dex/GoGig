#!/usr/bin/env bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 .
black .
vulture . --min-confidence 70 --exclude=".venv,alembic"
flake8 \
    --exclude alembic/versions,alembic/__pycache__,alembic/env.py,models/__pycache__,cogs/__pycache__,config/__pycache__,services/__pycache__,.venv \
    --max-line-length=120 \
    .
