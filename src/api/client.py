"""
FIB API HTTP client with authentication, pagination, and error handling.
"""

import os
from typing import Any, TypeVar

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from src.models import (
    AcademicTerm,
    Classroom,
    Course,
    Exam,
    NewsItem,
    Professor,
    UserClass,
    UserCourse,
    UserNotice,
    UserProfile,
)

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class FIBAPIError(Exception):
    """Base exception for FIB API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FIBAuthenticationError(FIBAPIError):
    """Authentication failed - invalid or missing client_id."""

    pass


class FIBRateLimitError(FIBAPIError):
    """API rate limit exceeded."""

    pass


class FIBNotFoundError(FIBAPIError):
    """Requested resource not found."""

    pass


class FIBOAuthRequiredError(FIBAPIError):
    """OAuth authentication required for this endpoint."""

    pass


class FIBAPIClient:
    """
    HTTP client for the FIB API.

    Handles authentication, pagination, language preferences, and error handling.
    Public endpoints require a client_id header.
    Private endpoints require OAuth bearer token authentication.
    """

    BASE_URL = "https://api.fib.upc.edu/v2"

    def __init__(
        self,
        client_id: str | None = None,
        language: str = "en",
        timeout: int = 30,
    ):
        self.client_id = client_id or os.getenv("FIB_CLIENT_ID")
        if not self.client_id:
            raise FIBAuthenticationError("FIB_CLIENT_ID is required")
        self.language = language
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self._default_headers)
        self._oauth_client = None

    def set_oauth_client(self, oauth_client: Any) -> None:
        """Set the OAuth client for authenticated requests."""
        self._oauth_client = oauth_client

    @property
    def is_authenticated(self) -> bool:
        """Check if OAuth is available and authenticated."""
        return self._oauth_client is not None and self._oauth_client.is_authenticated

    @property
    def _default_headers(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "Accept": "application/json",
            "Accept-Language": self.language,
        }

    def _get_auth_headers(self) -> dict[str, str]:
        """Get headers with OAuth bearer token for authenticated requests."""
        if not self._oauth_client:
            raise FIBOAuthRequiredError("OAuth client not configured")
        if not self._oauth_client.is_authenticated:
            raise FIBOAuthRequiredError("OAuth authentication required")

        token = self._oauth_client.access_token
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Accept-Language": self.language,
        }

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        if response.status_code == 401:
            raise FIBAuthenticationError("Invalid credentials", status_code=401)
        if response.status_code == 404:
            raise FIBNotFoundError("Resource not found", status_code=404)
        if response.status_code == 429:
            raise FIBRateLimitError("Rate limit exceeded", status_code=429)
        if response.status_code >= 400:
            raise FIBAPIError(f"API error: {response.text}", status_code=response.status_code)
        return response.json()

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        response = self._session.get(url, params=params, timeout=self.timeout)
        return self._handle_response(response)

    def _get_authenticated(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated GET request to a private endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_auth_headers()
        response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        return self._handle_response(response)

    def _get_authenticated_list(
        self,
        endpoint: str,
        model_class: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        """Fetch a list from an authenticated endpoint with pagination support."""
        all_results: list[T] = []
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_auth_headers()

        while url:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            data = self._handle_response(response)

            if isinstance(data, list):
                all_results.extend([model_class.model_validate(item) for item in data])
                break

            if "results" in data:
                results = data.get("results", [])
                all_results.extend([model_class.model_validate(item) for item in results])
                url = data.get("next")
            else:
                all_results.append(model_class.model_validate(data))
                break
            params = None

        return all_results

    def _get_paginated(
        self,
        endpoint: str,
        model_class: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        all_results: list[T] = []
        url = f"{self.BASE_URL}/{endpoint}"

        while url:
            response = self._session.get(url, params=params, timeout=self.timeout)
            data = self._handle_response(response)

            if isinstance(data, list):
                all_results.extend([model_class.model_validate(item) for item in data])
                break

            results = data.get("results", [])
            all_results.extend([model_class.model_validate(item) for item in results])

            url = data.get("next")
            params = None

        return all_results

    # Public endpoints

    def get_courses(self) -> list[Course]:
        """Fetch all courses from the assignatures endpoint."""
        return self._get_paginated("assignatures", Course)

    def get_course(self, course_id: str) -> Course:
        """Fetch a specific course by ID."""
        data = self._get(f"assignatures/{course_id}")
        return Course.model_validate(data)

    def get_exams(self) -> list[Exam]:
        """Fetch all exam schedules."""
        return self._get_paginated("examens", Exam)

    def get_professors(self) -> list[Professor]:
        """Fetch all professors."""
        return self._get_paginated("professors", Professor)

    def get_classrooms(self) -> list[Classroom]:
        """Fetch all classrooms."""
        return self._get_paginated("aules", Classroom)

    def get_academic_terms(self) -> list[AcademicTerm]:
        """Fetch all academic terms/semesters."""
        return self._get_paginated("quadrimestres", AcademicTerm)

    def get_news(self) -> list[NewsItem]:
        """Fetch news and announcements."""
        return self._get_paginated("noticies", NewsItem)

    # Private endpoints (require OAuth)

    def get_my_profile(self) -> UserProfile:
        """Fetch the authenticated user's profile."""
        data = self._get_authenticated("jo")
        return UserProfile.model_validate(data)

    def get_my_courses(self) -> list[UserCourse]:
        """Fetch the authenticated user's enrolled courses."""
        return self._get_authenticated_list("jo/assignatures", UserCourse)

    def get_my_classes(self) -> list[UserClass]:
        """Fetch the authenticated user's class schedule."""
        return self._get_authenticated_list("jo/classes", UserClass)

    def get_my_notices(self) -> list[UserNotice]:
        """Fetch the authenticated user's notices/announcements."""
        return self._get_authenticated_list("jo/avisos", UserNotice)


_client_instance: FIBAPIClient | None = None


def get_fib_client() -> FIBAPIClient:
    """Get or create a singleton FIB API client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = FIBAPIClient()
    return _client_instance


def configure_oauth() -> bool:
    """Configure OAuth for the FIB client if credentials are available."""
    from src.auth import get_oauth_client

    client = get_fib_client()
    oauth = get_oauth_client()
    if oauth:
        client.set_oauth_client(oauth)
        return True
    return False
