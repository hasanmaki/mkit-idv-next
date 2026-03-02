SHELL := /usr/bin/env bash

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help install dev dev-backend dev-frontend

help:
	@echo "Available targets:"
	@echo "  make install       - Install backend/frontend dependencies"
	@echo "  make dev           - Run backend + frontend in one command"
	@echo "  make dev-backend   - Run backend only"
	@echo "  make dev-frontend  - Run frontend only"

install:
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && npm install

dev-backend:
	cd $(BACKEND_DIR) && uv run fastapi dev app/main.py --port 9914

dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev

dev:
	@set -euo pipefail; \
	trap 'kill 0' INT TERM EXIT; \
	(cd $(BACKEND_DIR) && uv run fastapi dev app/main.py --port 9914) & \
	backend_pid=$$!; \
	(cd $(FRONTEND_DIR) && npm run dev) & \
	frontend_pid=$$!; \
	wait $$backend_pid $$frontend_pid
