"""
Base tool utilities and error handling for FIB API tools.
"""

import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from src.api import FIBAPIError, FIBAuthenticationError, FIBNotFoundError, FIBRateLimitError


def format_tool_response(data: Any, summary: str | None = None) -> str:
    """Format tool response for LLM consumption."""
    if isinstance(data, list):
        if len(data) == 0:
            return "No results found."
        result = {"count": len(data), "results": data}
        if summary:
            result["summary"] = summary
        return json.dumps(result, default=str, ensure_ascii=False, indent=2)
    return json.dumps(data, default=str, ensure_ascii=False, indent=2)


def handle_api_errors(func: Callable) -> Callable:
    """Decorator to handle FIB API errors and return user-friendly messages."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FIBAuthenticationError:
            return json.dumps(
                {
                    "error": "Authentication failed",
                    "message": "The FIB API credentials are invalid or missing. Please check your configuration.",
                }
            )
        except FIBNotFoundError:
            return json.dumps(
                {
                    "error": "Not found",
                    "message": "The requested resource was not found in the FIB system.",
                }
            )
        except FIBRateLimitError:
            return json.dumps(
                {
                    "error": "Rate limit exceeded",
                    "message": "Too many requests to the FIB API. Please wait a moment and try again.",
                }
            )
        except FIBAPIError as e:
            return json.dumps(
                {
                    "error": "API error",
                    "message": f"An error occurred while accessing the FIB API: {e.message}",
                }
            )
        except Exception as e:
            return json.dumps(
                {
                    "error": "Unexpected error",
                    "message": f"An unexpected error occurred: {str(e)}",
                }
            )

    return wrapper


def normalize_string(s: str) -> str:
    """Normalize a string for case-insensitive comparison."""
    return s.lower().strip()


def matches_query(text: str, query: str) -> bool:
    """Check if text contains the query (case-insensitive)."""
    return normalize_string(query) in normalize_string(text)
