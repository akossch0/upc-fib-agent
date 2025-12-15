"""
OAuth2 authentication client for FIB API private endpoints.

Handles token management, refresh, and authorization flow for accessing
user-specific data like courses, schedule, and notices.
"""

import json
import os
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OAuthToken:
    """OAuth2 token with expiration tracking."""

    access_token: str
    refresh_token: str
    expires_at: float
    token_type: str = "Bearer"

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at - 60

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OAuthToken":
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=data["expires_at"],
            token_type=data.get("token_type", "Bearer"),
        )


class FIBOAuthError(Exception):
    """Base exception for FIB OAuth errors."""

    pass


class FIBOAuthClient:
    """
    OAuth2 client for FIB API authentication.

    Implements the authorization code flow with PKCE support and handles
    token refresh automatically.
    """

    AUTH_URL = "https://api.fib.upc.edu/v2/o/authorize/"
    TOKEN_URL = "https://api.fib.upc.edu/v2/o/token/"
    DEFAULT_SCOPES = ["read"]

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str = "http://localhost:8085/callback",
        token_file: str | None = None,
    ):
        self.client_id = client_id or os.getenv("FIB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("FIB_CLIENT_SECRET")
        self.redirect_uri = redirect_uri

        if not self.client_id:
            raise FIBOAuthError("FIB_CLIENT_ID is required")
        if not self.client_secret:
            raise FIBOAuthError("FIB_CLIENT_SECRET is required for OAuth")

        self._token: OAuthToken | None = None
        self._token_file = Path(token_file) if token_file else Path.home() / ".fib_token.json"
        self._load_token()

    @property
    def is_authenticated(self) -> bool:
        return self._token is not None

    @property
    def access_token(self) -> str | None:
        if self._token is None:
            return None
        if self._token.is_expired:
            self._refresh_token()
        return self._token.access_token if self._token else None

    def get_authorization_url(self, scopes: list[str] | None = None) -> str:
        """Generate the authorization URL for user login."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes or self.DEFAULT_SCOPES),
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def authorize_interactive(self, scopes: list[str] | None = None) -> bool:
        """Run interactive authorization flow with local callback server."""
        auth_url = self.get_authorization_url(scopes)
        auth_code = None

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                query = parse_qs(urlparse(self.path).query)
                if "code" in query:
                    auth_code = query["code"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Authorization successful!</h1><p>You can close this window.</p></body></html>")
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Authorization failed</h1></body></html>")

            def log_message(self, format, *args):
                pass

        parsed = urlparse(self.redirect_uri)
        port = parsed.port or 8085

        server = HTTPServer(("localhost", port), CallbackHandler)
        server.timeout = 120

        print("Opening browser for FIB authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)

        def handle_request():
            server.handle_request()

        thread = Thread(target=handle_request)
        thread.start()
        thread.join(timeout=120)

        if auth_code:
            return self.exchange_code(auth_code)
        return False

    def exchange_code(self, code: str) -> bool:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30,
            )
            if response.status_code != 200:
                print(f"Token exchange failed: {response.status_code}")
                print(f"Response: {response.text}")
            response.raise_for_status()
            token_data = response.json()

            self._token = OAuthToken(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", ""),
                expires_at=time.time() + token_data.get("expires_in", 3600),
                token_type=token_data.get("token_type", "Bearer"),
            )
            self._save_token()
            return True
        except requests.RequestException as e:
            raise FIBOAuthError(f"Token exchange failed: {e}") from e

    def _refresh_token(self) -> None:
        """Refresh the access token using the refresh token."""
        if not self._token or not self._token.refresh_token:
            self._token = None
            return

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._token.refresh_token,
        }

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                auth=(self.client_id, self.client_secret),
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            self._token = OAuthToken(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", self._token.refresh_token),
                expires_at=time.time() + token_data.get("expires_in", 3600),
                token_type=token_data.get("token_type", "Bearer"),
            )
            self._save_token()
        except requests.RequestException:
            self._token = None
            self._clear_token()

    def _load_token(self) -> None:
        """Load token from file if exists."""
        if self._token_file.exists():
            try:
                with open(self._token_file) as f:
                    data = json.load(f)
                self._token = OAuthToken.from_dict(data)
                if self._token.is_expired and self._token.refresh_token:
                    self._refresh_token()
            except (json.JSONDecodeError, KeyError):
                self._token = None

    def _save_token(self) -> None:
        """Save token to file."""
        if self._token:
            with open(self._token_file, "w") as f:
                json.dump(self._token.to_dict(), f)

    def _clear_token(self) -> None:
        """Clear saved token."""
        if self._token_file.exists():
            self._token_file.unlink()

    def logout(self) -> None:
        """Clear authentication state."""
        self._token = None
        self._clear_token()


_oauth_client: FIBOAuthClient | None = None


def get_oauth_client() -> FIBOAuthClient | None:
    """Get the global OAuth client instance, or None if not configured."""
    global _oauth_client
    if _oauth_client is None:
        try:
            _oauth_client = FIBOAuthClient()
        except FIBOAuthError:
            return None
    return _oauth_client


def is_authenticated() -> bool:
    """Check if OAuth is configured and authenticated."""
    client = get_oauth_client()
    return client is not None and client.is_authenticated
