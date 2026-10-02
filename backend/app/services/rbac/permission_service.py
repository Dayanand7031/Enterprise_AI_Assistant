from sqlalchemy.orm import Session

from app.models.auth_model import User


def has_permission(
    db: Session,
    user: User,
    permission_name: str,
) -> bool:

    if user.role is None:
        return False

    for role_permission in user.role.role_permissions:

        if role_permission.permission.name == permission_name:
            return True

    return False