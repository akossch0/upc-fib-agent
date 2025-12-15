"""
Entry point for running the FIB API MCP server.

Usage:
    python -m src.mcp
"""

import asyncio

from src.mcp.server import run_server

if __name__ == "__main__":
    asyncio.run(run_server())
