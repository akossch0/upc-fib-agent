.PHONY: auth inference inference-public evaluate help

# Optional limit for number of questions (e.g., make inference LIMIT=5)
LIMIT ?=
LIMIT_FLAG := $(if $(LIMIT),--limit $(LIMIT),)

# Resume from existing file (e.g., make inference RESUME=path/to/file.json)
RESUME ?=
RESUME_FLAG := $(if $(RESUME),--resume $(RESUME),)

# Evaluation settings
INPUT ?=
INPUT_FLAG := $(if $(INPUT),-i $(INPUT),)
METRICS ?=
METRICS_FLAG := $(if $(METRICS),--metrics $(METRICS),)
EVAL_MODEL ?= gemini/gemini-2.5-flash-lite

# Model selection (default: gemini-2.5-flash)
# For Gemini: MODEL=gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro
# For custom: CUSTOM_MODEL_CLASS=langchain_ollama.ChatOllama CUSTOM_MODEL_KWARGS='{"model":"llama3.2"}'
MODEL ?= gemini-2.5-flash
CUSTOM_MODEL_CLASS ?=
CUSTOM_MODEL_KWARGS ?= {}

# Build model flags based on whether custom model is specified
ifdef CUSTOM_MODEL_CLASS
MODEL_FLAGS := --custom-model-class $(CUSTOM_MODEL_CLASS) --custom-model-kwargs '$(CUSTOM_MODEL_KWARGS)'
else
MODEL_FLAGS := --model $(MODEL)
endif

help:
	@echo "Available targets:"
	@echo "  auth             - Authenticate with FIB API using OAuth"
	@echo "  inference        - Run agent inference on all questions"
	@echo "  inference-public - Run inference on public questions only (skip auth-required)"
	@echo "  evaluate         - Run deepeval metrics on inference results"
	@echo ""
	@echo "Inference Options:"
	@echo "  LIMIT=N                  - Limit to first N questions"
	@echo "  RESUME=path              - Resume from existing inference file"
	@echo "  MODEL=name               - Gemini model (default: gemini-2.5-flash)"
	@echo "                             Options: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro"
	@echo "  CUSTOM_MODEL_CLASS=path  - Custom model class (e.g., langchain_ollama.ChatOllama)"
	@echo "  CUSTOM_MODEL_KWARGS=json - Custom model kwargs as JSON string"
	@echo ""
	@echo "Evaluation Options:"
	@echo "  INPUT=path               - Path to inference results JSON (required for evaluate)"
	@echo "  METRICS=ids              - Comma-separated metric IDs (default: all)"
	@echo "  EVAL_MODEL=name          - Evaluation LLM model (default: gemini/gemini-2.5-flash)"
	@echo "  LIMIT=N                  - Limit to first N questions"
	@echo ""
	@echo "Examples:"
	@echo "  make inference MODEL=gemini-2.5-pro LIMIT=5"
	@echo "  make inference RESUME=evaluation/results/inference_gemini-2.5-pro_20251214.json"
	@echo "  make inference CUSTOM_MODEL_CLASS=langchain_ollama.ChatOllama CUSTOM_MODEL_KWARGS='{\"model\":\"llama3.2\"}'"
	@echo "  make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json"
	@echo "  make evaluate INPUT=evaluation/results/inference_gemini-2.5-flash_20251214.json METRICS=relevance,helpfulness"
	@echo ""
	@echo "Results are saved to evaluation/results/"

auth:
	uv run python scripts/authenticate.py

inference:
	uv run python scripts/run_eval_inference.py --pretty $(LIMIT_FLAG) $(RESUME_FLAG) $(MODEL_FLAGS)

inference-public:
	uv run python scripts/run_eval_inference.py --skip-auth --pretty $(LIMIT_FLAG) $(RESUME_FLAG) $(MODEL_FLAGS)

evaluate:
ifndef INPUT
	$(error INPUT is required. Usage: make evaluate INPUT=path/to/inference_results.json)
endif
	uv run python scripts/run_eval_metrics.py $(INPUT_FLAG) --model $(EVAL_MODEL) --pretty $(LIMIT_FLAG) $(METRICS_FLAG)
