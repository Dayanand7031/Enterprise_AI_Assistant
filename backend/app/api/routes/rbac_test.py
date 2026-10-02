from fastapi import APIRouter, Depends

from app.models.auth_model import User

from app.services.rbac.dependencies import require_permission


router = APIRouter(
    prefix="/api/rbac-test",
    tags=["RBAC Test"],
)


@router.get("/jira-read")
def test_jira_read_permission(
    current_user: User = Depends(
        require_permission("jira:read")
    ),
):
    return {
        "message": "You have jira:read permission.",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.name if current_user.role else None,
    }


@router.get("/jira-delete")
def test_jira_delete_permission(
    current_user: User = Depends(
        require_permission("jira:delete")
    ),
):
    return {
        "message": "You have jira:delete permission.",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.name if current_user.role else None,
    }


@router.get("/fake-permission")
def test_fake_permission(
    current_user: User = Depends(
        require_permission("something:not_allowed")
    ),
):
    return {
        "message": "You have the fake permission.",
    }