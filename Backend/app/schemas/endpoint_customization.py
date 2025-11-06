"""Pydantic schemas for endpoint customization."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EndpointCustomizationBase(BaseModel):
    """Base schema for endpoint customization."""
    operation_id: str = Field(..., description="Operation ID from Swagger/OpenAPI")
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")
    path: str = Field(..., description="API endpoint path")
    custom_description: Optional[str] = Field(None, description="Custom description to help the LLM")
    is_enabled: bool = Field(True, description="Enable/disable this function for agents")


class EndpointCustomizationUpdate(BaseModel):
    """Schema for updating an endpoint customization."""
    custom_description: Optional[str] = Field(None, description="Custom description to help the LLM")
    is_enabled: Optional[bool] = Field(None, description="Enable/disable this function for agents")


class EndpointCustomization(EndpointCustomizationBase):
    """Schema for endpoint customization with all fields."""
    id: int
    swagger_doc_id: int
    endpoint_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
