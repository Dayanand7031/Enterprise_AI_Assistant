from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise AI Assistant"
    APP_ENV: str = "development"

    DATABASE_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Jira Cloud OAuth 2.0
    JIRA_CLIENT_ID: str
    JIRA_CLIENT_SECRET: str
    JIRA_REDIRECT_URI: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()