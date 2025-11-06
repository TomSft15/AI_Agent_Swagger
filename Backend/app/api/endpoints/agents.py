from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentList,
    AgentSimple,
    AgentSimpleList,
    AgentCreateResult
)
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/", response_model=AgentCreateResult, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an AI agent from a Swagger document.
    
    Args:
        agent_in: Agent creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Agent creation result with generated functions
    """
    result = agent_service.create(
        db=db,
        user_id=current_user.id,
        agent_in=agent_in
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return AgentCreateResult(
        success=result["success"],
        message=result["message"],
        agent=result["agent"],
        functions_count=result["functions_count"],
        errors=result.get("errors")
    )


@router.get("/", response_model=AgentSimpleList)
def list_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all agents for current user (lightweight response).

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of agents with minimal data
    """
    agents = agent_service.get_all_by_user_simple(db, current_user.id, skip, limit)
    total = agent_service.count_by_user(db, current_user.id)

    return AgentSimpleList(
        items=agents,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get("/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get agent by ID.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Agent details with functions
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=Agent)
def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update agent configuration.
    
    Args:
        agent_id: Agent ID
        agent_update: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent_service.update(db, agent, agent_update)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete agent.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent_service.delete(db, agent)


@router.post("/{agent_id}/regenerate", response_model=AgentCreateResult)
def regenerate_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate agent's system prompt and functions from current Swagger doc.
    
    Useful when Swagger doc has been updated.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Regeneration result
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    result = agent_service.regenerate(db, agent)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return AgentCreateResult(
        success=result["success"],
        message=result["message"],
        agent=result["agent"],
        functions_count=result.get("functions_count"),
        errors=result.get("errors")
    )


@router.post("/{agent_id}/activate", response_model=Agent)
def activate_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Activate agent.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    from app.schemas.agent import AgentUpdate
    return agent_service.update(db, agent, AgentUpdate(is_active=True))


@router.post("/{agent_id}/deactivate", response_model=Agent)
def deactivate_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate agent.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated agent
        
    Raises:
        HTTPException: If agent not found
    """
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    from app.schemas.agent import AgentUpdate
    return agent_service.update(db, agent, AgentUpdate(is_active=False))