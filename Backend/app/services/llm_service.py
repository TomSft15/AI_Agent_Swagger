"""
LLM Service

Handles communication with different LLM providers using user's personal API keys.
Supports OpenAI, Anthropic, and local Ollama.
"""
from typing import Dict, Any, List, Optional
import httpx
from app.models.user import User
from app.models.agent import Agent
from app.core.encryption import decrypt_api_key
from app.core.config import settings


class LLMService:
    """Service for interacting with LLM providers."""
    
    @staticmethod
    def get_api_key(user: User, provider: str) -> Optional[str]:
        """
        Get decrypted API key for a provider.
        
        Args:
            user: User instance
            provider: Provider name (openai, anthropic)
            
        Returns:
            Decrypted API key or None
            
        Raises:
            ValueError: If provider requires key but user doesn't have one
        """
        if provider == "openai":
            if not user.openai_api_key:
                raise ValueError(
                    "OpenAI API key required. Please add your API key in your profile settings."
                )
            return decrypt_api_key(user.openai_api_key)
        
        elif provider == "anthropic":
            if not user.anthropic_api_key:
                raise ValueError(
                    "Anthropic API key required. Please add your API key in your profile settings."
                )
            return decrypt_api_key(user.anthropic_api_key)
        
        elif provider == "ollama":
            # Ollama doesn't need an API key (local)
            return None
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @staticmethod
    async def chat_completion(
        user: User,
        agent: Agent,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion using the agent's configuration.
        
        Args:
            user: User instance (for API key)
            agent: Agent instance (for LLM config)
            messages: Chat messages
            functions: Optional function definitions for function calling
            
        Returns:
            LLM response
        """
        provider = agent.llm_provider
        print(f"\n[LLM SERVICE] === Chat completion request ===")
        print(f"[LLM SERVICE] Provider: {provider}")
        print(f"[LLM SERVICE] Model: {agent.llm_model}")
        print(f"[LLM SERVICE] Messages count: {len(messages)}")
        print(f"[LLM SERVICE] Functions available: {len(functions) if functions else 0}")

        if provider == "openai":
            return await LLMService._openai_chat_completion(
                user, agent, messages, functions
            )
        elif provider == "anthropic":
            return await LLMService._anthropic_chat_completion(
                user, agent, messages, functions
            )
        elif provider == "ollama":
            return await LLMService._ollama_chat_completion(
                agent, messages, functions
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    async def _openai_chat_completion(
        user: User,
        agent: Agent,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        OpenAI chat completion.
        
        Args:
            user: User instance
            agent: Agent instance
            messages: Chat messages
            functions: Function definitions
            
        Returns:
            OpenAI response
        """
        print(f"[LLM SERVICE - OPENAI] Getting API key...")
        api_key = LLMService.get_api_key(user, "openai")
        print(f"[LLM SERVICE - OPENAI] API key retrieved")

        # Prepare request
        payload = {
            "model": agent.llm_model,
            "messages": messages,
            "temperature": agent.temperature_float,
            "max_tokens": agent.max_tokens
        }

        # Add functions if provided
        if functions:
            # Remove metadata from functions (OpenAI doesn't need it)
            clean_functions = []
            for func in functions:
                clean_func = {
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"]
                }
                clean_functions.append(clean_func)

            payload["functions"] = clean_functions
            payload["function_call"] = "auto"
            print(f"[LLM SERVICE - OPENAI] Prepared {len(clean_functions)} functions for OpenAI")

        # Make request to OpenAI
        print(f"[LLM SERVICE - OPENAI] Sending request to OpenAI API...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"[LLM SERVICE - OPENAI] Response received from OpenAI")
            if result.get("choices") and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                has_function_call = "function_call" in message
                print(f"[LLM SERVICE - OPENAI] Response has function call: {has_function_call}")
            return result
    
    @staticmethod
    async def _anthropic_chat_completion(
        user: User,
        agent: Agent,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Anthropic (Claude) chat completion.
        
        Args:
            user: User instance
            agent: Agent instance
            messages: Chat messages
            functions: Function definitions
            
        Returns:
            Anthropic response formatted as OpenAI-like
        """
        print(f"[LLM SERVICE - ANTHROPIC] Getting API key...")
        api_key = LLMService.get_api_key(user, "anthropic")
        print(f"[LLM SERVICE - ANTHROPIC] API key retrieved")

        # Convert messages format (OpenAI -> Anthropic)
        # Anthropic uses system parameter separately
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        print(f"[LLM SERVICE - ANTHROPIC] Converted {len(messages)} messages to Anthropic format")

        # Prepare request
        payload = {
            "model": agent.llm_model,
            "messages": anthropic_messages,
            "max_tokens": agent.max_tokens,
            "temperature": agent.temperature_float
        }

        if system_message:
            payload["system"] = system_message

        # Add tools if provided (Anthropic uses "tools" instead of "functions")
        if functions:
            tools = []
            for func in functions:
                tool = {
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"]
                }
                tools.append(tool)
            payload["tools"] = tools
            print(f"[LLM SERVICE - ANTHROPIC] Prepared {len(tools)} tools for Anthropic")

        # Make request to Anthropic
        print(f"[LLM SERVICE - ANTHROPIC] Sending request to Anthropic API...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()

            # Convert Anthropic response to OpenAI format
            anthropic_response = response.json()
            print(f"[LLM SERVICE - ANTHROPIC] Response received from Anthropic")
            result = LLMService._convert_anthropic_to_openai_format(anthropic_response)
            print(f"[LLM SERVICE - ANTHROPIC] Converted to OpenAI format")
            return result
    
    @staticmethod
    async def _ollama_chat_completion(
        agent: Agent,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Ollama chat completion (local).
        
        Args:
            agent: Agent instance
            messages: Chat messages
            functions: Function definitions
            
        Returns:
            Ollama response formatted as OpenAI-like
        """
        print(f"[LLM SERVICE - OLLAMA] Using local Ollama")
        # Ollama endpoint (default local)
        ollama_url = "http://localhost:11434/api/chat"

        # Prepare request
        payload = {
            "model": agent.llm_model,
            "messages": messages,
            "stream": False
        }

        # Ollama doesn't have native function calling like OpenAI
        # We can include functions in the system prompt as a workaround
        if functions:
            print(f"[LLM SERVICE - OLLAMA] Adding {len(functions)} functions to system prompt")
            functions_description = "\n\nAvailable functions:\n"
            for func in functions:
                functions_description += f"\n- {func['name']}: {func['description']}"
            
            # Add to first system message or create one
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += functions_description
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": f"You are a helpful assistant.{functions_description}"
                })
        
        # Make request to Ollama
        print(f"[LLM SERVICE - OLLAMA] Sending request to Ollama...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    ollama_url,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()

                # Convert Ollama response to OpenAI format
                ollama_response = response.json()
                print(f"[LLM SERVICE - OLLAMA] Response received from Ollama")
                result = LLMService._convert_ollama_to_openai_format(ollama_response)
                print(f"[LLM SERVICE - OLLAMA] Converted to OpenAI format")
                return result
        except httpx.ConnectError:
            print(f"[LLM SERVICE - OLLAMA] ERROR: Could not connect to Ollama")
            raise ValueError(
                "Could not connect to Ollama. Make sure Ollama is running locally "
                "(install from https://ollama.com and run 'ollama serve')"
            )
    
    @staticmethod
    def _convert_anthropic_to_openai_format(anthropic_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Anthropic response to OpenAI format."""
        content = anthropic_response.get("content", [])
        
        # Extract text content
        text_content = ""
        tool_calls = []
        
        for block in content:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                # Convert tool use to function call
                tool_calls.append({
                    "id": block.get("id"),
                    "type": "function",
                    "function": {
                        "name": block.get("name"),
                        "arguments": str(block.get("input", {}))
                    }
                })
        
        # Build OpenAI-like response
        message = {
            "role": "assistant",
            "content": text_content if text_content else None
        }
        
        if tool_calls:
            message["function_call"] = tool_calls[0]["function"]  # OpenAI format
        
        return {
            "id": anthropic_response.get("id"),
            "object": "chat.completion",
            "created": 0,
            "model": anthropic_response.get("model"),
            "choices": [
                {
                    "index": 0,
                    "message": message,
                    "finish_reason": anthropic_response.get("stop_reason")
                }
            ],
            "usage": {
                "prompt_tokens": anthropic_response.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": anthropic_response.get("usage", {}).get("output_tokens", 0),
                "total_tokens": (
                    anthropic_response.get("usage", {}).get("input_tokens", 0) +
                    anthropic_response.get("usage", {}).get("output_tokens", 0)
                )
            }
        }
    
    @staticmethod
    def _convert_ollama_to_openai_format(ollama_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Ollama response to OpenAI format."""
        message = ollama_response.get("message", {})
        
        return {
            "id": "ollama-" + str(hash(str(ollama_response))),
            "object": "chat.completion",
            "created": 0,
            "model": ollama_response.get("model"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": message.get("role", "assistant"),
                        "content": message.get("content", "")
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # Ollama doesn't provide this
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }


# Singleton instance
llm_service = LLMService()