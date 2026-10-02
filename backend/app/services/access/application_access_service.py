from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.auth_model import UserApplicationAccess


def has_application_access(
    db: Session,
    user_id: int,
    application: str,
) -> bool:

    rows = (
        db.query(UserApplicationAccess)
        .filter(
            UserApplicationAccess.user_id == user_id,
        )
        .all()

    )

    print("========== APPLICATION ACCESS DEBUG ==========")
    print("user_id:", user_id)
    print("requested application:", repr(application))


    for row in rows:
        print(
            "DB ROW:",
            "id=", row.id,
            "user_id=", row.user_id,
            "application=", repr(row.application),
            "enabled=", repr(row.enabled),
        )

    access = (
        db.query(UserApplicationAccess)
        .filter(
            UserApplicationAccess.user_id == user_id,
            UserApplicationAccess.application == application,
            UserApplicationAccess.enabled.is_(True),
        )
        .first()
    )

    print("MATCHING ROW:", access)
    print("==============================================")

    return access is not None


def require_application_access(
    db: Session,
    user_id: int,
    application: str,
) -> None:
    has_access = has_application_access(
        db=db,
        user_id=user_id,
        application=application,
    )

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied for application: {application}",
        )
    