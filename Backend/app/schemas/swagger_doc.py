from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Base Swagger schema
class SwaggerDocBase(BaseModel):
    """Base schema for Swagger documentation."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: Optional[str] = None
    base_url: Optional[str] = None


# Schema for creating a Swagger doc (via file upload)
class SwaggerDocCreate(BaseModel):
    """Schema for creating a Swagger doc from uploaded content."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Dict[str, Any]  # The actual Swagger/OpenAPI spec
    file_format: str = Field(default="json", pattern="^(json|yaml)$")


# Schema for creating a Swagger doc (via direct JSON)
class SwaggerDocCreateDirect(SwaggerDocBase):
    """Schema for creating a Swagger doc from direct JSON input."""
    spec: Dict[str, Any]  # The actual Swagger/OpenAPI spec
    file_format: str = Field(default="json", pattern="^(json|yaml)$")


# Schema for updating a Swagger doc
class SwaggerDocUpdate(BaseModel):
    """Schema for updating Swagger doc metadata."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    base_url: Optional[str] = None


# Schema for Swagger doc response
class SwaggerDoc(SwaggerDocBase):
    """Schema for Swagger doc response."""
    id: int
    user_id: int
    endpoints_count: int
    file_format: Optional[str]
    openapi_version: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for Swagger doc with full spec
class SwaggerDocWithSpec(SwaggerDoc):
    """Schema for Swagger doc with complete specification."""
    spec: Dict[str, Any]


# Schema for Swagger doc list response
class SwaggerDocList(BaseModel):
    """Schema for paginated list of Swagger docs."""
    items: List[SwaggerDoc]
    total: int
    page: int
    page_size: int
    
    
# Schema for parsing result
class SwaggerParseResult(BaseModel):
    """Schema for parsing result."""
    success: bool
    message: str
    swagger_doc: Optional[SwaggerDoc] = None
    endpoints_count: Optional[int] = None
    errors: Optional[List[str]] = None