"""
Script to evaluate agent inference results using deepeval GEval metrics.

Runs custom LLM-as-judge evaluation on inference results using metrics
defined in evaluation/dataset/metrics.json.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from deepeval.metrics import GEval  # noqa: E402
from deepeval.models import DeepEvalBaseLLM, GeminiModel  # noqa: E402
from deepeval.test_case import LLMTestCase, LLMTestCaseParams  # noqa: E402


class FixedGeminiModel(GeminiModel):
    """GeminiModel with fix for use_vertexai bool/str type mismatch bug in deepeval."""

    def should_use_vertexai(self) -> bool:
        # Use Vertex AI when project and location are configured
        if self.project and self.location:
            return True
        return False


METRICS_PATH = Path(__file__).parent.parent / "evaluation" / "dataset" / "metrics.json"
RESULTS_DIR = Path(__file__).parent.parent / "evaluation" / "results"


def create_model(model_str: str) -> str | DeepEvalBaseLLM:
    """Create the appropriate model instance based on the model string."""
    if model_str.startswith("gemini/"):
        model_name = model_str[len("gemini/") :]
        # API key is optional when using Vertex AI with ADC authentication
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        return FixedGeminiModel(model=model_name, api_key=api_key)
    return model_str


def load_metrics(path: Path = METRICS_PATH) -> list[dict[str, Any]]:
    """Load metric definitions from JSON file."""
    with open(path) as f:
        return json.load(f)


def load_inference_results(path: Path) -> dict[str, Any]:
    """Load inference results from JSON file."""
    with open(path) as f:
        return json.load(f)


def create_geval_metric(metric_def: dict[str, Any], model: str | DeepEvalBaseLLM) -> GEval:
    """Create a GEval metric from a metric definition."""
    criteria = f"{metric_def['persona']}\n\nCorrect behaviors:\n"
    criteria += "\n".join(f"- {item}" for item in metric_def["rubric"]["correct"])
    criteria += "\n\nIncorrect behaviors:\n"
    criteria += "\n".join(f"- {item}" for item in metric_def["rubric"]["incorrect"])

    evaluation_steps = metric_def["instructions"] + metric_def["reminder"]

    return GEval(
        name=metric_def["name"],
        criteria=criteria,
        evaluation_steps=evaluation_steps,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=model,
        threshold=0.5,
    )


def format_output_with_trajectory(result: dict[str, Any]) -> str:
    """Format output including trajectory for tool_appropriateness metric."""
    final_response = result.get("final_response") or ""
    output = f"Final Response:\n{final_response}\n\n"

    expected_tools = result.get("metadata", {}).get("expected_tools", [])
    if expected_tools:
        output += f"Expected Tools: {', '.join(expected_tools)}\n\n"

    output += "Tool Calls Made:\n"
    tool_calls_found = False
    for msg in result.get("trajectory", []):
        if msg.get("type") == "ai" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tool_calls_found = True
                args_str = json.dumps(tc.get("args", {}), ensure_ascii=False)
                output += f"- {tc['name']}({args_str})\n"

    if not tool_calls_found:
        output += "- None\n"

    return output


def create_test_case(
    result: dict[str, Any],
    include_trajectory: bool = False,
) -> LLMTestCase:
    """Create an LLMTestCase from an inference result."""
    if include_trajectory:
        actual_output = format_output_with_trajectory(result)
    else:
        final_response = result.get("final_response")
        if isinstance(final_response, list):
            actual_output = "\n".join(item.get("text", "") for item in final_response if isinstance(item, dict))
        elif isinstance(final_response, str):
            actual_output = final_response
        else:
            actual_output = ""

    return LLMTestCase(
        input=result["question"],
        actual_output=actual_output,
        additional_metadata={
            "question_id": result["question_id"],
            "category": result.get("metadata", {}).get("category"),
            "complexity": result.get("metadata", {}).get("complexity"),
        },
    )


def filter_results(
    results: list[dict[str, Any]],
    question_id: str | None = None,
) -> list[dict[str, Any]]:
    """Filter inference results based on criteria."""
    if question_id:
        return [r for r in results if r["question_id"] == question_id]
    return results


def extract_model_name(model_info: dict[str, Any]) -> str:
    """Extract a clean model name from model info dict."""
    if model_info.get("type") == "gemini":
        return model_info.get("name", "unknown")
    # Custom model - extract from kwargs
    kwargs = model_info.get("kwargs", {})
    if "model" in kwargs:
        return kwargs["model"]
    if "model_path" in kwargs:
        # Extract model name from path (e.g., "models/qwen2.5-7b-instruct-q4_k_m.gguf" -> "qwen2.5-7b-instruct")
        return Path(kwargs["model_path"]).stem.split("-q")[0]
    return "unknown"


def generate_output_filename(model_info: dict[str, Any], timestamp: datetime) -> str:
    """Generate output filename based on model info and timestamp."""
    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
    model_name = extract_model_name(model_info)
    safe_model_name = model_name.replace("/", "-").replace(":", "-")
    return f"evaluation_{safe_model_name}_{ts_str}.json"


def write_checkpoint(
    output_path: Path,
    eval_results: list[dict[str, Any]],
    inference_file: str,
    eval_model: str,
    metric_ids: list[str],
    total: int,
    pretty: bool,
) -> None:
    """Write current results to checkpoint file."""
    summary = compute_summary(eval_results, metric_ids)
    output = {
        "eval_timestamp": datetime.now().isoformat(),
        "inference_file": inference_file,
        "eval_model": eval_model,
        "metrics_evaluated": metric_ids,
        "total_questions": total,
        "completed": len(eval_results),
        "summary": summary,
        "results": eval_results,
    }
    indent = 2 if pretty else None
    with open(output_path, "w") as f:
        json.dump(output, f, indent=indent, ensure_ascii=False, default=str)


def run_evaluation(
    results: list[dict[str, Any]],
    metric_defs: list[dict[str, Any]],
    model: str | DeepEvalBaseLLM,
    output_path: Path | None = None,
    inference_file: str = "",
    pretty: bool = False,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Run evaluation on all results with all metrics."""
    eval_results = []
    metric_ids = [m["id"] for m in metric_defs]
    total = len(results)

    model_instance = create_model(model) if isinstance(model, str) else model

    for i, result in enumerate(results, 1):
        question_id = result.get("question_id", f"unknown_{i}")
        try:
            if verbose:
                print(f"[{i}/{total}] Evaluating: {question_id}", file=sys.stderr)

            question_scores = {
                "question_id": question_id,
                "question": result.get("question", ""),
                "final_response": result.get("final_response"),
                "scores": {},
            }

            for metric_def in metric_defs:
                metric_id = metric_def["id"]
                metric_name = metric_def["name"]

                include_trajectory = metric_id == "tool_appropriateness"
                test_case = create_test_case(result, include_trajectory=include_trajectory)

                geval_metric = create_geval_metric(metric_def, model_instance)

                try:
                    geval_metric.measure(test_case)
                    question_scores["scores"][metric_id] = {
                        "score": geval_metric.score,
                        "reason": geval_metric.reason,
                    }
                    if verbose:
                        print(f"  {metric_name}: {geval_metric.score:.2f}", file=sys.stderr)
                except Exception as e:
                    question_scores["scores"][metric_id] = {
                        "score": None,
                        "reason": None,
                        "error": str(e),
                    }
                    if verbose:
                        print(f"  {metric_name}: ERROR - {e}", file=sys.stderr)

            eval_results.append(question_scores)
        except Exception as e:
            if verbose:
                print(f"[{i}/{total}] SKIPPED {question_id}: {e}", file=sys.stderr)
            eval_results.append(
                {
                    "question_id": question_id,
                    "question": result.get("question", ""),
                    "final_response": result.get("final_response"),
                    "scores": {},
                    "error": str(e),
                }
            )

        if output_path:
            write_checkpoint(output_path, eval_results, inference_file, model, metric_ids, total, pretty)

    return eval_results


def compute_summary(
    eval_results: list[dict[str, Any]],
    metric_ids: list[str],
) -> dict[str, Any]:
    """Compute summary statistics from evaluation results."""
    avg_scores = {}
    for metric_id in metric_ids:
        scores = [r["scores"][metric_id]["score"] for r in eval_results if r["scores"].get(metric_id, {}).get("score") is not None]
        if scores:
            avg_scores[metric_id] = sum(scores) / len(scores)

    return {
        "total_questions": len(eval_results),
        "avg_scores": avg_scores,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate agent inference results using deepeval metrics")
    parser.add_argument("--input", "-i", required=True, help="Path to inference results JSON file")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated)")
    parser.add_argument("--metrics", help="Comma-separated metric IDs to run (default: all)")
    parser.add_argument("--question-id", "-q", help="Evaluate only a specific question by ID")
    parser.add_argument("--model", "-m", default="gemini/gemini-2.5-flash", help="Evaluation LLM model (default: gemini/gemini-2.5-flash)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--stdout", action="store_true", help="Output to stdout instead of file")
    parser.add_argument("--limit", "-l", type=int, help="Limit to first N questions")

    args = parser.parse_args()

    inference_path = Path(args.input)
    if not inference_path.exists():
        print(f"Error: Input file not found: {inference_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading inference results from: {inference_path}", file=sys.stderr)
    inference_data = load_inference_results(inference_path)
    results = inference_data.get("results", [])

    results = filter_results(results, question_id=args.question_id)

    if args.limit:
        results = results[: args.limit]

    if not results:
        print("No results to evaluate.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading metrics from: {METRICS_PATH}", file=sys.stderr)
    all_metrics = load_metrics()

    if args.metrics:
        selected_ids = [m.strip() for m in args.metrics.split(",")]
        metric_defs = [m for m in all_metrics if m["id"] in selected_ids]
        if not metric_defs:
            print(f"Error: No valid metrics found in: {args.metrics}", file=sys.stderr)
            print(f"Available: {', '.join(m['id'] for m in all_metrics)}", file=sys.stderr)
            sys.exit(1)
    else:
        metric_defs = all_metrics

    metric_ids = [m["id"] for m in metric_defs]
    print(f"Evaluating {len(results)} results with metrics: {', '.join(metric_ids)}", file=sys.stderr)
    print(f"Using model: {args.model}", file=sys.stderr)

    run_timestamp = datetime.now()

    if args.stdout:
        output_path = None
    elif args.output:
        output_path = Path(args.output)
    else:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        model_info = inference_data.get("model", {})
        output_path = RESULTS_DIR / generate_output_filename(model_info, run_timestamp)

    if output_path:
        print(f"Results will be saved to: {output_path}", file=sys.stderr)

    eval_results = run_evaluation(
        results,
        metric_defs,
        args.model,
        output_path=output_path,
        inference_file=inference_path.name,
        pretty=args.pretty,
    )

    summary = compute_summary(eval_results, metric_ids)

    output = {
        "eval_timestamp": run_timestamp.isoformat(),
        "inference_file": str(inference_path.name),
        "eval_model": args.model,
        "metrics_evaluated": metric_ids,
        "total_questions": len(results),
        "completed": len(eval_results),
        "summary": summary,
        "results": eval_results,
    }

    indent = 2 if args.pretty else None
    json_output = json.dumps(output, indent=indent, ensure_ascii=False, default=str)

    if args.stdout:
        print(json_output)
    else:
        print(f"Results written to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
