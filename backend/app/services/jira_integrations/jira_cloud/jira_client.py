import httpx
from sqlalchemy.orm import Session

from app.services.jira_integrations.jira_cloud.jira_token_service import (
    get_jira_connection,
    get_valid_jira_access_token,
    refresh_jira_access_token_for_user,
)


class JiraClient:

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:

        access_token = await get_valid_jira_access_token(
            db=self.db,
            user_id=self.user_id,
        )

        headers = kwargs.pop("headers", {})

        headers["Authorization"] = (
            f"Bearer {access_token}"
        )

        headers.setdefault(
            "Accept",
            "application/json",
        )

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.request(
                method,
                url,
                headers=headers,
                **kwargs,
            )

            # ---------------------------------------------
            # Token rejected by Jira
            # ---------------------------------------------

            if response.status_code == 401:

                print(
                    "JIRA API: Initial request returned 401.",
                )

                try:
                    access_token = await refresh_jira_access_token_for_user(
                        db=self.db,
                        user_id=self.user_id,
                    )

                    print(
                        "JIRA API: Automatic token refresh successful."
                    )

                except Exception as exc:

                    print(
                        "JIRA API: Automatic token refresh FAILED:",
                        str(exc),
                    )

                    raise

                headers["Authorization"] = (
                    f"Bearer {access_token}"
                )

                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs,
                )

                print(
                    "JIRA API: Retry status:",
                    response.status_code,
                )

        return response

    async def get_server_info(self) -> dict:

        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        access_token = await get_valid_jira_access_token(
            db=self.db,
            user_id=self.user_id
        )

        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/serverInfo"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                url,
                headers=headers
            )

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()

    async def get_myself(self) -> dict:
        """
        Get the currently authenticated Jira Cloud user.
        """

        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )


        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/myself"
        )
        response = await self._request(
            "GET",
            url,
        )

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()
    


    async def get_projects(self) -> list[dict]:
        """
        Get Jira projects accessible to the connected user.
        """

        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )


        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/project"
        )

        response = await self._request(
            "GET",
            url,
        )

    

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()

    async def get_project(
        self,
        project_key: str,
    ) -> dict:

        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id,
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/project/{project_key}"
        )

        response = await self._request(
            "GET",
            url,
        )

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()

    

    async def get_issues(
        self,
        jql: str,
        max_results: int = 20,
    ) -> dict:
        """
        Search Jira issues using JQL.
        """

        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        

        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/search/jql"
        )

        

        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": [
            "summary",
            "status",
            "issuetype",
        ],
        }

        response = await self._request(
            "POST",
            url,
            headers={
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()


    async def get_issue(self, issue_key: str) -> dict:
        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        access_token = await get_valid_jira_access_token(
            db=self.db,
            user_id=self.user_id
        )

        url = (
            f"https://api.atlassian.com"
            f"/ex/jira/{connection.cloud_id}"
            f"/rest/api/3/issue/{issue_key}"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=headers
            )

        if response.is_error:
            raise ValueError(
                f"Jira API request failed: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()


    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
    ):
        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id,
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        cloud_id = connection.cloud_id

        url = (
            f"https://api.atlassian.com/ex/jira/"
            f"{cloud_id}/rest/api/3/issue"
        )

        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue_type
                }
            }
        }

        response = await self._request(
            "POST",
            url,
            json=payload,
        )

        if response.is_error:
            print("JIRA CREATE ISSUE STATUS:", response.status_code)
            print("JIRA CREATE ISSUE RESPONSE:", response.text)


        response.raise_for_status()

        return response.json()



    async def update_issue(
        self,
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
    ):
        connection = get_jira_connection(
            db=self.db,
            user_id=self.user_id,
        )

        if connection is None:
            raise ValueError(
                "Jira Cloud is not connected for this user."
            )

        cloud_id = connection.cloud_id

        url = (
            f"https://api.atlassian.com/ex/jira/"
            f"{cloud_id}/rest/api/3/issue/{issue_key}"
        )

        fields = {}

        if summary is not None:
            fields["summary"] = summary

        if description is not None:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }

        if not fields:
            raise ValueError(
                "At least one field must be provided for update."
            )

        payload = {
            "fields": fields
        }

        response = await self._request(
            "PUT",
            url,
            json=payload,
        )

        if response.status_code == 204:
            return {
                "message": "Jira issue updated successfully.",
                "issue_key": issue_key,
            }

        response.raise_for_status()

        return response.json()
    

    