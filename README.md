# UPC FIB Agent

A Python project for the UPC FIB agent system.

## Prerequisites

- Python 3.13 or higher
- `uv` package manager

## Getting Started

### 1. Install Dependencies including development dependencies

```bash
uv sync --dev
```

### 2. Set Up Pre-commit Hooks

(if not installed yet)
```bash
uv add pre-commit
```

(to install the hooks)
```bash
uv run pre-commit install
```

This ensures code quality checks run automatically on each commit.

### 3. Copy .env.example to .env and fill in the values

```bash
cp .env.example .env
```

You will need to:
- Obtain a Langsmith API key (https://langchain-5e9cc07a.mintlify.app/langsmith/home).
- Obtain a Tavily API key (https://docs.tavily.com/documentation/quickstart) - this is only relevant for testing purposes.
- Obtain a FIB API client ID and client secret (https://api.fib.upc.edu/v2/o/applications/register_private/).
- Ask for access to the `alta-mente` GCP project (akos.schneider@estudiantat.upc.edu)

### 4. Set up GCP authentication for using Gemini on Vertex AI

1. **Create a GCP account** (if you don't have one): https://cloud.google.com

2. **Install the Google Cloud CLI**: https://cloud.google.com/sdk/docs/install

3. **Authenticate with GCP:**
   ```bash
   gcloud auth login
   ```
4. **Set the project:**
   ```bash
   gcloud config set project alta-mente
   ```
   > Note: If you want to create your own project, run `gcloud projects create YOUR_PROJECT_ID` first, and ensure billing is enabled at https://console.cloud.google.com/billing

5. **Set up application default credentials:**
   ```bash
   gcloud auth application-default login
   ```
   
### 5. Run the langgraph studio for testing the agent

```bash
source .venv/bin/activate

langgraph dev --allow-blocking
```

This will open a browser window and log you in to Langsmith. There in the sidebar you can find the Studio and test the agent.

## Project Structure

```
.
├── src/              # Python source code
├── pyproject.toml    # Project configuration and dependencies
└── README.md         # This file
```

## Development

- Place all Python code in the `src/` directory
- Run `uv sync` after updating `pyproject.toml`
- Pre-commit hooks will automatically check code style and quality

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **Pre-commit** for automated checks

All checks are enforced via pre-commit hooks.

