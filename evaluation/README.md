# FIB Agent Evaluation

This directory contains the evaluation framework for the FIB conversational agent.

## Quick Start

End-to-end example evaluating `gemini-2.5-pro`:

```bash
# 1. Run inference (generates trajectories for all questions)
make inference MODEL=gemini-2.5-pro

# Output: evaluation/results/inference_gemini-2.5-pro_<timestamp>.json

# 2. Run evaluation (scores the inference results)
make evaluate INPUT=evaluation/results/inference_gemini-2.5-pro_<timestamp>.json

# Output: evaluation/results/evaluation_gemini-2.5-pro_<timestamp>_<eval_timestamp>.json

# 3. View results in the dashboard
cd evaluation && python -m http.server 8000
# Open: http://localhost:8000/visualize.html
```

See `make help` for all options.

## Structure

```
evaluation/
├── README.md           # This file
├── visualize.html      # Interactive dashboard for single evaluation
├── compare.html        # Compare multiple evaluations side-by-side
├── dataset/
│   ├── questions.json  # Test questions (45 samples)
│   ├── metrics.json    # Evaluation metrics definitions
│   └── README.md       # Dataset documentation
└── results/
    ├── inference_*.json    # Raw inference outputs (questions + trajectories)
    └── evaluation_*.json   # Evaluated results with scores
```

## Dataset Overview

The evaluation uses an **LLM-as-judge** approach to assess agent response quality, focusing on conversational quality rather than validating specific API data (which changes over time).

### Question Schema

```json
{
  "id": "q_001",
  "question": "How many credits is the IA course?",
  "category": "courses",
  "complexity": "simple",
  "expected_tools": ["search_courses"],
  "requires_auth": false,
  "notes": "Single tool, direct factual question"
}
```

### Categories

| Category | Description |
|----------|-------------|
| `courses` | Course information queries |
| `exams` | Exam schedules and rooms |
| `professors` | Faculty information |
| `news` | FIB announcements |
| `academic` | Terms and semesters |
| `classrooms` | Room information |
| `personal` | User-specific queries (requires auth) |
| `multi_tool` | Complex multi-aspect queries |
| `ambiguous` | Vague queries needing clarification |

### Complexity Levels

| Level | Description |
|-------|-------------|
| `simple` | Single tool, direct answer |
| `multi_step` | Requires multiple tools or reasoning steps |
| `contextual` | Requires user context (enrolled courses, schedule) |
| `ambiguous` | Intentionally vague to test clarification behavior |

See `dataset/README.md` for detailed documentation.

## Visualization Dashboard

The `visualize.html` file provides an interactive dashboard to explore evaluation results.

### Features

- **Summary Cards**: Overall score, model info, best/worst metrics
- **Charts**: 
  - Scores by metric (bar chart)
  - Scores by category (horizontal bar)
  - Score distribution histogram
  - Scores by complexity level
- **Insights**: Top/bottom performing questions, metrics ranking
- **Heatmap**: Visual score matrix across questions and metrics
- **Results Explorer**: Searchable, filterable, sortable table
- **Detail Modal**: Click any question to see:
  - Full question and response
  - Score breakdown with reasoning
  - Full trajectory (human → AI → tool interactions)
  - Metadata (category, complexity, expected tools)
- **Dark/Light Mode**: Toggle with 🌓 button

### Running the Dashboard

Since the visualization loads JSON files, you need to serve it from a web server (browsers block local file access).

**Option 1: Python HTTP Server (recommended)**

```bash
# Navigate to the results directory
cd evaluation/results

# Start a simple HTTP server
python -m http.server 8000

# Open in browser
# http://localhost:8000/visualize.html
```

Or serve from the evaluation directory:

```bash
cd evaluation
python -m http.server 8000
# Open: http://localhost:8000/visualize.html?eval=results/evaluation_*.json&inference=results/inference_*.json
```

**Option 2: Using npx serve**

```bash
cd evaluation/results
npx serve -p 8000
```

**Option 3: VS Code Live Server**

1. Install the "Live Server" extension
2. Right-click `visualize.html`
3. Select "Open with Live Server"

### URL Parameters

The dashboard accepts two URL parameters to specify which files to visualize:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `eval` | Path to evaluation results JSON | (first found eval file) |
| `inference` | Path to inference results JSON | (first found inference file) |

**Examples:**

```
# Default files (when served from results directory)
http://localhost:8000/visualize.html

# Specific files
http://localhost:8000/visualize.html?eval=evaluation_gemini-2.5-flash_20251214_172328_20251214_181109.json&inference=inference_gemini-2.5-flash_20251214_172328.json

# With relative paths (when served from evaluation directory)
http://localhost:8000/visualize.html?eval=results/evaluation_model_timestamp.json&inference=results/inference_model_timestamp.json
```

### Quick Start

```bash
# From the evaluation directory
cd evaluation
python -m http.server 8000

# Open dashboard: http://localhost:8000/visualize.html
# Open compare:   http://localhost:8000/compare.html
```

## Comparison Page

The `compare.html` page allows you to compare multiple evaluation runs side-by-side.

### Features

- **Multi-select**: Check multiple evaluations to compare
- **Radar Chart**: Overlay of all metrics for visual comparison
- **Grouped Bar Charts**: Side-by-side bars for each metric
- **Score Distribution**: How scores are distributed across evaluations
- **Category Breakdown**: Performance by question category
- **Detailed Table**: Metrics comparison with best/worst highlighting
- **Question-level Diffs**: See which questions improved or regressed
  - Biggest Gaps: Largest absolute differences
  - Most Improved: Questions that got better
  - Regressed: Questions that got worse

### Usage

1. Open `http://localhost:8000/compare.html`
2. Select 2 or more evaluations by clicking the checkboxes
3. Click "Compare Selected"
4. Explore the charts and tables

### Navigation

- Click **⚖️ Compare** in the dashboard header to go to comparison
- Click **📊 Dashboard** in the comparison header to go back

## Running Evaluations

See the `scripts/` directory for evaluation scripts:

- `scripts/run_eval_metrics.py` - Run LLM-as-judge evaluation on inference results

## Metrics

The evaluation uses 7 metrics (see `dataset/metrics.json` for full rubrics):

| Metric | Description |
|--------|-------------|
| Relevance | Does the response address the user's question? |
| Helpfulness | Is the response actionable and useful? |
| Conciseness | Is it appropriately brief without losing information? |
| Structure | Is the response well-organized with appropriate formatting? |
| Tone | Is the tone professional and appropriate? |
| Error Handling | How gracefully does it handle missing data or failures? |
| Tool Appropriateness | Did it select and use the right tools? |
