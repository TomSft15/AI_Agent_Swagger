from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Base User schema
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


# Schema for creating a new user
class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)


# Schema for updating user
class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Schema for setting LLM API keys
class UserLLMKeysUpdate(BaseModel):
    """Schema for updating user's LLM API keys."""
    openai_api_key: Optional[str] = Field(None, min_length=20)
    anthropic_api_key: Optional[str] = Field(None, min_length=20)


# Schema for user response (without password)
class User(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_superuser: bool
    has_openai_key: bool = False
    has_anthropic_key: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for user with masked keys
class UserWithKeys(User):
    """Schema for user with masked API keys."""
    openai_api_key_masked: Optional[str] = None
    anthropic_api_key_masked: Optional[str] = None


# Schema for user in database (internal use)
class UserInDB(User):
    """Schema for user stored in database."""
    hashed_password: str


# Token schemas
class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[int] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for user login with username or email."""
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str