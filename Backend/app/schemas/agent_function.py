"""Pydantic schemas for agent function customization."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentFunctionBase(BaseModel):
    """Base schema for agent function customization."""
    operation_id: str = Field(..., description="Operation ID from Swagger/OpenAPI")
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")
    path: str = Field(..., description="API endpoint path")
    custom_description: Optional[str] = Field(None, description="Custom description to help the LLM")
    is_enabled: bool = Field(True, description="Whether this function is enabled for the agent")


class AgentFunctionCreate(AgentFunctionBase):
    """Schema for creating a new agent function customization."""
    agent_id: int = Field(..., description="ID of the agent")


class AgentFunctionUpdate(BaseModel):
    """Schema for updating an agent function customization."""
    custom_description: Optional[str] = Field(None, description="Custom description to help the LLM")
    is_enabled: Optional[bool] = Field(None, description="Whether this function is enabled for the agent")


class AgentFunction(AgentFunctionBase):
    """Schema for agent function with all fields."""
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentFunctionBulkUpdate(BaseModel):
    """Schema for bulk updating multiple function customizations."""
    functions: list[AgentFunctionUpdate] = Field(..., description="List of function updates with operation_id as key")

    class Config:
        schema_extra = {
            "example": {
                "functions": [
                    {
                        "operation_id": "getPetById",
                        "custom_description": "Retrieves detailed information about a specific pet using its unique ID",
                        "is_enabled": True
                    },
                    {
                        "operation_id": "createPet",
                        "custom_description": "Creates a new pet in the system with the provided information",
                        "is_enabled": True
                    }
                ]
            }
        }
