import secrets
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
import httpx
from jose import JWTError, jwt

from app.core.config import settings


# ---------------------------------------------------------
# Atlassian OAuth endpoints
# ---------------------------------------------------------

ATLASSIAN_AUTH_URL = "https://auth.atlassian.com/authorize"

ATLASSIAN_TOKEN_URL = "https://auth.atlassian.com/oauth/token"

ATLASSIAN_RESOURCES_URL = (
    "https://api.atlassian.com/oauth/token/accessible-resources"
)


# ---------------------------------------------------------
# Jira OAuth scopes
# ---------------------------------------------------------

JIRA_OAUTH_SCOPES = [
    "read:jira-user",
    "read:jira-work",
    "write:jira-work",
    "offline_access",
]

# ---------------------------------------------------------
# OAuth state configuration
# ---------------------------------------------------------

OAUTH_STATE_EXPIRE_MINUTES = 10


# ---------------------------------------------------------
# Build authorization URL
# ---------------------------------------------------------

def build_jira_authorization_url(user_id: int) -> str:
    """
    Build the Atlassian OAuth 2.0 authorization URL.

    The state value is signed and contains the user ID so that
    the OAuth callback can identify which application user
    initiated the connection.
    """

    nonce = secrets.token_urlsafe(32)

    state_payload = {
        "user_id": user_id,
        "nonce": nonce,
    }

    state = jwt.encode(
        state_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    params = {
        "audience": "api.atlassian.com",
        "client_id": settings.JIRA_CLIENT_ID,
        "scope": " ".join(JIRA_OAUTH_SCOPES),
        "redirect_uri": settings.JIRA_REDIRECT_URI,
        "state": state,
        "response_type": "code",
        "prompt": "consent",
    }

    return f"{ATLASSIAN_AUTH_URL}?{urlencode(params)}"


# ---------------------------------------------------------
# Validate OAuth state
# ---------------------------------------------------------

def validate_jira_oauth_state(state: str) -> int:
    """
    Validate the OAuth state and return the application user ID.
    """

    try:
        payload = jwt.decode(
            state,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired OAuth state.") from exc

    user_id = payload.get("user_id")
    nonce = payload.get("nonce")

    if not user_id or not nonce:
        raise ValueError("Invalid OAuth state payload.")

    return int(user_id)


# ---------------------------------------------------------
# Exchange authorization code for tokens
# ---------------------------------------------------------

async def exchange_code_for_token(code: str) -> dict:
    """
    Exchange the authorization code received from Atlassian
    for access and refresh tokens.
    """

    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.JIRA_CLIENT_ID,
        "client_secret": settings.JIRA_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.JIRA_REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            ATLASSIAN_TOKEN_URL,
            json=payload,
            headers=headers,
        )

    if response.is_error:
        raise ValueError(
            f"Atlassian token exchange failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


# ---------------------------------------------------------
# Get accessible Jira resources
# ---------------------------------------------------------

async def get_accessible_resources(access_token: str) -> list[dict]:
    """
    Get Atlassian sites/resources accessible by the OAuth token.
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            ATLASSIAN_RESOURCES_URL,
            headers=headers,
        )

    if response.is_error:
        raise ValueError(
            f"Failed to retrieve Atlassian resources: "
            f"{response.status_code} - {response.text}"
        )

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Unexpected accessible-resources response.")

    return data


# ---------------------------------------------------------
# Find Jira resource
# ---------------------------------------------------------

def find_jira_resource(resources: list[dict]) -> dict:
    for resource in resources:
        scopes = set(resource.get("scopes", []))

        required_scopes = {
            "read:jira-user",
            "read:jira-work",
            "write:jira-work",
        }

        if required_scopes.intersection(scopes):
            return resource

    raise ValueError(
        "No Jira Cloud site with the required Jira scopes was found."
    )


def get_access_token_expiry(token_data: dict) -> datetime | None:
    """
    Calculate the access-token expiration time from Atlassian's
    expires_in value.
    """

    expires_in = token_data.get("expires_in")

    if expires_in is None:
        return None

    try:
        expires_in = int(expires_in)
    except (TypeError, ValueError):
        return None

    return datetime.now(timezone.utc) + timedelta(
        seconds=expires_in
    )


async def refresh_jira_access_token(
    refresh_token: str,
) -> dict:
    """
    Refresh an expired Jira Cloud access token.
    """

    payload = {
        "grant_type": "refresh_token",
        "client_id": settings.JIRA_CLIENT_ID,
        "client_secret": settings.JIRA_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            ATLASSIAN_TOKEN_URL,
            json=payload,
            headers=headers,
        )

    if response.is_error:
        raise ValueError(
            f"Jira access-token refresh failed: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()