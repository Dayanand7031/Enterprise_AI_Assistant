from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.auth_model import User
from app.schemas.auth import RegisterRequest
from app.services.auth.security import hash_password

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
)
from app.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
)
from app.services.auth.security import (
    hash_password,
    verify_password,
)
from app.services.auth.token_service import (
    store_refresh_token,
)
from app.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.services.auth.token_service import (
    store_refresh_token,
    validate_refresh_token,
    revoke_refresh_token,
)

def register_user(
    db: Session,
    user_data: RegisterRequest,
) -> User:

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    user = User(
        name=user_data.name.strip(),
        email=user_data.email.lower(),
        password_hash=hash_password(
            user_data.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



def login_user(
    db: Session,
    login_data: LoginRequest,
) -> dict:

    user = (
        db.query(User)
        .filter(
            User.email == login_data.email.lower()
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        user.id
    )

    refresh_token = create_refresh_token(
        user.id
    )

    store_refresh_token(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(
    db: Session,
    refresh_token: str,
) -> dict:

    # --------------------------------------------
    # 1. Decode JWT
    # --------------------------------------------

    try:
        payload = decode_token(
            refresh_token
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )


    # --------------------------------------------
    # 2. Make sure it is a refresh token
    # --------------------------------------------

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )


    # --------------------------------------------
    # 3. Get user ID from JWT
    # --------------------------------------------

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )


    # --------------------------------------------
    # 4. Validate token against database
    # --------------------------------------------

    old_token = validate_refresh_token(
        db=db,
        refresh_token=refresh_token,
    )

    if old_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is expired or revoked.",
        )


    # --------------------------------------------
    # 5. Make sure DB token belongs to JWT user
    # --------------------------------------------

    if old_token.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )


    # --------------------------------------------
    # 6. Revoke old refresh token
    # --------------------------------------------

    revoke_refresh_token(
        db=db,
        token_record=old_token,
    )


    # --------------------------------------------
    # 7. Generate NEW tokens
    # --------------------------------------------

    new_access_token = create_access_token(
        user_id
    )

    new_refresh_token = create_refresh_token(
        user_id
    )


    # --------------------------------------------
    # 8. Store NEW refresh token hash
    # --------------------------------------------

    store_refresh_token(
        db=db,
        user_id=user_id,
        refresh_token=new_refresh_token,
    )


    # --------------------------------------------
    # 9. Return new token pair
    # --------------------------------------------

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


