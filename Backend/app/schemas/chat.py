from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Message schema
class ChatMessage(BaseModel):
    """Schema for a single chat message."""
    role: str = Field(..., pattern="^(user|assistant|system|function)$")
    content: str
    function_call: Optional[Dict[str, Any]] = None
    name: Optional[str] = None  # For function messages


# Chat request
class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None  # For maintaining context


# Chat response
class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    conversation_id: str
    function_calls: Optional[List[Dict[str, Any]]] = None
    api_calls: Optional[List[Dict[str, Any]]] = None  # Details of API calls made
    

# Chat history
class ChatHistory(BaseModel):
    """Schema for chat history."""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# Function call details
class FunctionCallDetail(BaseModel):
    """Details of a function call execution."""
    function_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    execution_time: float  # in seconds