"""
Private/authenticated tools for FIB API.

These tools access user-specific data and require OAuth authentication.
"""

from typing import Literal

from src.api import FIBOAuthRequiredError, get_fib_client
from src.tools.base import format_tool_response, handle_api_errors, matches_query


def _check_auth() -> str | None:
    """Check if OAuth is configured and authenticated. Returns error message if not."""
    client = get_fib_client()
    if not client.is_authenticated:
        return "Authentication required. You need to log in with your FIB account to access personal data like your courses, schedule, and notices."
    return None


@handle_api_errors
def get_my_profile() -> str:
    """
    Get the authenticated user's profile information.

    Returns:
        JSON string with user profile including name, email, student ID, and program
    """
    auth_error = _check_auth()
    if auth_error:
        return format_tool_response({"error": "Authentication required", "message": auth_error})

    client = get_fib_client()
    try:
        profile = client.get_my_profile()
        result = {
            "username": profile.username,
            "full_name": profile.full_name,
            "email": profile.email,
            "type": profile.tipus,
            "study_plans": profile.plans_estudi,
            "is_student": profile.is_student,
            "is_professor": profile.is_professor,
        }
        return format_tool_response(result)
    except FIBOAuthRequiredError:
        return format_tool_response(
            {
                "error": "Authentication required",
                "message": "Please log in with your FIB account to access your profile.",
            }
        )


@handle_api_errors
def get_my_courses(
    semester: Literal["Q1", "Q2"] | None = None,
    passed_only: bool = False,
    with_grades: bool = False,
) -> str:
    """
    Get the authenticated user's enrolled courses.

    Args:
        semester: Filter by semester (Q1 or Q2)
        passed_only: Only show courses the user has passed
        with_grades: Include grade information in results

    Returns:
        JSON string with enrolled courses and optional grade information
    """
    auth_error = _check_auth()
    if auth_error:
        return format_tool_response({"error": "Authentication required", "message": auth_error})

    client = get_fib_client()
    try:
        courses = client.get_my_courses()

        results = []
        total_credits = 0.0

        for course in courses:
            if semester and course.quadrimestre.upper() != semester.upper():
                continue
            if passed_only and not course.is_passed:
                continue

            course_data = {
                "id": course.id,
                "name": course.nom,
                "credits": course.credits,
                "semester": course.quadrimestre,
                "group": course.grup,
            }

            if with_grades:
                course_data["grade"] = course.nota
                course_data["qualification"] = course.qualificacio
                course_data["passed"] = course.is_passed

            results.append(course_data)
            total_credits += course.credits

        summary = f"Found {len(results)} enrolled course(s), {total_credits} total credits"
        if semester:
            summary += f" in {semester}"
        return format_tool_response(results, summary)
    except FIBOAuthRequiredError:
        return format_tool_response(
            {
                "error": "Authentication required",
                "message": "Please log in with your FIB account to access your courses.",
            }
        )


@handle_api_errors
def get_my_schedule(
    day: Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] | None = None,
    course_code: str | None = None,
) -> str:
    """
    Get the authenticated user's class schedule.

    Args:
        day: Filter by day of week
        course_code: Filter by specific course code

    Returns:
        JSON string with class schedule including times, locations, and class types
    """
    auth_error = _check_auth()
    if auth_error:
        return format_tool_response({"error": "Authentication required", "message": auth_error})

    client = get_fib_client()
    try:
        classes = client.get_my_classes()

        day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }

        results = []
        for cls in classes:
            if day and cls.dia_setmana != day_map.get(day, 0):
                continue
            if course_code and not matches_query(cls.codi_assig, course_code):
                continue

            results.append(
                {
                    "course": cls.codi_assig,
                    "course_name": cls.nom_assig,
                    "day": cls.day_name,
                    "start_time": cls.inici,
                    "end_time": cls.fi,
                    "type": cls.class_type_name,
                    "classroom": cls.aules,
                    "group": cls.grup,
                }
            )

        results.sort(key=lambda x: (day_map.get(x["day"], 0), x["start_time"]))

        summary = f"Found {len(results)} class(es)"
        if day:
            summary += f" on {day}"
        if course_code:
            summary += f" for {course_code}"
        return format_tool_response(results, summary)
    except FIBOAuthRequiredError:
        return format_tool_response(
            {
                "error": "Authentication required",
                "message": "Please log in with your FIB account to access your schedule.",
            }
        )


@handle_api_errors
def get_my_notices(
    course_code: str | None = None,
    limit: int = 10,
) -> str:
    """
    Get the authenticated user's course notices and announcements.

    Args:
        course_code: Filter notices by course code
        limit: Maximum number of notices to return

    Returns:
        JSON string with notices including title, course, content, and date
    """
    auth_error = _check_auth()
    if auth_error:
        return format_tool_response({"error": "Authentication required", "message": auth_error})

    client = get_fib_client()
    try:
        notices = client.get_my_notices()

        results = []
        for notice in notices:
            if course_code and not matches_query(notice.codi_assig, course_code):
                continue

            results.append(
                {
                    "id": notice.id,
                    "title": notice.titol,
                    "course": notice.codi_assig,
                    "content": notice.plain_text[:500] + "..." if len(notice.plain_text) > 500 else notice.plain_text,
                    "date": notice.data_insercio.isoformat(),
                    "has_attachments": len(notice.adjunts) > 0,
                }
            )

            if len(results) >= limit:
                break

        results.sort(key=lambda x: x["date"], reverse=True)

        summary = f"Found {len(results)} notice(s)"
        if course_code:
            summary += f" for {course_code}"
        return format_tool_response(results, summary)
    except FIBOAuthRequiredError:
        return format_tool_response(
            {
                "error": "Authentication required",
                "message": "Please log in with your FIB account to access your notices.",
            }
        )
