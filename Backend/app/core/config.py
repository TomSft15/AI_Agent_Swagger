from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application
    PROJECT_NAME: str = "AI Agent Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SUPERADMIN_PWD: str
    
    # Database
    DATABASE_URL: str
    
    # CORS - Use Union to prevent JSON parsing
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ""

    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v or v.strip() == "":
                return []
            # Remove brackets if present
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = v[1:-1]
            # Split by comma and clean each URL
            return [i.strip().strip('"').strip("'") for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_parse_none_str="null"
    )


settings = Settings()