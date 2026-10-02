from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_model import User

from app.schemas.admin import (
    UpdateApplicationAccessRequest,
    UserAccessResponse,
    AdminUserResponse,
    AdminUserDetailResponse,

)

from app.services.auth.admin_dependencies import (
    require_admin,
)

from app.services.access.admin_access_service import (
    get_user_application_access,
    update_user_application_access,
    get_all_users,
    get_user_details,
)


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return get_all_users(db=db)


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse,
)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    user = get_user_details(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return user



@router.get(
    "/users/{user_id}/access",
    response_model=UserAccessResponse,
)
def get_user_access(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    applications = get_user_application_access(
        db=db,
        user_id=user_id,
    )

    return {
        "user_id": user_id,
        "applications": applications,
    }


@router.put(
    "/users/{user_id}/access",
)
def update_user_access(
    user_id: int,
    request: UpdateApplicationAccessRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):

    try:

        access = update_user_application_access(
            db=db,
            user_id=user_id,
            application=request.application,
            enabled=request.enabled,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "message": "Application access updated successfully.",
        "user_id": user_id,
        "application": access.application,
        "enabled": access.enabled,
    }
