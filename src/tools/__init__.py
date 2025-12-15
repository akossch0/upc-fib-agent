from src.tools.academic import get_academic_terms, get_current_term
from src.tools.base import format_tool_response, handle_api_errors
from src.tools.classrooms import list_classrooms
from src.tools.courses import get_course_details, search_courses
from src.tools.exams import get_upcoming_exams, search_exams
from src.tools.news import get_fib_news
from src.tools.private import get_my_courses, get_my_notices, get_my_profile, get_my_schedule
from src.tools.professors import get_course_professors, search_professors

__all__ = [
    "format_tool_response",
    "handle_api_errors",
    "search_courses",
    "get_course_details",
    "search_exams",
    "get_upcoming_exams",
    "search_professors",
    "get_course_professors",
    "get_academic_terms",
    "get_current_term",
    "get_fib_news",
    "list_classrooms",
    "get_my_profile",
    "get_my_courses",
    "get_my_schedule",
    "get_my_notices",
]


ALL_FIB_TOOLS = [
    search_courses,
    get_course_details,
    search_exams,
    get_upcoming_exams,
    search_professors,
    get_course_professors,
    get_academic_terms,
    get_current_term,
    get_fib_news,
    list_classrooms,
]


PRIVATE_FIB_TOOLS = [
    get_my_profile,
    get_my_courses,
    get_my_schedule,
    get_my_notices,
]
