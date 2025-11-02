from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Endpoint(Base):
    """Model for storing individual API endpoints from Swagger docs."""
    
    __tablename__ = "endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    swagger_doc_id = Column(Integer, ForeignKey("swagger_docs.id"), nullable=False, index=True)
    
    # HTTP method and path
    method = Column(String(10), nullable=False, index=True)  # GET, POST, PUT, DELETE, etc.
    path = Column(String(500), nullable=False, index=True)   # /users/{id}, /pets, etc.
    
    # Endpoint info
    summary = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    operation_id = Column(String(255), nullable=True, index=True)  # Unique operation identifier
    
    # Tags for categorization
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Parameters
    parameters = Column(JSON, nullable=True)  # Query params, path params, headers
    
    # Request body
    request_body = Column(JSON, nullable=True)  # Request body schema
    
    # Responses
    responses = Column(JSON, nullable=True)  # All possible responses with schemas
    
    # Security/Authentication
    security = Column(JSON, nullable=True)  # Security requirements for this endpoint
    
    # Additional metadata
    deprecated = Column(Integer, default=0)  # Boolean: is endpoint deprecated?
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    swagger_doc = relationship("SwaggerDoc", back_populates="endpoints")
    
    def __repr__(self):
        return f"<Endpoint {self.method} {self.path}>"
    
    @property
    def full_url(self):
        """Get the full URL by combining base_url and path."""
        if self.swagger_doc and self.swagger_doc.base_url:
            return f"{self.swagger_doc.base_url.rstrip('/')}/{self.path.lstrip('/')}"
        return self.path