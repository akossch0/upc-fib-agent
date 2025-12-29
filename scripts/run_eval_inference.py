"""
Script to run agent inference on evaluation questions.

Runs the FIB agent on questions from the evaluation dataset and outputs
the final response along with trajectory data (tool calls and results).
"""

import argparse
import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent.main import GEMINI_MODELS, CustomModelStrategy, create_fib_agent

QUESTIONS_PATH = Path(__file__).parent.parent / "evaluation" / "dataset" / "questions.json"
RESULTS_DIR = Path(__file__).parent.parent / "evaluation" / "results"


def generate_output_filename(model_info: dict[str, Any], timestamp: datetime) -> str:
    """Generate a default output filename based on model and timestamp."""
    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")

    if model_info["type"] == "gemini":
        model_name = model_info["name"]
    else:
        class_name = model_info["class"].split(".")[-1]
        kwargs = model_info["kwargs"]
        if "model" in kwargs:
            model_kwarg = kwargs["model"]
        elif "model_path" in kwargs:
            # Extract model name from path (e.g., "models/qwen2.5-7b-instruct.gguf" -> "qwen2.5-7b-instruct")
            model_kwarg = Path(kwargs["model_path"]).stem.split("-q")[0]  # Remove quantization suffix
        else:
            model_kwarg = "unknown"
        model_name = f"{class_name}_{model_kwarg}"

    safe_model_name = model_name.replace("/", "-").replace(":", "-")
    return f"inference_{safe_model_name}_{ts_str}.json"


def load_custom_model(class_path: str, model_kwargs: dict[str, Any]) -> BaseChatModel:
    """Load a custom model class from an import path."""
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    model_class = getattr(module, class_name)
    return model_class(**model_kwargs)


def load_questions(path: Path = QUESTIONS_PATH) -> list[dict[str, Any]]:
    """Load questions from the evaluation dataset."""
    with open(path) as f:
        return json.load(f)


def filter_questions(
    questions: list[dict[str, Any]],
    question_id: str | None = None,
    category: str | None = None,
    complexity: str | None = None,
    skip_auth: bool = False,
) -> list[dict[str, Any]]:
    """Filter questions based on criteria."""
    filtered = questions

    if question_id:
        filtered = [q for q in filtered if q["id"] == question_id]

    if category:
        filtered = [q for q in filtered if q["category"] == category]

    if complexity:
        filtered = [q for q in filtered if q["complexity"] == complexity]

    if skip_auth:
        filtered = [q for q in filtered if not q.get("requires_auth", False)]

    return filtered


def extract_text_from_content(content: Any) -> str:
    """Extract text from AIMessage content which may be a string or list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "\n".join(text_parts)
    return str(content)


def extract_message(msg: Any) -> dict[str, Any]:
    """Extract relevant fields from a LangChain message."""
    if isinstance(msg, HumanMessage):
        return {
            "type": "human",
            "content": msg.content,
        }
    elif isinstance(msg, AIMessage):
        result = {
            "type": "ai",
            "content": extract_text_from_content(msg.content),
        }
        if msg.tool_calls:
            result["tool_calls"] = [{"name": tc["name"], "args": tc["args"]} for tc in msg.tool_calls]
        return result
    elif isinstance(msg, ToolMessage):
        return {
            "type": "tool",
            "name": msg.name,
            "content": msg.content,
        }
    else:
        return {
            "type": msg.__class__.__name__.lower(),
            "content": str(msg.content) if hasattr(msg, "content") else str(msg),
        }


def extract_trajectory(messages: list[Any]) -> list[dict[str, Any]]:
    """Extract trajectory from agent messages."""
    return [extract_message(msg) for msg in messages]


def get_final_response(messages: list[Any]) -> str:
    """Get the final AI response from messages."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return extract_text_from_content(msg.content)
    return ""


def run_inference(question: dict[str, Any], agent: Any, model_info: dict[str, Any]) -> dict[str, Any]:
    """Run agent inference on a single question."""
    question_text = question["question"]

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": question_text}]})

        messages = result.get("messages", [])
        trajectory = extract_trajectory(messages)
        final_response = get_final_response(messages)

        return {
            "question_id": question["id"],
            "question": question_text,
            "final_response": final_response,
            "trajectory": trajectory,
            "metadata": {
                "category": question.get("category"),
                "complexity": question.get("complexity"),
                "expected_tools": question.get("expected_tools", []),
                "requires_auth": question.get("requires_auth", False),
                "model": model_info,
            },
            "error": None,
        }
    except Exception as e:
        return {
            "question_id": question["id"],
            "question": question_text,
            "final_response": None,
            "trajectory": [],
            "metadata": {
                "category": question.get("category"),
                "complexity": question.get("complexity"),
                "expected_tools": question.get("expected_tools", []),
                "requires_auth": question.get("requires_auth", False),
                "model": model_info,
            },
            "error": str(e),
        }


def write_checkpoint(
    output_path: Path,
    results: list[dict[str, Any]],
    model_info: dict[str, Any],
    total: int,
    pretty: bool,
) -> None:
    """Write current results to checkpoint file."""
    output = {
        "run_timestamp": datetime.now().isoformat(),
        "model": model_info,
        "total_questions": total,
        "completed": len(results),
        "successful": sum(1 for r in results if r["error"] is None),
        "failed": sum(1 for r in results if r["error"] is not None),
        "results": results,
    }
    indent = 2 if pretty else None
    with open(output_path, "w") as f:
        json.dump(output, f, indent=indent, ensure_ascii=False, default=str)


def load_existing_results(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Load existing results from a checkpoint file."""
    if not path.exists():
        return [], None
    with open(path) as f:
        data = json.load(f)
    return data.get("results", []), data.get("model")


def main():
    parser = argparse.ArgumentParser(description="Run agent inference on evaluation questions")
    parser.add_argument("--question-id", "-q", help="Run only a specific question by ID (e.g., q_001)")
    parser.add_argument("--category", "-c", help="Filter by category (e.g., courses, exams, professors)")
    parser.add_argument("--complexity", help="Filter by complexity (simple, multi_step, contextual, ambiguous)")
    parser.add_argument("--skip-auth", action="store_true", help="Skip questions that require authentication")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated with model name and timestamp)")
    parser.add_argument("--resume", "-r", help="Resume from an existing inference file (skips already completed questions)")
    parser.add_argument("--stdout", action="store_true", help="Output to stdout instead of file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--limit", "-l", type=int, help="Limit to first N questions")

    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--model", "-m", default="gemini-2.5-flash", choices=sorted(GEMINI_MODELS), help="Gemini model to use (default: gemini-2.5-flash)"
    )
    model_group.add_argument("--custom-model-class", help="Custom model class path (e.g., langchain_ollama.ChatOllama)")
    parser.add_argument("--custom-model-kwargs", default="{}", help='JSON string of kwargs for custom model (e.g., \'{"model": "llama3.2"}\')')

    args = parser.parse_args()

    existing_results = []
    completed_ids: set[str] = set()

    if args.resume:
        resume_path = Path(args.resume)
        existing_results, existing_model = load_existing_results(resume_path)
        completed_ids = {r["question_id"] for r in existing_results}
        print(f"Resuming from {resume_path} ({len(completed_ids)} questions already completed)", file=sys.stderr)

    questions = load_questions()
    questions = filter_questions(
        questions,
        question_id=args.question_id,
        category=args.category,
        complexity=args.complexity,
        skip_auth=args.skip_auth,
    )

    if args.limit:
        questions = questions[: args.limit]

    if not questions:
        print("No questions match the specified filters.", file=sys.stderr)
        sys.exit(1)

    run_timestamp = datetime.now()

    if args.custom_model_class:
        model_kwargs = json.loads(args.custom_model_kwargs)
        print(f"Loading custom model: {args.custom_model_class}", file=sys.stderr)
        print(f"  kwargs: {model_kwargs}", file=sys.stderr)
        custom_model = load_custom_model(args.custom_model_class, model_kwargs)
        strategy = CustomModelStrategy(custom_model)
        agent = create_fib_agent(model=strategy)
        model_info = {
            "type": "custom",
            "class": args.custom_model_class,
            "kwargs": model_kwargs,
        }
    else:
        print(f"Creating agent with model: {args.model}", file=sys.stderr)
        agent = create_fib_agent(model=args.model)
        model_info = {
            "type": "gemini",
            "name": args.model,
        }

    if args.resume:
        output_path = Path(args.resume)
    elif args.stdout:
        output_path = None
    elif args.output:
        output_path = Path(args.output)
    else:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = RESULTS_DIR / generate_output_filename(model_info, run_timestamp)

    if output_path:
        print(f"Results will be saved to: {output_path}", file=sys.stderr)

    results = list(existing_results)
    total = len(questions)
    remaining = [q for q in questions if q["id"] not in completed_ids]
    print(f"Running {len(remaining)} remaining questions out of {total} total", file=sys.stderr)

    for i, question in enumerate(remaining, len(completed_ids) + 1):
        print(f"[{i}/{total}] Running: {question['id']} - {question['question'][:50]}...", file=sys.stderr)
        result = run_inference(question, agent, model_info)
        results.append(result)

        if result["error"]:
            print(f"  Error: {result['error']}", file=sys.stderr)
        else:
            print("  Done.", file=sys.stderr)

        if output_path:
            write_checkpoint(output_path, results, model_info, total, args.pretty)

    output = {
        "run_timestamp": run_timestamp.isoformat(),
        "model": model_info,
        "total_questions": total,
        "completed": len(results),
        "successful": sum(1 for r in results if r["error"] is None),
        "failed": sum(1 for r in results if r["error"] is not None),
        "results": results,
    }

    indent = 2 if args.pretty else None
    json_output = json.dumps(output, indent=indent, ensure_ascii=False, default=str)

    if output_path:
        print(f"Results written to {output_path}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
