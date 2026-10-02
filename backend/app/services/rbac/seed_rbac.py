from app.db.database import SessionLocal
from app.models.role_permission_model import Role, Permission,RolePermission
# IMPORTANT:
# Import existing User model so SQLAlchemy registers it.
from app.db.auth_model import User

ROLES = [
    {
        "name": "admin",
        "description": "Full system access",
    },
    {
        "name": "manager",
        "description": "Manager-level access",
    },
    {
        "name": "employee",
        "description": "Standard employee access",
    },
]


PERMISSIONS = [
    {
        "name": "jira:create",
        "description": "Create Jira tickets",
    },
    {
        "name": "jira:read",
        "description": "Read Jira tickets",
    },
    {
        "name": "jira:update",
        "description": "Update Jira tickets",
    },
    {
        "name": "jira:delete",
        "description": "Delete Jira tickets",
    },
    {
        "name": "rag:query",
        "description": "Query company knowledge base",
    },
    {
        "name": "mcp:execute",
        "description": "Execute MCP tools",
    },
]



def seed_roles(db):
    for role_data in ROLES:
        existing_role = (
            db.query(Role)
            .filter(Role.name == role_data["name"])
            .first()
        )

        if existing_role is None:
            role = Role(**role_data)
            db.add(role)

    db.commit()


def seed_permissions(db):
    for permission_data in PERMISSIONS:
        existing_permission = (
            db.query(Permission)
            .filter(
                Permission.name == permission_data["name"]
            )
            .first()
        )

        if existing_permission is None:
            permission = Permission(**permission_data)
            db.add(permission)

    db.commit()


def seed_role_permissions(db):
    role_permissions = {
        "admin": [
            "jira:create",
            "jira:read",
            "jira:update",
            "jira:delete",
            "rag:query",
            "mcp:execute",
        ],
        "manager": [
            "jira:create",
            "jira:read",
            "jira:update",
            "rag:query",
            "mcp:execute",
        ],
        "employee": [
            "jira:create",
            "jira:read",
            "rag:query",
        ],
    }

    for role_name, permission_names in role_permissions.items():

        role = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if role is None:
            continue

        for permission_name in permission_names:

            permission = (
                db.query(Permission)
                .filter(
                    Permission.name == permission_name
                )
                .first()
            )

            if permission is None:
                continue

            existing = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
                .first()
            )

            if existing is None:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permission.id,
                )

                db.add(role_permission)

    db.commit()

def main():
    db = SessionLocal()

    try:
        seed_roles(db)
        seed_permissions(db)
        seed_role_permissions(db)

        print("RBAC seed completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()