from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Base Endpoint schema
class EndpointBase(BaseModel):
    """Base schema for API endpoint."""
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: str = Field(..., min_length=1, max_length=500)
    summary: Optional[str] = None
    description: Optional[str] = None
    operation_id: Optional[str] = None
    tags: Optional[List[str]] = None
    deprecated: bool = False


# Schema for Endpoint response
class Endpoint(EndpointBase):
    """Schema for endpoint response."""
    id: int
    swagger_doc_id: int
    parameters: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schema for Endpoint with full details
class EndpointDetail(Endpoint):
    """Schema for detailed endpoint with all information."""
    pass


# Schema for Endpoint list response
class EndpointList(BaseModel):
    """Schema for list of endpoints."""
    items: List[Endpoint]
    total: int
    swagger_doc_id: int


# Schema for simplified endpoint (for display)
class EndpointSimple(BaseModel):
    """Simplified endpoint schema for listings."""
    id: int
    method: str
    path: str
    summary: Optional[str]
    tags: Optional[List[str]]
    deprecated: bool = False
    
    class Config:
        from_attributes = True