# Makefile for Memora
.PHONY: init_be run_be
# Init backend environment
init_be:
	cd backend && uv sync
# Run the backend server
run_be:
	cd backend && uv run main.py
