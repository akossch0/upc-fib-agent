# Scripts

Utility scripts for authentication, API exploration, and evaluation.

## Scripts Overview

| Script | Description |
|--------|-------------|
| `authenticate.py` | Authenticate with the FIB API using OAuth |
| `explore_fib_api.py` | Explore and test FIB API endpoints |
| `run_eval_inference.py` | Run agent inference on evaluation questions |
| `run_eval_metrics.py` | Evaluate inference results using deepeval metrics |

## Evaluation Inference

The `run_eval_inference.py` script runs the FIB agent on evaluation questions and outputs responses with trajectory data.

### Basic Usage

```bash
# Gemini (default)
make inference

# Gemini Pro
make inference MODEL=gemini-2.5-pro

# Ollama (local)
make inference CUSTOM_MODEL_CLASS=langchain_ollama.ChatOllama CUSTOM_MODEL_KWARGS='{"model":"llama3.2"}'

# OpenAI
make inference CUSTOM_MODEL_CLASS=langchain_openai.ChatOpenAI CUSTOM_MODEL_KWARGS='{"model":"gpt-4o-mini"}'
```

Results are saved to `evaluation/results/inference_{model}_{timestamp}.json`.

### Command Line Options

```
--question-id, -q     Run only a specific question by ID (e.g., q_001)
--category, -c        Filter by category (courses, exams, professors, etc.)
--complexity          Filter by complexity (simple, multi_step, contextual, ambiguous)
--skip-auth           Skip questions that require authentication
--output, -o          Output file path (default: auto-generated)
--stdout              Output to stdout instead of file
--pretty              Pretty-print JSON output
--limit, -l           Limit to first N questions
--model, -m           Gemini model to use (default: gemini-2.5-flash)
--custom-model-class  Custom model class path for non-Gemini models
--custom-model-kwargs JSON string of kwargs for custom model
```

### Output File Naming

By default, results are saved to `evaluation/results/` with auto-generated filenames:

| Model Type | Filename Pattern |
|------------|------------------|
| Gemini | `inference_gemini-2.5-flash_20251214_120000.json` |
| Custom | `inference_ChatOllama_llama3.2_20251214_120000.json` |

Use `--output` to specify a custom path, or `--stdout` to print to console.

### Model Selection

#### Gemini Models (Default)

Use the `--model` flag with one of the supported Gemini models:

```bash
# Default: gemini-2.5-flash
uv run python scripts/run_eval_inference.py -o results.json --pretty

# Use gemini-2.5-pro for better quality
uv run python scripts/run_eval_inference.py --model gemini-2.5-pro -o results.json --pretty

# Use gemini-2.5-flash-lite for faster/cheaper inference
uv run python scripts/run_eval_inference.py --model gemini-2.5-flash-lite -o results.json --pretty
```

Supported Gemini models:
- `gemini-2.5-flash` (default)
- `gemini-2.5-flash-lite`
- `gemini-2.5-pro`

#### Custom Models (Local/Other Providers)

Use `--custom-model-class` with `--custom-model-kwargs` for custom LangChain chat models:

**Ollama (Local Models)**
```bash
# Using Llama 3.2
uv run python scripts/run_eval_inference.py \
  --custom-model-class langchain_ollama.ChatOllama \
  --custom-model-kwargs '{"model": "llama3.2"}' \
  -o results.json --pretty

# Using Mistral with custom settings
uv run python scripts/run_eval_inference.py \
  --custom-model-class langchain_ollama.ChatOllama \
  --custom-model-kwargs '{"model": "mistral", "temperature": 0}' \
  -o results.json --pretty
```

**OpenAI**
```bash
uv run python scripts/run_eval_inference.py \
  --custom-model-class langchain_openai.ChatOpenAI \
  --custom-model-kwargs '{"model": "gpt-4o-mini", "temperature": 0}' \
  -o results.json --pretty
```

**Anthropic**
```bash
uv run python scripts/run_eval_inference.py \
  --custom-model-class langchain_anthropic.ChatAnthropic \
  --custom-model-kwargs '{"model": "claude-3-5-sonnet-20241022"}' \
  -o results.json --pretty
```

> **Note:** Ensure the required provider package is installed (e.g., `uv add langchain-ollama` for Ollama).

### Filtering Questions

```bash
# Run only course-related questions
uv run python scripts/run_eval_inference.py --category courses -o results.json --pretty

# Run only simple questions
uv run python scripts/run_eval_inference.py --complexity simple -o results.json --pretty

# Skip questions requiring authentication (public data only)
uv run python scripts/run_eval_inference.py --skip-auth -o results.json --pretty

# Run a specific question
uv run python scripts/run_eval_inference.py --question-id q_001 -o results.json --pretty

# Limit to first 5 questions (useful for testing)
uv run python scripts/run_eval_inference.py --limit 5 -o results.json --pretty
```

### Using Make

The Makefile provides convenient shortcuts:

```bash
# Run inference on all questions
make inference

# Run inference on public questions only
make inference-public

# Limit number of questions
make inference LIMIT=5

# Use a different Gemini model
make inference MODEL=gemini-2.5-pro

# Combine options
make inference-public MODEL=gemini-2.5-pro LIMIT=10
```

#### Custom Models with Make

Use `CUSTOM_MODEL_CLASS` and `CUSTOM_MODEL_KWARGS` for non-Gemini models:

```bash
# Ollama (local)
make inference \
  CUSTOM_MODEL_CLASS=langchain_ollama.ChatOllama \
  CUSTOM_MODEL_KWARGS='{"model":"llama3.2"}'

# OpenAI
make inference \
  CUSTOM_MODEL_CLASS=langchain_openai.ChatOpenAI \
  CUSTOM_MODEL_KWARGS='{"model":"gpt-4o-mini","temperature":0}'

# Anthropic
make inference \
  CUSTOM_MODEL_CLASS=langchain_anthropic.ChatAnthropic \
  CUSTOM_MODEL_KWARGS='{"model":"claude-3-5-sonnet-20241022"}'

# Custom model with limit and public-only
make inference-public \
  CUSTOM_MODEL_CLASS=langchain_ollama.ChatOllama \
  CUSTOM_MODEL_KWARGS='{"model":"mistral"}' \
  LIMIT=10
```

> **Note:** When using `CUSTOM_MODEL_CLASS`, the `MODEL` variable is ignored.

Run `make help` to see all available options.

### Output Format

Results are saved as JSON with the following structure:

```json
{
  "run_timestamp": "2025-12-14T12:00:00.000000",
  "model": {
    "type": "gemini",
    "name": "gemini-2.5-flash"
  },
  "total_questions": 20,
  "completed": 20,
  "successful": 18,
  "failed": 2,
  "results": [
    {
      "question_id": "q_001",
      "question": "What courses are available in the first semester?",
      "final_response": "Here are the courses...",
      "trajectory": [
        {"type": "human", "content": "..."},
        {"type": "ai", "content": "...", "tool_calls": [...]},
        {"type": "tool", "name": "search_courses", "content": "..."}
      ],
      "metadata": {
        "category": "courses",
        "complexity": "simple",
        "expected_tools": ["search_courses"],
        "requires_auth": false,
        "model": {"type": "gemini", "name": "gemini-2.5-flash"}
      },
      "error": null
    }
  ]
}
```

### Checkpointing

When using `--output`, results are saved after each question completes. This provides:
- Real-time progress monitoring
- Recovery from interruptions
- Partial results if the script crashes

### Examples

```bash
# Quick test with 3 questions
uv run python scripts/run_eval_inference.py --limit 3 --pretty

# Full evaluation with gemini-2.5-pro
uv run python scripts/run_eval_inference.py \
  --model gemini-2.5-pro \
  -o evaluation/results/gemini-pro-results.json \
  --pretty

# Compare local model performance
uv run python scripts/run_eval_inference.py \
  --custom-model-class langchain_ollama.ChatOllama \
  --custom-model-kwargs '{"model": "llama3.2"}' \
  --skip-auth \
  -o evaluation/results/llama-results.json \
  --pretty
```

## Evaluation Metrics

The `run_eval_metrics.py` script evaluates inference results using deepeval's GEval metrics, applying custom LLM-as-judge evaluation based on metrics defined in `evaluation/dataset/metrics.json`.

### Basic Usage

```bash
# Evaluate all metrics on inference results
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214_172328.json

# Evaluate specific metrics only
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214_172328.json METRICS=relevance,helpfulness

# Limit to first N questions
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214_172328.json LIMIT=5
```

Results are saved to `evaluation/results/evaluation_{model}_{timestamp}.json`.

### Command Line Options

```
--input, -i           Path to inference results JSON (required)
--output, -o          Output file path (default: auto-generated)
--metrics             Comma-separated metric IDs to run (default: all)
--question-id, -q     Evaluate only a specific question by ID
--model, -m           Evaluation LLM model (default: gemini/gemini-2.5-flash)
--limit, -l           Limit to first N questions
--pretty              Pretty-print JSON output
--stdout              Output to stdout instead of file
```

### Available Metrics

The following metrics are defined in `evaluation/dataset/metrics.json`:

| Metric ID | Description |
|-----------|-------------|
| `relevance` | How well the response addresses the user's query |
| `helpfulness` | Practical utility of the response for accomplishing goals |
| `conciseness` | Communication efficiency without unnecessary verbosity |
| `structure` | Information organization and formatting quality |
| `tone` | Appropriateness of communication tone for academic context |
| `error_handling` | Graceful handling of missing information or errors |
| `tool_appropriateness` | Optimal selection and usage of available tools |

### Using Make

```bash
# Run all metrics
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json

# Run specific metrics
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json METRICS=relevance,helpfulness,conciseness

# Use a different evaluation model
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json EVAL_MODEL=gemini/gemini-2.5-pro

# Combine options
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json METRICS=relevance LIMIT=5
```

### Direct Script Usage

```bash
# Basic evaluation
uv run python scripts/run_eval_metrics.py \
  -i evaluation/results/inference_gemini-2.5-flash_20251214.json \
  --pretty

# Specific metrics with custom output
uv run python scripts/run_eval_metrics.py \
  -i evaluation/results/inference_gemini-2.5-flash_20251214.json \
  --metrics relevance,helpfulness \
  -o evaluation/results/custom_eval.json \
  --pretty

# Single question evaluation
uv run python scripts/run_eval_metrics.py \
  -i evaluation/results/inference_gemini-2.5-flash_20251214.json \
  --question-id q_001 \
  --stdout --pretty
```

### Output Format

Results are saved as JSON with the following structure:

```json
{
  "eval_timestamp": "2025-12-14T18:00:00.000000",
  "inference_file": "inference_gemini-2.5-flash_20251214_172328.json",
  "eval_model": "gemini/gemini-2.5-flash",
  "metrics_evaluated": ["relevance", "helpfulness", "conciseness", "structure", "tone", "error_handling", "tool_appropriateness"],
  "total_questions": 45,
  "completed": 45,
  "summary": {
    "total_questions": 45,
    "avg_scores": {
      "relevance": 0.85,
      "helpfulness": 0.78,
      "conciseness": 0.92
    }
  },
  "results": [
    {
      "question_id": "q_001",
      "question": "How many credits is the IA course?",
      "final_response": "The course \"IA\" has 6 credits.",
      "scores": {
        "relevance": {
          "score": 0.95,
          "reason": "Response directly answers the specific question about credits..."
        },
        "helpfulness": {
          "score": 0.85,
          "reason": "Provides the exact information needed..."
        }
      }
    }
  ]
}
```

### Checkpointing

When writing to a file (not using `--stdout`), results are saved after each question completes. This provides:
- Real-time progress monitoring
- Recovery from interruptions
- Partial results if the script crashes

The `completed` field in the output shows how many questions have been evaluated so far, allowing you to track progress and identify partial runs.

### Workflow Example

A typical evaluation workflow:

```bash
# 1. Run inference on evaluation questions
make inference-public MODEL=gemini-2.5-flash

# 2. Evaluate the results (use the generated filename)
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214_172328.json

# 3. Quick test on subset first
make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214_172328.json LIMIT=5 METRICS=relevance,helpfulness
```
