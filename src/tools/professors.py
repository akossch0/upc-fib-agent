"""
Professor/faculty directory tools for FIB API.
"""

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors, matches_query


@handle_api_errors
def search_professors(
    name: str | None = None,
    course_code: str | None = None,
    department: str | None = None,
) -> str:
    """
    Search the FIB faculty directory.

    Args:
        name: Search by professor name (first or last name)
        course_code: Find professors teaching a specific course
        department: Filter by department code (e.g., 'AC', 'CS', 'ESSI')

    Returns:
        JSON string with matching professors
    """
    client = get_fib_client()
    professors = client.get_professors()

    results = []
    for prof in professors:
        if name and not (matches_query(prof.nom, name) or matches_query(prof.cognoms, name)):
            continue
        if course_code:
            course_upper = course_code.upper()
            if not any(course_upper in c.upper() for c in prof.assignatures):
                continue
        if department and prof.departament.upper() != department.upper():
            continue

        results.append(
            {
                "name": prof.full_name,
                "email": prof.email,
                "department": prof.departament,
                "courses": prof.assignatures,
                "specializations": prof.especialitats if prof.especialitats else None,
                "research_profile": prof.futur_url if prof.futur_url else None,
                "teaching_profile": prof.apren_url if prof.apren_url else None,
            }
        )

    summary = f"Found {len(results)} professor(s)"
    if name:
        summary += f" matching '{name}'"
    if course_code:
        summary += f" teaching {course_code}"
    return format_tool_response(results, summary)


@handle_api_errors
def get_course_professors(course_code: str) -> str:
    """
    Get all professors teaching a specific course.

    Args:
        course_code: The course code (e.g., 'IA', 'AC2')

    Returns:
        JSON string with professors teaching this course
    """
    return search_professors(course_code=course_code)
