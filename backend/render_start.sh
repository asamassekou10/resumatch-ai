#!/usr/bin/env bash
# Use gunicorn_config.py for optimized thread + worker configuration
gunicorn --config gunicorn_config.py app:app