"""
Agent Service

This service handles CRUD operations for AI agents.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.swagger_doc import SwaggerDoc
from app.models.endpoint import Endpoint
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.agent_generator import agent_generator
from app.services.swagger_doc_service import swagger_doc_service


class AgentService:
    """Service for managing AI agents."""
    
    @staticmethod
    def get_by_id(db: Session, agent_id: int, user_id: int) -> Optional[Agent]:
        """
        Get agent by ID (only if owned by user).
        
        Args:
            db: Database session
            agent_id: Agent ID
            user_id: Owner user ID
            
        Returns:
            Agent or None
        """
        return db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.user_id == user_id
        ).first()
    
    @staticmethod
    def get_all_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Agent]:
        """
        Get all agents for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Agent
        """
        return db.query(Agent).filter(
            Agent.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_by_user(db: Session, user_id: int) -> int:
        """
        Count agents for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Count of agents
        """
        return db.query(Agent).filter(
            Agent.user_id == user_id
        ).count()
    
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        agent_in: AgentCreate
    ) -> Dict[str, Any]:
        """
        Create agent from Swagger doc.
        
        Args:
            db: Database session
            user_id: Owner user ID
            agent_in: Agent creation data
            
        Returns:
            Dictionary with result info
        """
        errors = []
        
        # Get Swagger doc
        swagger_doc = swagger_doc_service.get_by_id(
            db,
            agent_in.swagger_doc_id,
            user_id
        )
        
        if not swagger_doc:
            return {
                "success": False,
                "message": "Swagger document not found or unauthorized",
                "errors": ["Swagger document not found"]
            }
        
        # Get endpoints
        endpoints = swagger_doc_service.get_endpoints(
            db,
            agent_in.swagger_doc_id,
            user_id
        )
        
        if not endpoints:
            return {
                "success": False,
                "message": "No endpoints found in Swagger document",
                "errors": ["No endpoints available"]
            }
        
        # Generate system prompt
        try:
            system_prompt = agent_generator.generate_system_prompt(swagger_doc, endpoints)
        except Exception as e:
            errors.append(f"Failed to generate system prompt: {str(e)}")
            system_prompt = f"You are an AI assistant for the {swagger_doc.name} API."
        
        # Generate function definitions
        try:
            functions = agent_generator.generate_function_definitions(endpoints)
        except Exception as e:
            errors.append(f"Failed to generate functions: {str(e)}")
            functions = []
        
        # Create agent
        agent = Agent(
            user_id=user_id,
            swagger_doc_id=agent_in.swagger_doc_id,
            name=agent_in.name,
            description=agent_in.description,
            system_prompt=system_prompt,
            available_functions=functions,
            llm_provider=agent_in.llm_provider,
            llm_model=agent_in.llm_model,
            temperature=agent_in.temperature,
            max_tokens=agent_in.max_tokens,
            is_active=True
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        return {
            "success": True,
            "message": f"Agent created with {len(functions)} functions",
            "agent": agent,
            "functions_count": len(functions),
            "errors": errors if errors else None
        }
    
    @staticmethod
    def update(
        db: Session,
        agent: Agent,
        agent_update: AgentUpdate
    ) -> Agent:
        """
        Update agent.
        
        Args:
            db: Database session
            agent: Agent instance
            agent_update: Update data
            
        Returns:
            Updated Agent
        """
        update_data = agent_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def delete(db: Session, agent: Agent) -> None:
        """
        Delete agent.
        
        Args:
            db: Database session
            agent: Agent instance
        """
        db.delete(agent)
        db.commit()
    
    @staticmethod
    def regenerate(
        db: Session,
        agent: Agent
    ) -> Dict[str, Any]:
        """
        Regenerate agent's system prompt and functions.
        
        Args:
            db: Database session
            agent: Agent instance
            
        Returns:
            Dictionary with result info
        """
        errors = []
        
        # Get Swagger doc
        swagger_doc = db.query(SwaggerDoc).filter(
            SwaggerDoc.id == agent.swagger_doc_id
        ).first()
        
        if not swagger_doc:
            return {
                "success": False,
                "message": "Associated Swagger document not found",
                "errors": ["Swagger document missing"]
            }
        
        # Get endpoints
        endpoints = db.query(Endpoint).filter(
            Endpoint.swagger_doc_id == agent.swagger_doc_id
        ).all()
        
        if not endpoints:
            return {
                "success": False,
                "message": "No endpoints found",
                "errors": ["No endpoints available"]
            }
        
        # Regenerate
        try:
            agent.system_prompt = agent_generator.generate_system_prompt(swagger_doc, endpoints)
            agent.available_functions = agent_generator.generate_function_definitions(endpoints)
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to regenerate: {str(e)}",
                "errors": [str(e)]
            }
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        return {
            "success": True,
            "message": "Agent regenerated successfully",
            "agent": agent,
            "functions_count": len(agent.available_functions)
        }


# Singleton instance
agent_service = AgentService()