from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.auth_model import User
from app.models.Jira_connection_model import JiraConnection
from app.services.auth.dependencies import get_current_user
from app.services.jira_integrations.jira_cloud.jira_auth import (
    build_jira_authorization_url,
    exchange_code_for_token,
    find_jira_resource,
    get_accessible_resources,
    validate_jira_oauth_state,
    get_access_token_expiry,

)
from app.services.jira_integrations.jira_cloud.jira_token_service import (
    refresh_jira_access_token_for_user,
)
from app.schemas.jira_cloud_schema import JiraIssueSearchRequest

from app.services.jira_integrations.jira_cloud.jira_client import JiraClient


router = APIRouter(
    prefix="/api/integrations/jira",
    tags=["Jira Integration"],
)



    
@router.get("/me")
async def get_jira_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        result = await jira_client.get_myself()

        return {
            "message": "Jira API request successful.",
            "jira_user": result
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get("/server-info")
async def get_jira_server_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:

        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        result = await jira_client.get_server_info()

        return {
            "message": "Jira server information retrieved successfully.",
            "server_info": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

@router.post("/refresh-token")
async def refresh_jira_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:

        result = await refresh_jira_access_token_for_user(
            db=db,
            user_id=current_user.id,
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/projects")
async def get_jira_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        projects = await jira_client.get_projects()

        return {
            "message": "Jira projects retrieved successfully.",
            "projects": projects
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

@router.get("/projects/{project_key}")
async def get_jira_project(
    project_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        result = await jira_client.get_project(project_key)

        return {
            "message": "Jira project retrieved successfully.",
            "project": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.post("/issues")
async def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = JiraClient(
        db=db,
        user_id=current_user.id,
    )

    return await client.create_issue(
        project_key=project_key,
        summary=summary,
        description=description,
        issue_type=issue_type,
    )



@router.post("/issues/search")
async def search_jira_issues(
    request: JiraIssueSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        result = await jira_client.get_issues(
            jql=request.jql,
            max_results=request.max_results,
        )

        return {
            "message": "Jira issues retrieved successfully.",
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get("/issues/{issue_key}")
async def get_jira_issue(
    issue_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        jira_client = JiraClient(
            db=db,
            user_id=current_user.id
        )

        result = await jira_client.get_issue(issue_key)

        return {
            "message": "Jira issue retrieved successfully.",
            "issue": result
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.put("/issues/{issue_key}")
async def update_jira_issue(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = JiraClient(
        db=db,
        user_id=current_user.id,
    )

    return await client.update_issue(
        issue_key=issue_key,
        summary=summary,
        description=description,
    )

@router.get("/connect")
def connect_jira(
    current_user: User = Depends(get_current_user),
):
    """
    Start Jira Cloud OAuth 2.0 (3LO) authorization.
    """

    authorization_url = build_jira_authorization_url(
        user_id=current_user.id
    )

    return RedirectResponse(
        url=authorization_url,
        status_code=302,
    )


@router.get("/callback")
async def jira_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """
    Handle the OAuth callback from Atlassian.

    Flow:
        authorization code
            ↓
        exchange for tokens
            ↓
        get accessible Jira resources
            ↓
        identify Jira Cloud site
            ↓
        save connection in PostgreSQL
    """

    try:
        # -------------------------------------------------
        # 1. Validate OAuth state
        # -------------------------------------------------

        user_id = validate_jira_oauth_state(state)

        # -------------------------------------------------
        # 2. Exchange authorization code for tokens
        # -------------------------------------------------

        token_data = await exchange_code_for_token(code)

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        access_token_expires_at = get_access_token_expiry(
            token_data
        )

        if not access_token:
            raise ValueError(
                "Atlassian did not return an access token."
            )

        # -------------------------------------------------
        # 3. Get accessible Atlassian resources
        # -------------------------------------------------

        resources = await get_accessible_resources(
            access_token
        )

        # -------------------------------------------------
        # 4. Find Jira Cloud resource
        # -------------------------------------------------

        jira_resource = find_jira_resource(resources)

        cloud_id = jira_resource.get("id")
        site_name = jira_resource.get("name")
        site_url = jira_resource.get("url")

        if not cloud_id:
            raise ValueError(
                "Jira Cloud ID was not returned by Atlassian."
            )

        if not site_url:
            raise ValueError(
                "Jira site URL was not returned by Atlassian."
            )

        # -------------------------------------------------
        # 5. Verify application user exists
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            raise ValueError(
                "Application user no longer exists."
            )

        # -------------------------------------------------
        # 6. Check existing Jira connection
        # -------------------------------------------------

        connection = (
            db.query(JiraConnection)
            .filter(
                JiraConnection.user_id == user_id
            )
            .first()
        )

        # -------------------------------------------------
        # 7. Create or update connection
        # -------------------------------------------------

        if connection is None:

            connection = JiraConnection(
                user_id=user_id,
                cloud_id=cloud_id,
                site_name=site_name,
                site_url=site_url,
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_at=access_token_expires_at,
            )

            db.add(connection)

        else:

            connection.cloud_id = cloud_id
            connection.site_name = site_name
            connection.site_url = site_url
            connection.access_token = access_token
 
            
            if refresh_token:
                connection.refresh_token = refresh_token

            connection.access_token_expires_at = (
                access_token_expires_at
            )
        # -------------------------------------------------
        # 8. Commit connection
        # -------------------------------------------------

        db.commit()
        db.refresh(connection)

        # -------------------------------------------------
        # 9. Return safe response
        # -------------------------------------------------

        return {
            "message": "Jira Cloud connection saved successfully.",
            "connection_id": connection.id,
            "user_id": connection.user_id,
            "cloud_id": connection.cloud_id,
            "site_name": connection.site_name,
            "site_url": connection.site_url,
            "token_received": True,
            "refresh_token_received": bool(
                connection.refresh_token
            ),
        }

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save Jira Cloud connection.",
        )



@router.get("/resources")
async def get_jira_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        from app.services.jira_integrations.jira_cloud.jira_token_service import (
            get_valid_jira_access_token,
        )

        access_token = await get_valid_jira_access_token(
            db=db,
            user_id=current_user.id
        )

        resources = await get_accessible_resources(
            access_token
        )

        return resources

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )