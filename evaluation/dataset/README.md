# FIB Agent Evaluation Dataset

This directory contains evaluation datasets for the FIB (Facultat d'Informàtica de Barcelona) conversational agent. The evaluation uses an **LLM-as-judge** approach to assess agent response quality.

## Evaluation Philosophy

Rather than validating specific API data (which changes over time), this evaluation focuses on **conversational agent quality**. The judge LLM rates responses on multiple quality dimensions, outputting a float score between 0.0 and 1.0 for each metric.

## Dataset Files

| File | Description |
|------|-------------|
| `questions.json` | 45 sample questions across various categories and complexity levels |
| `metrics.json` | 7 evaluation metrics with descriptive rubrics |

## Question Format

Each question in `questions.json` follows this schema:

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

### Fields

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `question` | The user's natural language question |
| `category` | Question category (see below) |
| `complexity` | Complexity level (see below) |
| `expected_tools` | Tools the agent should likely use |
| `requires_auth` | Whether the query needs user authentication |
| `notes` | Additional context for evaluation |

### Categories

| Category | Description | Example Tools |
|----------|-------------|---------------|
| `courses` | Course information queries | search_courses, get_course_details |
| `exams` | Exam schedules and rooms | search_exams, get_upcoming_exams |
| `professors` | Faculty information | search_professors |
| `news` | FIB announcements | get_fib_news |
| `academic` | Terms and semesters | get_academic_terms, get_current_term |
| `classrooms` | Room information | list_classrooms |
| `personal` | User-specific queries | get_my_courses, get_my_schedule |
| `multi_tool` | Complex multi-aspect queries | Multiple tools |
| `web_search` | External information | internet_search |
| `ambiguous` | Vague queries needing clarification | — |

### Complexity Levels

| Level | Description |
|-------|-------------|
| `simple` | Single tool, direct answer |
| `multi_step` | Requires multiple tools or reasoning steps |
| `contextual` | Requires user context (enrolled courses, schedule) |
| `ambiguous` | Intentionally vague to test clarification behavior |

## Metrics Format

Each metric in `metrics.json` has a descriptive rubric:

```json
{
  "id": "relevance",
  "name": "Relevance",
  "rubric": "Measures how well the response addresses the user's actual question..."
}
```

The judge LLM reads the rubric and outputs a **float score between 0.0 and 1.0**.

### Metrics

| Metric | What it measures |
|--------|------------------|
| **Relevance** | Does the response address the user's question? |
| **Helpfulness** | Is the response actionable and useful? |
| **Conciseness** | Is it appropriately brief without losing information? |
| **Structure** | Is the response well-organized with appropriate formatting? |
| **Tone** | Is the tone professional and appropriate? |
| **Error Handling** | How gracefully does it handle missing data or failures? |
| **Tool Appropriateness** | Did it select and use the right tools? |

## Evaluation Workflow

1. **Load questions** from `questions.json`
2. **Run agent** on each question to get responses
3. **Judge responses** using an LLM with metrics from `metrics.json`
4. **Aggregate scores** across all questions and metrics

### Example Judge Prompt

```
You are evaluating a conversational AI assistant for FIB university.

## Question
{question}

## Agent Response
{response}

## Metric: {metric_name}
{metric_rubric}

Based on the rubric above, rate the response from 0.0 to 1.0.
Output only a JSON object: {"score": <float>, "reasoning": "<brief explanation>"}
```

## Notes

- Questions marked `requires_auth: true` need user authentication to test properly
- Questions in the `ambiguous` category test the agent's clarification behavior
- The `expected_tools` field is for reference; agents may use different valid approaches
- Scores are not compared against "golden answers" since API data is dynamic
