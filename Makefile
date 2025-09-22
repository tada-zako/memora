# Makefile for Memora
.PHONY: init_be run_be
# Init backend environment
init_be:
	cd backend && uv sync
# Run the backend server
run_be:
	uv run backend.main.py
