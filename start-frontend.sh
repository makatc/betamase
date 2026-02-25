#!/bin/bash
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true
eval "$(/home/makatc/.local/bin/mise activate bash)"
cd /home/makatc/PROYECTOS/betamase
bun run build-hot
