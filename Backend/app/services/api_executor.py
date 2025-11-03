"""
API Executor Service

This service executes real HTTP calls to external APIs based on function calls
from the LLM. It interprets the agent's function metadata and makes the actual
requests to the endpoints defined in the Swagger documentation.
"""
from typing import Dict, Any, Optional
import httpx
import json
from urllib.parse import urljoin
from app.models.agent import Agent
from app.models.endpoint import Endpoint
from app.models.swagger_doc import SwaggerDoc
from sqlalchemy.orm import Session


class APIExecutorService:
    """Service for executing API calls based on agent function calls."""
    
    @staticmethod
    async def execute_function_call(
        db: Session,
        agent: Agent,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a function call by making the actual HTTP request.
        
        Args:
            db: Database session
            agent: Agent instance
            function_name: Name of the function to call
            arguments: Function arguments (parameters)
            
        Returns:
            API response as dictionary
            
        Raises:
            ValueError: If function not found or execution fails
        """
        print(f"\n[API EXECUTOR] === Executing function call ===")
        print(f"[API EXECUTOR] Function name: {function_name}")
        print(f"[API EXECUTOR] Arguments: {arguments}")

        # Find the function in agent's available functions
        function_def = None
        for func in agent.available_functions:
            if func["name"] == function_name:
                function_def = func
                break

        if not function_def:
            print(f"[API EXECUTOR] ERROR: Function '{function_name}' not found")
            raise ValueError(f"Function '{function_name}' not found in agent's available functions")

        print(f"[API EXECUTOR] Function found in agent's available functions")
        
        # Get metadata
        metadata = function_def.get("_metadata", {})
        endpoint_id = metadata.get("endpoint_id")

        if not endpoint_id:
            print(f"[API EXECUTOR] ERROR: No endpoint metadata found")
            raise ValueError(f"No endpoint metadata found for function '{function_name}'")

        print(f"[API EXECUTOR] Endpoint ID from metadata: {endpoint_id}")

        # Get endpoint from database
        endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
        if not endpoint:
            print(f"[API EXECUTOR] ERROR: Endpoint {endpoint_id} not found in database")
            raise ValueError(f"Endpoint {endpoint_id} not found")

        print(f"[API EXECUTOR] Endpoint found: {endpoint.method} {endpoint.path}")

        # Get swagger doc for base URL
        swagger_doc = db.query(SwaggerDoc).filter(
            SwaggerDoc.id == endpoint.swagger_doc_id
        ).first()

        if not swagger_doc:
            print(f"[API EXECUTOR] ERROR: Swagger doc {endpoint.swagger_doc_id} not found")
            raise ValueError(f"Swagger doc {endpoint.swagger_doc_id} not found")

        print(f"[API EXECUTOR] Swagger doc found: {swagger_doc.name} (base URL: {swagger_doc.base_url})")
        print(f"[API EXECUTOR] Preparing HTTP request...")

        # Execute the HTTP request
        return await APIExecutorService._execute_http_request(
            endpoint=endpoint,
            swagger_doc=swagger_doc,
            arguments=arguments
        )
    
    @staticmethod
    async def _execute_http_request(
        endpoint: Endpoint,
        swagger_doc: SwaggerDoc,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the actual HTTP request.
        
        Args:
            endpoint: Endpoint instance
            swagger_doc: Swagger doc instance
            arguments: Function arguments
            
        Returns:
            API response
        """
        print(f"\n[HTTP REQUEST] Building HTTP request...")
        print(f"[HTTP REQUEST] Method: {endpoint.method}")
        print(f"[HTTP REQUEST] Path template: {endpoint.path}")

        # Build URL
        base_url = swagger_doc.base_url or ""
        path = endpoint.path

        # Replace path parameters
        path_params = {}
        if endpoint.parameters and endpoint.parameters.get("path"):
            print(f"[HTTP REQUEST] Processing {len(endpoint.parameters['path'])} path parameters")
            for param in endpoint.parameters["path"]:
                param_name = param.get("name")
                if param_name and param_name in arguments:
                    old_path = path
                    path = path.replace(f"{{{param_name}}}", str(arguments[param_name]))
                    path_params[param_name] = arguments[param_name]
                    print(f"[HTTP REQUEST] Replaced path param '{param_name}': {old_path} -> {path}")
        
        # Build full URL
        if base_url:
            url = urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))
        else:
            url = path

        print(f"[HTTP REQUEST] Full URL: {url}")

        # Prepare query parameters
        query_params = {}
        if endpoint.parameters and endpoint.parameters.get("query"):
            print(f"[HTTP REQUEST] Processing {len(endpoint.parameters['query'])} query parameters")
            for param in endpoint.parameters["query"]:
                param_name = param.get("name")
                if param_name and param_name in arguments:
                    query_params[param_name] = arguments[param_name]
            if query_params:
                print(f"[HTTP REQUEST] Query params: {query_params}")
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Agent-Platform/1.0"
        }
        
        # Add header parameters
        if endpoint.parameters and endpoint.parameters.get("header"):
            for param in endpoint.parameters["header"]:
                param_name = param.get("name")
                if param_name and param_name in arguments:
                    headers[param_name] = str(arguments[param_name])
        
        # Prepare request body
        body = None
        if endpoint.request_body and endpoint.method.upper() in ["POST", "PUT", "PATCH"]:
            # Get body from arguments
            # If there's a 'body' argument, use it
            if "body" in arguments:
                body = arguments["body"]
            else:
                # Otherwise, collect non-path/query params as body
                body = {}
                used_params = set(path_params.keys()) | set(query_params.keys())
                for key, value in arguments.items():
                    if key not in used_params and not key.startswith("_"):
                        body[key] = value
            if body:
                print(f"[HTTP REQUEST] Request body: {body}")

        # Make the HTTP request
        method = endpoint.method.upper()
        print(f"\n[HTTP REQUEST] Executing {method} request to {url}...")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                if method == "GET":
                    response = await client.get(url, params=query_params, headers=headers)
                elif method == "POST":
                    response = await client.post(url, params=query_params, json=body, headers=headers)
                elif method == "PUT":
                    response = await client.put(url, params=query_params, json=body, headers=headers)
                elif method == "PATCH":
                    response = await client.patch(url, params=query_params, json=body, headers=headers)
                elif method == "DELETE":
                    response = await client.delete(url, params=query_params, headers=headers)
                elif method == "HEAD":
                    response = await client.head(url, params=query_params, headers=headers)
                elif method == "OPTIONS":
                    response = await client.options(url, params=query_params, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                print(f"[HTTP REQUEST] Response received: HTTP {response.status_code}")

                # Parse response
                result = {
                    "success": True,
                    "status_code": response.status_code,
                    "url": str(response.url),
                    "method": method
                }

                # Try to parse JSON response
                try:
                    result["data"] = response.json()
                    print(f"[HTTP REQUEST] Response is JSON (size: {len(str(result['data']))} chars)")
                except Exception:
                    # If not JSON, return text
                    result["data"] = response.text
                    print(f"[HTTP REQUEST] Response is text (size: {len(response.text)} chars)")

                # Check if request was successful
                if response.status_code >= 400:
                    result["success"] = False
                    result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                    print(f"[HTTP REQUEST] Request FAILED: {result['error']}")
                else:
                    print(f"[HTTP REQUEST] Request SUCCESSFUL")

                return result
                
        except httpx.TimeoutException:
            print(f"[HTTP REQUEST] ERROR: Request timeout")
            return {
                "success": False,
                "error": "Request timeout - the API took too long to respond",
                "status_code": 408,
                "url": url,
                "method": method
            }
        except httpx.ConnectError:
            print(f"[HTTP REQUEST] ERROR: Connection failed to {url}")
            return {
                "success": False,
                "error": f"Could not connect to {url}",
                "status_code": 0,
                "url": url,
                "method": method
            }
        except Exception as e:
            print(f"[HTTP REQUEST] ERROR: {str(e)}")
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "status_code": 0,
                "url": url,
                "method": method
            }
    
    @staticmethod
    def format_result_for_llm(result: Dict[str, Any]) -> str:
        """
        Format API result for LLM consumption.
        
        Args:
            result: API execution result
            
        Returns:
            Formatted string for LLM
        """
        if result.get("success"):
            data = result.get("data", {})
            if isinstance(data, dict) or isinstance(data, list):
                return json.dumps(data, indent=2, ensure_ascii=False)
            return str(data)
        else:
            error = result.get("error", "Unknown error")
            status = result.get("status_code", 0)
            return f"Error {status}: {error}"


# Singleton instance
api_executor = APIExecutorService()