# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UPC FIB Agent is a conversational AI agent for FIB (Facultat d'Informàtica de Barcelona) at UPC. It helps with information about courses, exams, professors, schedules, and university news using a hierarchical agent architecture built with `deepagents`.

## Common Commands

```bash
# Install dependencies
uv sync --dev

# Run LangGraph Studio (interactive agent testing)
source .venv/bin/activate && langgraph dev --allow-blocking

# Run MCP server
uv run python -m src.mcp

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix
uv run ruff format

# OAuth authentication (for private API endpoints)
make auth

# Run evaluation inference
make inference MODEL=gemini-2.5-flash LIMIT=5

# Run evaluation metrics (requires inference output)
make evaluate INPUT=evaluation/results/inference_*.json

# View evaluation dashboard
cd evaluation && python -m http.server 8000
```

## Architecture

### Hierarchical Agent Design

The agent uses a two-level hierarchy via `deepagents.create_deep_agent`:

1. **Root Agent** (`src/agent/main.py`): Handles private/authenticated tools and coordinates subagents
   - Tools: `get_my_profile`, `get_my_courses`, `get_my_schedule`, `get_my_notices`, `internet_search`
   - Delegates public queries to subagent via `task()` tool

2. **Public FIB Subagent**: Handles all public FIB API queries
   - Tools: `search_courses`, `get_course_details`, `search_exams`, `get_upcoming_exams`, `search_professors`, `get_academic_terms`, `get_current_term`, `get_fib_news`, `list_classrooms`

### Model Strategy Pattern

The agent supports multiple model backends via strategy pattern (`src/agent/main.py:35-63`):
- `GeminiModelStrategy`: For Vertex AI Gemini models (default: `gemini-2.5-flash`)
- `CustomModelStrategy`: For any `BaseChatModel` (Ollama, OpenAI, local models)

### Key Integration Points

- **LangGraph Studio**: Configured via `langgraph.json`, entry point is `get_default_agent()`
- **MCP Server**: `src/mcp/server.py` exposes tools via Model Context Protocol
- **FIB API Client**: `src/api/client.py` handles HTTP requests with pagination and error handling
- **OAuth**: `src/auth/oauth.py` implements OAuth2 authorization code flow for private endpoints

### Data Flow

User query → Root Agent → (private tools OR task() to subagent) → FIB API → Response

## Code Conventions

- **Absolute imports only** (no relative imports)
- **Module-level docstrings only** (no method docstrings)
- **Ruff** for linting and formatting (line length 150)
- **Pydantic models** for all API types (`src/models/fib_types.py`)

## Environment Variables

Required in `.env`:
- `FIB_CLIENT_ID` / `FIB_CLIENT_SECRET`: FIB API OAuth credentials
- `LANGSMITH_API_KEY`: For tracing
- `TAVILY_API_KEY`: For web search
- GCP authentication for Vertex AI (use `gcloud auth application-default login`)

## Evaluation Framework

Located in `evaluation/`:
- `dataset/questions.json`: 45 test questions across 10 categories
- `dataset/metrics.json`: 7 LLM-as-judge metrics
- `visualize.html` / `compare.html`: Interactive dashboards for results

Workflow: `make inference` → `make evaluate` → view in dashboard
