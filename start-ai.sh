#!/bin/bash
source ~/.betamase_secrets
eval "$(/home/makatc/.local/bin/mise activate bash)"
cd /home/makatc/PROYECTOS/betamase/automation/ai/api
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
