"""
Academic terms and general academic information tools for FIB API.
"""

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors


@handle_api_errors
def get_academic_terms(current_only: bool = False, year: int | None = None) -> str:
    """
    Get academic terms/semesters information.

    Args:
        current_only: Only return the current active term
        year: Filter by academic year (e.g., 2024)

    Returns:
        JSON string with academic term information
    """
    client = get_fib_client()
    terms = client.get_academic_terms()

    results = []
    for term in terms:
        if current_only and not term.is_current:
            continue
        if year is not None and term.year != year:
            continue

        results.append(
            {
                "id": term.id,
                "year": term.year,
                "semester": f"Q{term.semester}",
                "is_current": term.is_current,
                "has_current_schedules": term.actual_horaris == "S",
            }
        )

    results.sort(key=lambda x: x["id"], reverse=True)

    if current_only and results:
        return format_tool_response(results[0])
    return format_tool_response(results, f"Found {len(results)} academic term(s)")


@handle_api_errors
def get_current_term() -> str:
    """
    Get the current academic term/semester.

    Returns:
        JSON string with current term information
    """
    return get_academic_terms(current_only=True)
