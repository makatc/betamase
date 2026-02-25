#!/bin/bash
echo "Starting script..."
# Configure Aiven Postgres for Metabase App DB
export MB_DB_TYPE=postgres
export MB_DB_HOST=pg-basemetal-makatc-9778.c.aivencloud.com
export MB_DB_PORT=17104
export MB_DB_DBNAME=defaultdb
export MB_DB_USER=avnadmin
export MB_DB_PASS=YOUR_DB_SECRET
export MB_DB_CONNECTION_URI="jdbc:postgresql://pg-basemetal-makatc-9778.c.aivencloud.com:17104/defaultdb?sslmode=require"
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true
echo "Features exported."
eval "$(/home/makatc/.local/bin/mise activate bash)"
echo "Mise activated."
java -version
echo "Starting clojure..."
cd /home/makatc/PROYECTOS/betamase
clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
