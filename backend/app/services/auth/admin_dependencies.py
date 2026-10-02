from fastapi import Depends, HTTPException, status

from app.models.auth_model import User
from app.services.auth.dependencies import get_current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user