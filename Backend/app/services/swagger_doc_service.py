"""
SwaggerDoc Service

This service handles CRUD operations for Swagger documents
and orchestrates parsing and storage.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.swagger_doc import SwaggerDoc
from app.models.endpoint import Endpoint
from app.schemas.swagger_doc import SwaggerDocCreate, SwaggerDocUpdate, SwaggerDocCreateDirect
from app.services.swagger_parser import swagger_parser


class SwaggerDocService:
    """Service for managing Swagger documents."""
    
    @staticmethod
    def get_by_id(db: Session, doc_id: int, user_id: int) -> Optional[SwaggerDoc]:
        """
        Get Swagger doc by ID (only if owned by user).
        
        Args:
            db: Database session
            doc_id: Document ID
            user_id: Owner user ID
            
        Returns:
            SwaggerDoc or None
        """
        return db.query(SwaggerDoc).filter(
            SwaggerDoc.id == doc_id,
            SwaggerDoc.user_id == user_id
        ).first()
    
    @staticmethod
    def get_all_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SwaggerDoc]:
        """
        Get all Swagger docs for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of SwaggerDoc
        """
        return db.query(SwaggerDoc).filter(
            SwaggerDoc.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_by_user(db: Session, user_id: int) -> int:
        """
        Count Swagger docs for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Count of documents
        """
        return db.query(SwaggerDoc).filter(
            SwaggerDoc.user_id == user_id
        ).count()
    
    @staticmethod
    async def create_from_file(
        db: Session,
        user_id: int,
        file: UploadFile,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Swagger doc from uploaded file.
        
        Args:
            db: Database session
            user_id: Owner user ID
            file: Uploaded file
            name: Name for the document
            description: Optional description
            
        Returns:
            Dictionary with result info
        """
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine file format
        file_format = "json"
        if file.filename.endswith(('.yaml', '.yml')):
            file_format = "yaml"
        
        # Parse content
        try:
            spec = swagger_parser.parse_content(content_str, file_format)
        except ValueError as e:
            return {
                "success": False,
                "message": f"Failed to parse file: {str(e)}",
                "errors": [str(e)]
            }
        
        # Create doc from parsed spec
        return SwaggerDocService.create_from_spec(
            db=db,
            user_id=user_id,
            name=name,
            description=description,
            spec=spec,
            file_format=file_format
        )
    
    @staticmethod
    def create_from_spec(
        db: Session,
        user_id: int,
        name: str,
        spec: Dict[str, Any],
        description: Optional[str] = None,
        file_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Create Swagger doc from specification dictionary.
        
        Args:
            db: Database session
            user_id: Owner user ID
            name: Name for the document
            spec: OpenAPI specification
            description: Optional description
            file_format: Format (json/yaml)
            
        Returns:
            Dictionary with result info
        """
        errors = []
        
        # Validate spec
        is_valid, validation_error = swagger_parser.validate_openapi_spec(spec)
        if not is_valid:
            errors.append(f"Validation error: {validation_error}")
        
        # Extract info
        openapi_version = swagger_parser.get_openapi_version(spec)
        if not openapi_version:
            errors.append("Could not determine OpenAPI/Swagger version")
        
        base_url = swagger_parser.get_base_url(spec)
        api_info = swagger_parser.get_api_info(spec)
        
        # Use API title as name if not provided
        if not name or name.strip() == "":
            name = api_info.get("title", "Untitled API")
        
        # Use API description if not provided
        if not description:
            description = api_info.get("description")
        
        # Extract endpoints
        try:
            endpoints_data = swagger_parser.extract_endpoints(spec)
        except Exception as e:
            errors.append(f"Failed to extract endpoints: {str(e)}")
            endpoints_data = []
        
        # Create SwaggerDoc
        swagger_doc = SwaggerDoc(
            user_id=user_id,
            name=name,
            description=description,
            version=api_info.get("version"),
            base_url=base_url,
            spec=spec,
            endpoints_count=len(endpoints_data),
            file_format=file_format,
            openapi_version=openapi_version
        )
        
        db.add(swagger_doc)
        db.flush()  # Get the ID without committing
        
        # Create Endpoint records
        for endpoint_data in endpoints_data:
            endpoint = Endpoint(
                swagger_doc_id=swagger_doc.id,
                method=endpoint_data["method"],
                path=endpoint_data["path"],
                summary=endpoint_data.get("summary"),
                description=endpoint_data.get("description"),
                operation_id=endpoint_data.get("operation_id"),
                tags=endpoint_data.get("tags"),
                parameters=endpoint_data.get("parameters"),
                request_body=endpoint_data.get("request_body"),
                responses=endpoint_data.get("responses"),
                security=endpoint_data.get("security"),
                deprecated=1 if endpoint_data.get("deprecated") else 0
            )
            db.add(endpoint)
        
        db.commit()
        db.refresh(swagger_doc)
        
        return {
            "success": True,
            "message": f"Successfully parsed {len(endpoints_data)} endpoints",
            "swagger_doc": swagger_doc,
            "endpoints_count": len(endpoints_data),
            "errors": errors if errors else None
        }
    
    @staticmethod
    def update(
        db: Session,
        swagger_doc: SwaggerDoc,
        doc_update: SwaggerDocUpdate
    ) -> SwaggerDoc:
        """
        Update Swagger doc metadata.
        
        Args:
            db: Database session
            swagger_doc: SwaggerDoc instance
            doc_update: Update data
            
        Returns:
            Updated SwaggerDoc
        """
        update_data = doc_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(swagger_doc, field, value)
        
        db.add(swagger_doc)
        db.commit()
        db.refresh(swagger_doc)
        return swagger_doc
    
    @staticmethod
    def delete(db: Session, swagger_doc: SwaggerDoc) -> None:
        """
        Delete Swagger doc and all associated endpoints.
        
        Args:
            db: Database session
            swagger_doc: SwaggerDoc instance
        """
        db.delete(swagger_doc)
        db.commit()
    
    @staticmethod
    def get_endpoints(
        db: Session,
        swagger_doc_id: int,
        user_id: int
    ) -> Optional[List[Endpoint]]:
        """
        Get all endpoints for a Swagger doc.
        
        Args:
            db: Database session
            swagger_doc_id: SwaggerDoc ID
            user_id: User ID (for authorization)
            
        Returns:
            List of Endpoints or None if doc not found/unauthorized
        """
        # Verify ownership
        swagger_doc = SwaggerDocService.get_by_id(db, swagger_doc_id, user_id)
        if not swagger_doc:
            return None
        
        return db.query(Endpoint).filter(
            Endpoint.swagger_doc_id == swagger_doc_id
        ).all()


# Singleton instance
swagger_doc_service = SwaggerDocService()