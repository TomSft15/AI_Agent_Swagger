from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class SwaggerDoc(Base):
    """Model for storing Swagger/OpenAPI documentation."""
    
    __tablename__ = "swagger_docs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)  # OpenAPI version (3.0.0, 2.0, etc.)
    
    # API info
    base_url = Column(String(500), nullable=True)  # Base URL of the API
    
    # Complete specification
    spec = Column(JSON, nullable=False)  # Full Swagger/OpenAPI spec as JSON
    
    # Parsed data
    endpoints_count = Column(Integer, default=0)
    
    # Metadata
    file_format = Column(String(10), nullable=True)  # 'json' or 'yaml'
    openapi_version = Column(String(20), nullable=True)  # e.g., "3.0.0", "2.0"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    endpoints = relationship("Endpoint", back_populates="swagger_doc", cascade="all, delete-orphan")
    user = relationship("User", backref="swagger_docs")
    
    def __repr__(self):
        return f"<SwaggerDoc {self.name} (v{self.version})>"