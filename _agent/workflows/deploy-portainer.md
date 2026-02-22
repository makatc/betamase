---
description: Deploy Metabase with AI functionalities to Portainer
---

To deploy the updated Metabase stack with AI features enabled, follow these steps:

1. **Commit and Push Changes**:
   ```bash
   git add .
   git commit -m "Fix build errors and implement AI backend endpoints"
   git push origin custom
   ```

2. **Wait for GitHub Actions**:
   Ensure the build finishes successfully. The image will be available as `ghcr.io/makatc/betamase:latest`.

3. **Deploy to Portainer**:
   Go to your Portainer instance and create or update a Stack with the following `docker-compose.yml`:

```yaml
version: '3'
services:
  metabase:
    image: ghcr.io/makatc/betamase:latest
    container_name: metabase_ai
    ports:
      - "3000:3000"
    environment:
      - MB_DB_TYPE=h2
      - MB_DB_FILE=/metabase-data/metabase.db
      - MB_LLM_ANTHROPIC_API_KEY=your_anthropic_api_key_here
      - LW_FEATURE_AI_SQL_GENERATION=true
      - LW_FEATURE_AI_CHAT_WIDGET=true
      - LW_FEATURE_AI_INSIGHTS=true
    volumes:
      - metabase-data:/metabase-data
    restart: always

volumes:
  metabase-data:
```

4. **Configuration**:
   - Make sure to replace `your_anthropic_api_key_here` with a valid Anthropic API key.
   - Once the container is running, go to **Admin settings -> General** and verify that "AI" features are appearing.
   - The Chat Assistant will be available in the bottom right corner (Robot icon).
   - "Ask AI" button will be available in the Native Query Editor.

5. **Troubleshooting**:
   - If AI features don't appear, check the container logs for any errors related to `metabase.api.ai`.
   - Ensure the `LW_FEATURE_*` environment variables are set to `true`.
