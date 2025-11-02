from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.swagger_doc import (
    SwaggerDoc,
    SwaggerDocCreate,
    SwaggerDocCreateDirect,
    SwaggerDocUpdate,
    SwaggerDocWithSpec,
    SwaggerDocList,
    SwaggerParseResult
)
from app.schemas.endpoint import Endpoint, EndpointList
from app.services.swagger_doc_service import swagger_doc_service
from app.services.swagger_parser import swagger_parser

router = APIRouter()


@router.post("/upload", response_model=SwaggerParseResult, status_code=status.HTTP_201_CREATED)
async def upload_swagger_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a Swagger/OpenAPI file (JSON or YAML).
    
    Args:
        file: Swagger/OpenAPI file (JSON or YAML)
        name: Name for the API documentation
        description: Optional description
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Parse result with created SwaggerDoc
    """
    # Validate file extension
    if not file.filename.endswith(('.json', '.yaml', '.yml')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be JSON or YAML format (.json, .yaml, .yml)"
        )
    
    # Create from file
    result = await swagger_doc_service.create_from_file(
        db=db,
        user_id=current_user.id,
        file=file,
        name=name,
        description=description
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return SwaggerParseResult(
        success=result["success"],
        message=result["message"],
        swagger_doc=result["swagger_doc"],
        endpoints_count=result["endpoints_count"],
        errors=result.get("errors")
    )


@router.post("/", response_model=SwaggerParseResult, status_code=status.HTTP_201_CREATED)
def create_swagger_direct(
    swagger_in: SwaggerDocCreateDirect,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create Swagger doc from direct JSON input.
    
    Args:
        swagger_in: Swagger creation data with spec
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Parse result with created SwaggerDoc
    """
    result = swagger_doc_service.create_from_spec(
        db=db,
        user_id=current_user.id,
        name=swagger_in.name,
        spec=swagger_in.spec,
        description=swagger_in.description,
        file_format=swagger_in.file_format
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return SwaggerParseResult(
        success=result["success"],
        message=result["message"],
        swagger_doc=result["swagger_doc"],
        endpoints_count=result["endpoints_count"],
        errors=result.get("errors")
    )


@router.get("/", response_model=SwaggerDocList)
def list_swagger_docs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all Swagger docs for current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of Swagger docs
    """
    docs = swagger_doc_service.get_all_by_user(db, current_user.id, skip, limit)
    total = swagger_doc_service.count_by_user(db, current_user.id)
    
    return SwaggerDocList(
        items=docs,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{doc_id}", response_model=SwaggerDoc)
def get_swagger_doc(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Swagger doc by ID (without full spec).
    
    Args:
        doc_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SwaggerDoc information
        
    Raises:
        HTTPException: If document not found
    """
    doc = swagger_doc_service.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger document not found"
        )
    return doc


@router.get("/{doc_id}/spec", response_model=SwaggerDocWithSpec)
def get_swagger_spec(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Swagger doc with full specification.
    
    Args:
        doc_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SwaggerDoc with complete spec
        
    Raises:
        HTTPException: If document not found
    """
    doc = swagger_doc_service.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger document not found"
        )
    return doc


@router.get("/{doc_id}/endpoints", response_model=EndpointList)
def get_swagger_endpoints(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all endpoints for a Swagger doc.
    
    Args:
        doc_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of endpoints
        
    Raises:
        HTTPException: If document not found
    """
    endpoints = swagger_doc_service.get_endpoints(db, doc_id, current_user.id)
    if endpoints is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger document not found"
        )
    
    return EndpointList(
        items=endpoints,
        total=len(endpoints),
        swagger_doc_id=doc_id
    )


@router.put("/{doc_id}", response_model=SwaggerDoc)
def update_swagger_doc(
    doc_id: int,
    doc_update: SwaggerDocUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update Swagger doc metadata.
    
    Args:
        doc_id: Document ID
        doc_update: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated SwaggerDoc
        
    Raises:
        HTTPException: If document not found
    """
    doc = swagger_doc_service.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger document not found"
        )
    
    return swagger_doc_service.update(db, doc, doc_update)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_swagger_doc(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete Swagger doc and all associated endpoints.
    
    Args:
        doc_id: Document ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If document not found
    """
    doc = swagger_doc_service.get_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swagger document not found"
        )
    
    swagger_doc_service.delete(db, doc)