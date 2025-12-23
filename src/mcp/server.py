"""
MCP server exposing FIB API tools.

This module creates an MCP server that exposes all FIB API tools
for use by MCP-compatible clients and agents.
"""

from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp.server import Server
from src.tools import (
    get_academic_terms,
    get_course_details,
    get_current_term,
    get_fib_news,
    get_my_courses,
    get_my_notices,
    get_my_profile,
    get_my_schedule,
    get_upcoming_exams,
    list_classrooms,
    search_courses,
    search_exams,
    search_professors,
)

server = Server("fib-api")


TOOL_DEFINITIONS = [
    Tool(
        name="search_courses",
        description="Search the FIB course catalog. Find courses by name, code, semester, study plan, or credits.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term to match against course code or name",
                },
                "semester": {
                    "type": "string",
                    "enum": ["Q1", "Q2"],
                    "description": "Filter by semester (Q1 or Q2)",
                },
                "study_plan": {
                    "type": "string",
                    "description": "Filter by study plan code (e.g., GRAU, MAI, MIRI)",
                },
                "credits_min": {
                    "type": "number",
                    "description": "Minimum ECTS credits",
                },
                "credits_max": {
                    "type": "number",
                    "description": "Maximum ECTS credits",
                },
                "active_only": {
                    "type": "boolean",
                    "description": "Only return active courses (default true)",
                    "default": True,
                },
            },
        },
    ),
    Tool(
        name="get_course_details",
        description="Get detailed information about a specific FIB course including syllabus, requirements, and languages.",
        inputSchema={
            "type": "object",
            "properties": {
                "course_code": {
                    "type": "string",
                    "description": "The course code/ID (e.g., 'IA', 'AC2', 'CPP-MAI')",
                },
            },
            "required": ["course_code"],
        },
    ),
    Tool(
        name="search_exams",
        description="Search FIB exam schedules. Find exams by course, date range, semester, year, or type.",
        inputSchema={
            "type": "object",
            "properties": {
                "course_code": {
                    "type": "string",
                    "description": "Filter by course code (e.g., 'IA', 'AC2')",
                },
                "start_date": {
                    "type": "string",
                    "description": "Filter exams starting from this date (YYYY-MM-DD format)",
                },
                "end_date": {
                    "type": "string",
                    "description": "Filter exams until this date (YYYY-MM-DD format)",
                },
                "semester": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "Filter by semester (1 or 2)",
                },
                "year": {
                    "type": "integer",
                    "description": "Filter by academic year (e.g., 2024 for 2024-2025)",
                },
                "exam_type": {
                    "type": "string",
                    "enum": ["F", "P"],
                    "description": "Filter by type - 'F' for Final, 'P' for Partial",
                },
                "study_plan": {
                    "type": "string",
                    "description": "Filter by study plan (e.g., GRAU, MAI)",
                },
            },
        },
    ),
    Tool(
        name="get_upcoming_exams",
        description="Get exams scheduled within the next N days.",
        inputSchema={
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "Number of days to look ahead (default 30)",
                    "default": 30,
                },
                "study_plan": {
                    "type": "string",
                    "description": "Filter by study plan (e.g., GRAU, MAI)",
                },
            },
        },
    ),
    Tool(
        name="search_professors",
        description="Search the FIB faculty directory. Find professors by name, course, or department.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Search by professor name (first or last name)",
                },
                "course_code": {
                    "type": "string",
                    "description": "Find professors teaching a specific course",
                },
                "department": {
                    "type": "string",
                    "description": "Filter by department code (e.g., 'AC', 'CS', 'ESSI')",
                },
            },
        },
    ),
    Tool(
        name="get_academic_terms",
        description="Get academic terms/semesters information from FIB.",
        inputSchema={
            "type": "object",
            "properties": {
                "current_only": {
                    "type": "boolean",
                    "description": "Only return the current active term",
                    "default": False,
                },
                "year": {
                    "type": "integer",
                    "description": "Filter by academic year (e.g., 2024)",
                },
            },
        },
    ),
    Tool(
        name="get_current_term",
        description="Get the current academic term/semester at FIB.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_fib_news",
        description="Get FIB news and announcements.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of news items to return (default 5)",
                    "default": 5,
                },
                "since_date": {
                    "type": "string",
                    "description": "Only return news published after this date (YYYY-MM-DD format)",
                },
            },
        },
    ),
    Tool(
        name="list_classrooms",
        description="List FIB classrooms, optionally filtered by building.",
        inputSchema={
            "type": "object",
            "properties": {
                "building": {
                    "type": "string",
                    "description": "Filter by building letter (e.g., 'A', 'B', 'C', 'D')",
                },
            },
        },
    ),
    Tool(
        name="get_my_profile",
        description="Get the authenticated user's profile information (name, email, student ID, etc). Requires OAuth.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_my_courses",
        description="Get the authenticated user's enrolled courses. Requires OAuth.",
        inputSchema={
            "type": "object",
            "properties": {
                "semester": {
                    "type": "string",
                    "enum": ["Q1", "Q2"],
                    "description": "Filter by semester (Q1 or Q2)",
                },
                "passed_only": {
                    "type": "boolean",
                    "description": "Only show courses the user has passed",
                    "default": False,
                },
                "with_grades": {
                    "type": "boolean",
                    "description": "Include grade information in results",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="get_my_schedule",
        description="Get the authenticated user's class schedule. Requires OAuth.",
        inputSchema={
            "type": "object",
            "properties": {
                "day": {
                    "type": "string",
                    "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "description": "Filter by day of week",
                },
                "course_code": {
                    "type": "string",
                    "description": "Filter by specific course code",
                },
            },
        },
    ),
    Tool(
        name="get_my_notices",
        description="Get the authenticated user's course notices and announcements. Requires OAuth.",
        inputSchema={
            "type": "object",
            "properties": {
                "course_code": {
                    "type": "string",
                    "description": "Filter notices by course code",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of notices to return (default 10)",
                    "default": 10,
                },
            },
        },
    ),
]


TOOL_HANDLERS = {
    "search_courses": search_courses,
    "get_course_details": get_course_details,
    "search_exams": search_exams,
    "get_upcoming_exams": get_upcoming_exams,
    "search_professors": search_professors,
    "get_academic_terms": get_academic_terms,
    "get_current_term": get_current_term,
    "get_fib_news": get_fib_news,
    "list_classrooms": list_classrooms,
    "get_my_profile": get_my_profile,
    "get_my_courses": get_my_courses,
    "get_my_schedule": get_my_schedule,
    "get_my_notices": get_my_notices,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available FIB API tools."""
    return TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a FIB API tool."""
    if name not in TOOL_HANDLERS:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    handler = TOOL_HANDLERS[name]
    result = handler(**arguments)
    return [TextContent(type="text", text=result)]


async def run_server():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
