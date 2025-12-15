"""
Classroom tools for FIB API.
"""

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors


@handle_api_errors
def list_classrooms(building: str | None = None, prefix: str | None = None) -> str:
    """
    List FIB classrooms with optional filtering.

    Args:
        building: Filter by building letter (e.g., 'A', 'B', 'C', 'D')
        prefix: Filter by room ID prefix (e.g., 'A5' for rooms A5001, A5002, A5E01, etc.)

    Returns:
        JSON string with classroom information
    """
    client = get_fib_client()
    classrooms = client.get_classrooms()

    results = []
    for room in classrooms:
        if room.id == "**":
            continue

        # If prefix is given, filter by prefix (more specific than building)
        if prefix:
            if not room.id.upper().startswith(prefix.upper()):
                continue
        elif building:
            # Only apply building filter if prefix is not given
            if room.building.upper() != building.upper():
                continue

        results.append(
            {
                "id": room.id,
                "building": room.building if room.building else "Other",
            }
        )

    results.sort(key=lambda x: x["id"])

    summary = f"Found {len(results)} classroom(s)"
    if prefix:
        summary += f" with prefix '{prefix}'"
    elif building:
        summary += f" in building {building}"
    return format_tool_response(results, summary)
