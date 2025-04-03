#!/usr/bin/env bash
export PYTHONPATH=$PYTHONPATH:/opt/render/TrashTalk-BE/app
gunicorn -w 4 -b 0.0.0.0:$PORT app.main:app