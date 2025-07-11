from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "SyllaAI API"
    debug: bool = False
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs - MOVED FROM CLIENT SIDE!
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    
    # Redis (for background jobs)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File upload
    max_file_size_mb: int = 10
    allowed_file_types: list[str] = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()