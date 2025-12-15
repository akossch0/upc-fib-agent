"""
News and announcements tools for FIB API.
"""

from datetime import datetime

from src.api import get_fib_client
from src.tools.base import format_tool_response, handle_api_errors


@handle_api_errors
def get_fib_news(limit: int = 5, since_date: str | None = None) -> str:
    """
    Get FIB news and announcements.

    Args:
        limit: Maximum number of news items to return (default 5)
        since_date: Only return news published after this date (YYYY-MM-DD format)

    Returns:
        JSON string with news items
    """
    client = get_fib_client()
    news_items = client.get_news()

    since_dt = datetime.fromisoformat(since_date) if since_date else None

    results = []
    for item in news_items:
        if since_dt and item.data_publicacio < since_dt:
            continue

        results.append(
            {
                "title": item.titol,
                "date": item.data_publicacio.strftime("%Y-%m-%d"),
                "summary": item.plain_description[:300] + "..." if len(item.plain_description) > 300 else item.plain_description,
                "link": item.link,
            }
        )

    results.sort(key=lambda x: x["date"], reverse=True)
    results = results[:limit]

    return format_tool_response(results, f"Latest {len(results)} news item(s) from FIB")
