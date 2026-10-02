from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.Jira_connection_model import JiraConnection
from app.services.jira_integrations.jira_cloud.jira_auth import (
    get_access_token_expiry,
    refresh_jira_access_token,
)


TOKEN_EXPIRY_BUFFER_SECONDS = 60


def get_jira_connection(
    db: Session,
    user_id: int,
) -> JiraConnection | None:

    return (
        db.query(JiraConnection)
        .filter(
            JiraConnection.user_id == user_id
        )
        .first()
    )


def is_access_token_valid(
    connection: JiraConnection,
) -> bool:

    if not connection.access_token:
        return False

    if connection.access_token_expires_at is None:
        return False

    expires_at = connection.access_token_expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    buffer_time = timedelta(
        seconds=TOKEN_EXPIRY_BUFFER_SECONDS
    )

    return datetime.now(timezone.utc) + buffer_time < expires_at





async def get_valid_jira_access_token(
    db: Session,
    user_id: int,
) -> str:

    connection = get_jira_connection(
        db=db,
        user_id=user_id,
    )

    if connection is None:
        raise ValueError(
            "Jira Cloud is not connected for this user."
        )

    # -------------------------------------------------
    # Existing access token is still valid
    # -------------------------------------------------

    if is_access_token_valid(connection):

        return connection.access_token

    # -------------------------------------------------
    # Access token expired
    # -------------------------------------------------

    if not connection.refresh_token:

        raise ValueError(
            "Jira access token expired and no refresh token "
            "is available."
        )

    token_data = await refresh_jira_access_token(
        connection.refresh_token
    )

    new_access_token = token_data.get(
        "access_token"
    )

    if not new_access_token:
        raise ValueError(
            "Atlassian did not return a new access token."
        )

    new_refresh_token = token_data.get(
        "refresh_token"
    )

    # -------------------------------------------------
    # Update connection
    # -------------------------------------------------

    connection.access_token = new_access_token

    if new_refresh_token:
        connection.refresh_token = new_refresh_token

    connection.access_token_expires_at = (
        get_access_token_expiry(token_data)
    )

    db.commit()
    db.refresh(connection)

    return connection.access_token







async def refresh_jira_access_token_for_user(
    db: Session,
    user_id: int,
) -> dict:

    connection = get_jira_connection(
        db=db,
        user_id=user_id,
    )

    if connection is None:
        raise ValueError(
            "Jira Cloud is not connected for this user."
        )

    if not connection.refresh_token:
        raise ValueError(
            "No Jira refresh token is available."
        )

    # Ask Atlassian for a new token pair
    token_data = await refresh_jira_access_token(
        connection.refresh_token
    )

    new_access_token = token_data.get("access_token")

    if not new_access_token:
        raise ValueError(
            "Atlassian did not return a new access token."
        )

    new_refresh_token = token_data.get("refresh_token")

    # Save new access token
    connection.access_token = new_access_token

    # Atlassian may rotate the refresh token
    if new_refresh_token:
        connection.refresh_token = new_refresh_token

    # Save new expiry
    connection.access_token_expires_at = (
        get_access_token_expiry(token_data)
    )

    db.commit()
    db.refresh(connection)

    return {
        "message": "Jira access token refreshed successfully.",
        "expires_at": connection.access_token_expires_at,
        "new_refresh_token_received": bool(new_refresh_token),
    }