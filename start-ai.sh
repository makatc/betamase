#!/bin/bash
export GEMINI_API_KEY="AIzaSyCfxnAsV9Wiu27tFptlOftMNyrDJ2_6NRQ"
export DATABASE_URL="postgresql://avnadmin:YOUR_DB_SECRET@pg-basemetal-makatc-9778.c.aivencloud.com:17104/defaultdb?sslmode=require"
eval "$(/home/makatc/.local/bin/mise activate bash)"
cd /home/makatc/PROYECTOS/betamase/automation/ai/api
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
