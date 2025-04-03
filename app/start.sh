#!/usr/bin/env bash
# This script is used to start the application using Gunicorn.
gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app