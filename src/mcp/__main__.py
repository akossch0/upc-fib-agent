"""
Entry point for running the FIB API MCP server.

Usage:
    python -m src.mcp
"""

import asyncio

from src.api import configure_oauth
from src.mcp.server import run_server

# Configure OAuth for private endpoints if credentials are available
configure_oauth()

if __name__ == "__main__":
    asyncio.run(run_server())
