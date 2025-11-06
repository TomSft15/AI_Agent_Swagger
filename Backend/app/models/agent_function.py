from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class AgentFunction(Base):
    """Model for storing custom descriptions for agent functions."""

    __tablename__ = "agent_functions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Function identification (from Swagger endpoint)
    operation_id = Column(String(255), nullable=False, index=True)  # e.g., "getPetById"
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    path = Column(String(500), nullable=False)  # /pets/{petId}

    # User's custom description to help the LLM
    custom_description = Column(Text, nullable=True)

    # Flag to enable/disable this function for the agent
    is_enabled = Column(Integer, default=1)  # Boolean: is function available to agent?

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    agent = relationship("Agent", backref="function_customizations")

    def __repr__(self):
        return f"<AgentFunction {self.method} {self.path}>"
