"""
Course/assignatures tools for FIB API.
"""

from typing import Literal

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors, matches_query


@handle_api_errors
def search_courses(
    query: str | None = None,
    semester: Literal["Q1", "Q2"] | None = None,
    study_plan: str | None = None,
    course_type: Literal["OBL", "OPT", "PE"] | None = None,
    credits_min: float | None = None,
    credits_max: float | None = None,
    active_only: bool = True,
) -> str:
    """
    Search the FIB course catalog with various filters.

    Args:
        query: Search term to match against course code or name
        semester: Filter by semester (Q1 or Q2)
        study_plan: Filter by study plan code (e.g., GRAU, MAI, MIRI)
        course_type: Filter by course type (OBL=obligatory, OPT=optional/elective, PE=project)
        credits_min: Minimum ECTS credits
        credits_max: Maximum ECTS credits
        active_only: Only return active courses (default True)

    Returns:
        JSON string with matching courses
    """
    client = get_fib_client()
    courses = client.get_courses()

    results = []
    for course in courses:
        if active_only and not course.is_active:
            continue
        if query and not (matches_query(course.id, query) or matches_query(course.nom, query)):
            continue
        if semester and semester not in course.quadrimestres:
            continue
        if study_plan and study_plan.upper() not in [p.upper() for p in course.plans]:
            continue

        # Filter by course type (optionally combined with study_plan)
        if course_type:
            type_match = False
            for req in course.obligatorietats:
                if req.codi_oblig.upper() == course_type.upper():
                    # If study_plan is also specified, must match both
                    if study_plan is None or req.pla.upper() == study_plan.upper():
                        type_match = True
                        break
            if not type_match:
                continue

        if credits_min is not None and course.credits < credits_min:
            continue
        if credits_max is not None and course.credits > credits_max:
            continue
        results.append(
            {
                "id": course.id,
                "name": course.nom,
                "credits": course.credits,
                "semester": course.semestre,
                "semesters_offered": course.quadrimestres,
                "study_plans": course.plans,
                "syllabus_url": course.guia_docent_url_publica,
            }
        )

    summary = f"Found {len(results)} course(s)"
    if query:
        summary += f" matching '{query}'"
    if course_type:
        summary += f" of type {course_type}"
    return format_tool_response(results, summary)


@handle_api_errors
def get_course_details(course_code: str) -> str:
    """
    Get detailed information about a specific course.

    Args:
        course_code: The course code/ID (e.g., 'IA', 'AC2', 'CPP-MAI')

    Returns:
        JSON string with full course details
    """
    client = get_fib_client()
    course = client.get_course(course_code.upper())

    result = {
        "id": course.id,
        "name": course.nom,
        "credits": course.credits,
        "semester": course.semestre,
        "semesters_offered": course.quadrimestres,
        "study_plans": course.plans,
        "upc_code": course.codi_upc,
        "active": course.is_active,
        "languages": course.lang,
        "syllabus_url": course.guia_docent_url_publica,
        "requirements": [
            {
                "type": req.codi_oblig,
                "plan": req.pla,
                "specialization": req.nom_especialitat or None,
            }
            for req in course.obligatorietats
        ],
    }
    return format_tool_response(result)
