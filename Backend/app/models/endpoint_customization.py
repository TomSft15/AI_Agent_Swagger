from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class EndpointCustomization(Base):
    """Model for storing custom descriptions for Swagger endpoints."""

    __tablename__ = "endpoint_customizations"

    id = Column(Integer, primary_key=True, index=True)
    swagger_doc_id = Column(Integer, ForeignKey("swagger_docs.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=True, index=True)

    # Function identification (from Swagger endpoint)
    operation_id = Column(String(255), nullable=False, index=True)  # e.g., "getPetById"
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    path = Column(String(500), nullable=False)  # /pets/{petId}

    # User's custom description to help the LLM
    custom_description = Column(Text, nullable=True)

    # Enable/disable this function for agents
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    swagger_doc = relationship("SwaggerDoc", backref="endpoint_customizations")
    endpoint = relationship("Endpoint", backref="customization", uselist=False)

    def __repr__(self):
        return f"<EndpointCustomization {self.method} {self.path}>"
