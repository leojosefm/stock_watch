FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY mcp_server.py .

# Port configured explicitly in mcp_server.py (host=0.0.0.0, port=8100)
EXPOSE 8100

ENV API_BASE_URL=http://fastapi:8000
# CLIENT_ID, MCP_RESOURCE_URL, and ALLOWED_EMAILS are provided at runtime
# via docker-compose environment / .env - not baked into the image.

CMD ["python", "mcp_server.py"]