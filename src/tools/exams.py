"""
Exam schedule tools for FIB API.
"""

from datetime import datetime
from typing import Literal

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors


@handle_api_errors
def search_exams(
    course_code: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    semester: Literal["1", "2"] | None = None,
    year: int | None = None,
    exam_type: Literal["F", "P"] | None = None,
    study_plan: str | None = None,
) -> str:
    """
    Search FIB exam schedules with various filters.

    Args:
        course_code: Filter by course code (e.g., 'IA', 'AC2')
        start_date: Filter exams starting from this date (YYYY-MM-DD format)
        end_date: Filter exams until this date (YYYY-MM-DD format)
        semester: Filter by semester ('1' or '2')
        year: Filter by academic year (e.g., 2024 for 2024-2025)
        exam_type: Filter by type - 'F' for Final, 'P' for Partial
        study_plan: Filter by study plan (e.g., GRAU, MAI)

    Returns:
        JSON string with matching exams
    """
    client = get_fib_client()
    exams = client.get_exams()

    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None
    semester_int = int(semester) if semester else None

    results = []
    for exam in exams:
        if course_code and exam.assig.upper() != course_code.upper():
            continue
        if start_dt and exam.inici < start_dt:
            continue
        if end_dt and exam.fi > end_dt:
            continue
        if semester_int is not None and exam.quatr != semester_int:
            continue
        if year is not None and exam.curs != year:
            continue
        if exam_type and exam.tipus != exam_type:
            continue
        if study_plan and exam.pla.upper() != study_plan.upper():
            continue

        results.append(
            {
                "course": exam.assig,
                "date": exam.inici.strftime("%Y-%m-%d"),
                "start_time": exam.inici.strftime("%H:%M"),
                "end_time": exam.fi.strftime("%H:%M"),
                "classroom": exam.aules,
                "type": "Final" if exam.is_final else "Partial" if exam.is_partial else exam.tipus,
                "study_plan": exam.pla,
                "academic_year": f"{exam.curs}-{exam.curs + 1}",
                "semester": f"Q{exam.quatr}",
                "comments": exam.comentaris if exam.comentaris else None,
            }
        )

    results.sort(key=lambda x: (x["date"], x["start_time"]))

    summary = f"Found {len(results)} exam(s)"
    if course_code:
        summary += f" for course {course_code}"
    return format_tool_response(results, summary)


@handle_api_errors
def get_upcoming_exams(days_ahead: int = 30, study_plan: str | None = None) -> str:
    """
    Get exams scheduled within the next N days.

    Args:
        days_ahead: Number of days to look ahead (default 30)
        study_plan: Filter by study plan (e.g., GRAU, MAI)

    Returns:
        JSON string with upcoming exams
    """
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    end_dt = datetime(now.year, now.month, now.day)
    end_dt = end_dt.replace(day=min(now.day + days_ahead, 28))

    return search_exams(
        start_date=start_date,
        end_date=end_dt.strftime("%Y-%m-%d"),
        study_plan=study_plan,
    )
