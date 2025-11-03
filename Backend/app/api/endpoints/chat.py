"""
Chat Endpoint

Allows users to interact with their AI agents through a conversational interface.
Handles the full loop: User message → LLM → Function calls → API execution → LLM → Response
"""
import time
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, FunctionCallDetail
from app.services.agent_service import agent_service
from app.services.llm_service import llm_service
from app.services.api_executor import api_executor

router = APIRouter()


@router.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Chat with an AI agent. The agent can make real API calls based on the conversation.
    
    Args:
        agent_id: Agent ID
        chat_request: Chat request with user message
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat response with agent's reply and function call details
        
    Raises:
        HTTPException: If agent not found or not active
    """
    print(f"\n=== [CHAT ENDPOINT] Received chat request ===")
    print(f"Agent ID: {agent_id}")
    print(f"User: {current_user.email}")
    print(f"Message: {chat_request.message[:100]}...")

    # Get agent
    print(f"[CHAT ENDPOINT] Fetching agent from database...")
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        print(f"[CHAT ENDPOINT] ERROR: Agent {agent_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    print(f"[CHAT ENDPOINT] Agent found: {agent.name} (LLM: {agent.llm_provider}/{agent.llm_model})")

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not active"
        )
    
    # Generate conversation ID if not provided
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())
    print(f"[CHAT ENDPOINT] Conversation ID: {conversation_id}")

    # Build messages for LLM
    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": chat_request.message}
    ]
    print(f"[CHAT ENDPOINT] Built {len(messages)} initial messages for LLM")

    # Track function calls and API calls
    function_calls_made = []
    api_calls_made = []

    try:
        # First LLM call
        print(f"\n[CHAT ENDPOINT] Calling LLM service for first completion...")
        llm_response = await llm_service.chat_completion(
            user=current_user,
            agent=agent,
            messages=messages,
            functions=agent.available_functions
        )
        print(f"[CHAT ENDPOINT] Received LLM response")

        # Check if LLM wants to call a function
        assistant_message = llm_response["choices"][0]["message"]

        # Handle function calling loop
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while assistant_message.get("function_call") and iteration < max_iterations:
            iteration += 1
            print(f"\n[CHAT ENDPOINT] === Function call iteration {iteration} ===")
            
            function_call = assistant_message["function_call"]
            function_name = function_call["name"]
            print(f"[CHAT ENDPOINT] LLM wants to call function: {function_name}")

            # Parse arguments (they come as JSON string)
            import json
            try:
                arguments = json.loads(function_call["arguments"])
                print(f"[CHAT ENDPOINT] Function arguments: {arguments}")
            except json.JSONDecodeError:
                arguments = {}
                print(f"[CHAT ENDPOINT] WARNING: Failed to parse function arguments")

            # Execute the function (make real API call)
            start_time = time.time()
            print(f"[CHAT ENDPOINT] Executing function via API executor...")

            try:
                api_result = await api_executor.execute_function_call(
                    db=db,
                    agent=agent,
                    function_name=function_name,
                    arguments=arguments
                )

                execution_time = time.time() - start_time
                print(f"[CHAT ENDPOINT] Function execution completed in {execution_time:.2f}s")
                print(f"[CHAT ENDPOINT] API call result: success={api_result.get('success')}, status={api_result.get('status_code')}")

                # Track the function call
                function_calls_made.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "success": api_result.get("success", False),
                    "execution_time": execution_time
                })

                # Track the API call details
                api_calls_made.append({
                    "method": api_result.get("method"),
                    "url": api_result.get("url"),
                    "status_code": api_result.get("status_code"),
                    "success": api_result.get("success", False)
                })

                # Format result for LLM
                result_str = api_executor.format_result_for_llm(api_result)

                print(f"[CHAT ENDPOINT] Formatted result for LLM (first 200 chars): {result_str[:200]}...")
                
            except Exception as e:
                print(f"[CHAT ENDPOINT] ERROR during function execution: {str(e)}")
                result_str = f"Error executing function: {str(e)}"
                function_calls_made.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "success": False,
                    "error": str(e)
                })

            # Add function call and result to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": function_call
            })
            messages.append({
                "role": "function",
                "name": function_name,
                "content": result_str
            })
            print(f"[CHAT ENDPOINT] Added function call and result to conversation history")

            # Call LLM again with the function result
            print(f"[CHAT ENDPOINT] Calling LLM again with function result...")
            llm_response = await llm_service.chat_completion(
                user=current_user,
                agent=agent,
                messages=messages,
                functions=agent.available_functions
            )
            print(f"[CHAT ENDPOINT] Received LLM response for iteration {iteration}")

            assistant_message = llm_response["choices"][0]["message"]

        # Get final response content
        print(f"\n[CHAT ENDPOINT] Function calling loop completed (iterations: {iteration})")
        final_content = assistant_message.get("content", "")

        if not final_content:
            final_content = "I completed the action but couldn't generate a response."

        print(f"[CHAT ENDPOINT] Final response: {final_content[:100]}...")
        print(f"[CHAT ENDPOINT] Total function calls made: {len(function_calls_made)}")
        print(f"[CHAT ENDPOINT] Returning chat response\n")

        return ChatResponse(
            message=final_content,
            conversation_id=conversation_id,
            function_calls=function_calls_made if function_calls_made else None,
            api_calls=api_calls_made if api_calls_made else None
        )
        
    except ValueError as e:
        # LLM API key error or similar
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/agents/{agent_id}/test-function")
async def test_function_execution(
    agent_id: int,
    function_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Test endpoint to manually execute a function without LLM.
    Useful for debugging.
    
    Args:
        agent_id: Agent ID
        function_name: Name of function to test
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Function execution result
    """
    # Get agent
    agent = agent_service.get_by_id(db, agent_id, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Test with empty arguments
    try:
        result = await api_executor.execute_function_call(
            db=db,
            agent=agent,
            function_name=function_name,
            arguments={}
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution error: {str(e)}"
        )