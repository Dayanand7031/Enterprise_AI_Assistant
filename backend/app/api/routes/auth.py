from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.role_permission_model import RolePermission,Role,Permission
from app.db.database import get_db
from app.models.auth_model import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
)
from app.services.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    return register_user(
        db=db,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    return login_user(
        db=db,
        login_data=login_data,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return refresh_access_token(
        db=db,
        refresh_token=token_data.refresh_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user