from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_model import RefreshToken,User
from app.services.auth.security import hash_refresh_token


def store_refresh_token(
    db: Session,
    user_id: int,
    refresh_token: str,
) -> RefreshToken:

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    token_record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at,
        revoked=False,
    )

    db.add(token_record)
    db.commit()
    db.refresh(token_record)

    return token_record


def get_refresh_token(
    db: Session,
    refresh_token: str,
) -> RefreshToken | None:

    token_hash = hash_refresh_token(
        refresh_token
    )

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash
        )
        .first()
    )


def validate_refresh_token(
    db: Session,
    refresh_token: str,
) -> RefreshToken | None:

    token_record = get_refresh_token(
        db=db,
        refresh_token=refresh_token,
    )

    if token_record is None:
        return None

    if token_record.revoked:
        return None

    now = datetime.now(timezone.utc)

    expires_at = token_record.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= now:
        return None

    return token_record


def revoke_refresh_token(
    db: Session,
    token_record: RefreshToken,
) -> None:

    token_record.revoked = True
    token_record.revoked_at = datetime.now(timezone.utc)

    db.commit()