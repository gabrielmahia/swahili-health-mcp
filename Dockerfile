FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/swahili-health-mcp"
LABEL org.opencontainers.image.description="swahili-health-mcp: MCP server over stdio, no credentials needed"
LABEL org.opencontainers.image.licenses="MIT"
# Installs the latest published release from PyPI (do not pin: a pinned version made Glama inspect an old release of mpesa-mcp).
RUN pip install --no-cache-dir swahili-health-mcp
CMD ["swahili-health-mcp"]
