from sqlalchemy.orm import Session

from app.models.auth_model import User, UserApplicationAccess

from app.services.access.application_access_constants import (
    ALLOWED_APPLICATIONS,
)


def get_all_users(
    db: Session,
):
    users = (
        db.query(User)
        .order_by(User.id.asc())
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.name if user.role else None,
        }
        for user in users
    ]


def get_user_application_access(
    db: Session,
    user_id: int,
):
    rows = (
        db.query(UserApplicationAccess)
        .filter(
            UserApplicationAccess.user_id == user_id
        )
        .all()
    )

    access_map = {
        row.application: row.enabled
        for row in rows
    }

    return [
        {
            "application": application,
            "enabled": access_map.get(application, False),
        }
        for application in sorted(ALLOWED_APPLICATIONS)
    ]


def update_user_application_access(
    db: Session,
    user_id: int,
    application: str,
    enabled: bool,
):
    if application not in ALLOWED_APPLICATIONS:
        raise ValueError(
            f"Invalid application: {application}"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise ValueError("User not found.")

    access = (
        db.query(UserApplicationAccess)
        .filter(
            UserApplicationAccess.user_id == user_id,
            UserApplicationAccess.application == application,
        )
        .first()
    )

    if access is None:

        access = UserApplicationAccess(
            user_id=user_id,
            application=application,
            enabled=enabled,
        )

        db.add(access)

    else:

        access.enabled = enabled

    db.commit()
    db.refresh(access)

    return access



def get_user_details(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    applications = get_user_application_access(
        db=db,
        user_id=user_id,
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.name if user.role else None,
        "applications": applications,
    }