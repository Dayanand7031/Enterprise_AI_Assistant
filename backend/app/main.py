from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine


from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.mock_jira import router as mock_jira_router
from app.api.routes.auth import router as auth_router
from app.api.routes.rbac_test import router as rbac_test_router
from app.api.routes.mcp_audit import router as mcp_audit_router
from app.api.routes.jira_integration import router as jira_integration_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(mock_jira_router)
app.include_router(auth_router)
app.include_router(rbac_test_router)
app.include_router(mcp_audit_router)
app.include_router(jira_integration_router)
app.include_router(conversations_router)
app.include_router(admin_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }