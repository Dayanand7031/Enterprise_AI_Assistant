from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_model import User

from app.services.auth.dependencies import get_current_user
from app.services.rbac.permission_service import has_permission


def require_permission(permission_name: str):

    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

        allowed = has_permission(
            db=db,
            user=current_user,
            permission_name=permission_name,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permission required: "
                    f"{permission_name}"
                ),
            )

        return current_user

    return permission_dependency