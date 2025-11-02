from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base


class Agent(Base):
    """Model for storing AI agents that can use APIs."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    swagger_doc_id = Column(Integer, ForeignKey("swagger_docs.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Agent configuration
    system_prompt = Column(Text, nullable=False)  # System prompt for LLM
    available_functions = Column(JSON, nullable=False)  # Functions the agent can call
    
    # LLM settings
    llm_provider = Column(String(50), default="openai")  # openai, ollama, etc.
    llm_model = Column(String(100), default="gpt-4-turbo-preview")
    temperature = Column(Integer, default=70)  # 0-100 (will be divided by 100)
    max_tokens = Column(Integer, default=4096)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="agents")
    swagger_doc = relationship("SwaggerDoc", backref="agents")
    
    def __repr__(self):
        return f"<Agent {self.name}>"
    
    @property
    def temperature_float(self):
        """Get temperature as float (0.0 - 1.0)."""
        return self.temperature / 100.0