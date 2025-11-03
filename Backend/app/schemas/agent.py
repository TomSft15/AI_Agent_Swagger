from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Base Agent schema
class AgentBase(BaseModel):
    """Base schema for AI agent."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    llm_provider: str = Field(default="openai", pattern="^(openai|ollama|mistral)$")
    llm_model: str = Field(default="gpt-4-turbo-preview")
    temperature: int = Field(default=70, ge=0, le=100)
    max_tokens: int = Field(default=4096, ge=1, le=128000)


# Schema for creating an agent
class AgentCreate(BaseModel):
    """Schema for creating an agent from Swagger doc."""
    swagger_doc_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    llm_provider: str = Field(default="openai", pattern="^(openai|ollama|mistral)$")
    llm_model: str = Field(default="gpt-4-turbo-preview")
    temperature: int = Field(default=70, ge=0, le=100)
    max_tokens: int = Field(default=4096, ge=1, le=128000)


# Schema for updating an agent
class AgentUpdate(BaseModel):
    """Schema for updating agent information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    llm_provider: Optional[str] = Field(None, pattern="^(openai|ollama|mistral)$")
    llm_model: Optional[str] = None
    temperature: Optional[int] = Field(None, ge=0, le=100)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_active: Optional[bool] = None


# Schema for agent response
class Agent(AgentBase):
    """Schema for agent response."""
    id: int
    user_id: int
    swagger_doc_id: int
    swagger_doc_name: Optional[str] = None
    system_prompt: str
    available_functions: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for agent with full details
class AgentDetail(Agent):
    """Schema for detailed agent information."""
    pass


# Schema for agent list response
class AgentList(BaseModel):
    """Schema for paginated list of agents."""
    items: List[Agent]
    total: int
    page: int
    page_size: int


# Schema for simplified agent (for display)
class AgentSimple(BaseModel):
    """Simplified agent schema for listings."""
    id: int
    name: str
    description: Optional[str]
    llm_provider: str
    llm_model: str
    is_active: bool
    swagger_doc_id: int
    swagger_doc_name: Optional[str] = None
    created_at: datetime
    functions_count: int = 0

    class Config:
        from_attributes = True


# Schema for simplified agent list response
class AgentSimpleList(BaseModel):
    """Schema for paginated list of simplified agents."""
    items: List[AgentSimple]
    total: int
    page: int
    page_size: int


# Schema for agent creation result
class AgentCreateResult(BaseModel):
    """Schema for agent creation result."""
    success: bool
    message: str
    agent: Optional[Agent] = None
    functions_count: Optional[int] = None
    errors: Optional[List[str]] = None