"""
Temporary script to analyze evaluation results and find potential grading issues.

Usage:
    python analysis_script.py <evaluation_file>

Example:
    python analysis_script.py results/evaluation_gemini-2.5-flash_20251214_172328_20251214_181109.json
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def get_available_evaluation_files() -> list[Path]:
    """Return list of evaluation JSON files in the results directory."""
    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        return []
    return sorted(results_dir.glob("evaluation_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_data(eval_file: Path) -> dict:
    if not eval_file.exists():
        print(f"Error: Evaluation file not found: {eval_file}", file=sys.stderr)
        available = get_available_evaluation_files()
        if available:
            print("\nAvailable evaluation files:", file=sys.stderr)
            for f in available:
                print(f"  - {f.name}", file=sys.stderr)
        sys.exit(1)

    with open(eval_file) as f:
        return json.load(f)


def analyze_error_handling_issues(data):
    """Find cases where error_handling scored low (0.1) for factual responses."""
    print("\n" + "=" * 80)
    print("POTENTIAL ERROR_HANDLING METRIC ISSUES")
    print("=" * 80)

    low_error_handling = []
    for r in data["results"]:
        eh = r["scores"].get("error_handling", {})
        score = eh.get("score")
        reason = eh.get("reason", "")

        if score is not None and score <= 0.15:
            # Check if reason mentions "factual" or "no error handling needed"
            if "factual" in reason.lower() or "no error" in reason.lower():
                low_error_handling.append(
                    {
                        "question_id": r["question_id"],
                        "question": r["question"],
                        "score": score,
                        "reason": reason[:200],
                    }
                )

    print(f"\nFound {len(low_error_handling)} cases where error_handling scored ≤0.15 despite factual response:")
    for item in low_error_handling[:10]:
        print(f"\n  {item['question_id']}: {item['question'][:60]}...")
        print(f"    Score: {item['score']}")
        print(f"    Reason: {item['reason'][:150]}...")


def analyze_ambiguous_query_handling(data):
    """Find cases where ambiguous queries were penalized for appropriate clarification."""
    print("\n" + "=" * 80)
    print("AMBIGUOUS QUERY HANDLING ANALYSIS")
    print("=" * 80)

    ambiguous_ids = ["q_036", "q_037", "q_038", "q_039"]

    for r in data["results"]:
        if r["question_id"] in ambiguous_ids:
            print(f"\n{r['question_id']}: '{r['question']}'")
            print(f"  Response preview: {str(r.get('final_response'))[:150]}...")
            print("  Scores:")
            for metric, val in r["scores"].items():
                if val.get("score") is not None:
                    print(f"    {metric}: {val['score']:.2f} - {val.get('reason', '')[:80]}...")


def analyze_relevance_helpfulness_discrepancies(data):
    """Find cases with very low relevance/helpfulness but potentially good responses."""
    print("\n" + "=" * 80)
    print("LOW RELEVANCE/HELPFULNESS ANALYSIS")
    print("=" * 80)

    issues = []
    for r in data["results"]:
        rel = r["scores"].get("relevance", {}).get("score")
        help_score = r["scores"].get("helpfulness", {}).get("score")
        tone = r["scores"].get("tone", {}).get("score")
        structure = r["scores"].get("structure", {}).get("score")

        # If tone and structure are high but relevance/helpfulness are very low - potential issue
        if rel is not None and help_score is not None and tone is not None and structure is not None:
            if (rel < 0.1 or help_score < 0.1) and tone > 0.7 and structure > 0.6:
                issues.append(
                    {
                        "question_id": r["question_id"],
                        "question": r["question"],
                        "relevance": rel,
                        "helpfulness": help_score,
                        "tone": tone,
                        "structure": structure,
                        "response": str(r.get("final_response"))[:200],
                    }
                )

    print(f"\nFound {len(issues)} cases with low rel/help but high tone/structure:")
    for item in issues:
        print(f"\n  {item['question_id']}: {item['question'][:50]}...")
        print(f"    relevance={item['relevance']:.2f}, helpfulness={item['helpfulness']:.2f}")
        print(f"    tone={item['tone']:.2f}, structure={item['structure']:.2f}")
        print(f"    Response: {item['response'][:150]}...")


def analyze_by_category(data):
    """Analyze scores grouped by category."""
    print("\n" + "=" * 80)
    print("ANALYSIS BY CATEGORY")
    print("=" * 80)

    # Load questions to get categories
    questions_file = Path(__file__).parent / "dataset" / "questions.json"
    with open(questions_file) as f:
        questions = {q["id"]: q for q in json.load(f)}

    categories = defaultdict(lambda: defaultdict(list))

    for r in data["results"]:
        qid = r["question_id"]
        category = questions.get(qid, {}).get("category", "unknown")

        for metric, val in r["scores"].items():
            if val.get("score") is not None:
                categories[category][metric].append(val["score"])

    print("\nAverage scores by category and metric:\n")
    header = f"{'Category':<15}"
    metrics = ["relevance", "helpfulness", "conciseness", "structure", "tone", "error_handling", "tool_appropriateness"]
    for m in metrics:
        header += f"{m[:8]:<10}"
    print(header)
    print("-" * len(header))

    for category in sorted(categories.keys()):
        row = f"{category:<15}"
        for m in metrics:
            scores = categories[category].get(m, [])
            if scores:
                avg = sum(scores) / len(scores)
                row += f"{avg:.2f}      "
            else:
                row += "N/A       "
        print(row)


def analyze_score_inconsistencies(data):
    """Find responses with very inconsistent scores across metrics."""
    print("\n" + "=" * 80)
    print("SCORE INCONSISTENCIES (high variance)")
    print("=" * 80)

    inconsistent = []
    for r in data["results"]:
        scores = []
        for _metric, val in r["scores"].items():
            if val.get("score") is not None:
                scores.append(val["score"])

        if len(scores) >= 4:
            avg = sum(scores) / len(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)

            # High variance suggests inconsistent grading
            if variance > 0.15:  # threshold
                inconsistent.append(
                    {
                        "question_id": r["question_id"],
                        "question": r["question"][:50],
                        "variance": variance,
                        "scores": {m: v.get("score") for m, v in r["scores"].items() if v.get("score") is not None},
                    }
                )

    inconsistent.sort(key=lambda x: x["variance"], reverse=True)

    print("\nTop 10 responses with highest score variance:")
    for item in inconsistent[:10]:
        print(f"\n  {item['question_id']}: {item['question']}...")
        print(f"    Variance: {item['variance']:.3f}")
        for m, s in item["scores"].items():
            print(f"      {m}: {s:.2f}")


def analyze_specific_questions(data):
    """Deep dive into specific questions that look problematic."""
    print("\n" + "=" * 80)
    print("SPECIFIC QUESTION DEEP DIVE")
    print("=" * 80)

    # Questions to investigate
    problematic_ids = ["q_005", "q_012", "q_013", "q_033", "q_036", "q_037", "q_038"]

    for r in data["results"]:
        if r["question_id"] in problematic_ids:
            print(f"\n{'=' * 60}")
            print(f"Question ID: {r['question_id']}")
            print(f"Question: {r['question']}")
            print("\nResponse preview:")
            resp = r.get("final_response")
            if isinstance(resp, list):
                resp_text = resp[0].get("text", "") if resp else ""
            else:
                resp_text = str(resp)
            print(f"  {resp_text[:300]}...")

            print("\nScores:")
            for metric, val in r["scores"].items():
                score = val.get("score", "N/A")
                reason = val.get("reason", "")[:100]
                print(f"  {metric}: {score}")
                print(f"    Reason: {reason}...")


def main():
    parser = argparse.ArgumentParser(description="Analyze evaluation results and find potential grading issues.")
    parser.add_argument(
        "evaluation_file",
        type=Path,
        help="Path to the evaluation JSON file (e.g., results/evaluation_*.json)",
    )
    args = parser.parse_args()

    eval_file = args.evaluation_file
    if not eval_file.is_absolute():
        eval_file = Path(__file__).parent / eval_file

    data = load_data(eval_file)
    print(f"Loaded {len(data['results'])} evaluation results from {args.evaluation_file}")
    print(f"Summary scores: {data['summary']['avg_scores']}")

    analyze_error_handling_issues(data)
    analyze_ambiguous_query_handling(data)
    analyze_relevance_helpfulness_discrepancies(data)
    analyze_by_category(data)
    analyze_score_inconsistencies(data)
    analyze_specific_questions(data)


if __name__ == "__main__":
    main()
