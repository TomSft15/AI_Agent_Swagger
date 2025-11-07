"""
Agent Generator Service

This service generates AI agents from Swagger/OpenAPI documentation.
It creates system prompts and function definitions for LLM function calling.
"""
from typing import Dict, Any, List, Optional
from app.models.swagger_doc import SwaggerDoc
from app.models.endpoint import Endpoint
from app.models.endpoint_customization import EndpointCustomization


class AgentGeneratorService:
    """Service for generating AI agents from Swagger docs."""
    
    @staticmethod
    def generate_system_prompt(swagger_doc: SwaggerDoc, endpoints: List[Endpoint]) -> str:
        """
        Generate system prompt for the agent.
        
        Args:
            swagger_doc: Swagger documentation
            endpoints: List of endpoints
            
        Returns:
            System prompt string
        """
        api_info = f"{swagger_doc.name} (v{swagger_doc.version})" if swagger_doc.version else swagger_doc.name
        
        prompt = f"""You are an AI assistant that can interact with the {api_info} API.

API Information:
- Name: {swagger_doc.name}
- Description: {swagger_doc.description or 'No description available'}
- Base URL: {swagger_doc.base_url or 'Not specified'}
- OpenAPI Version: {swagger_doc.openapi_version}

Your capabilities:
You have access to {len(endpoints)} API endpoints that you can call to help users. When a user asks you to do something that requires API interaction, you should:

1. Understand the user's intent
2. Determine which API endpoint(s) to call
3. Extract the necessary parameters from the user's request
4. Call the appropriate function(s)
5. Provide a direct, concise response with the results

Important guidelines:
- Call the API functions directly without announcing what you're going to do
- Provide results immediately and concisely
- If you need more information from the user, ask for it
- Handle errors gracefully and explain what went wrong
- Never make up or hallucinate API responses - only use actual data from the API calls

Available endpoints:
"""
        
        # Add endpoint summaries
        for endpoint in endpoints:
            tags_str = f" [{', '.join(endpoint.tags)}]" if endpoint.tags else ""
            prompt += f"\n- {endpoint.method} {endpoint.path}{tags_str}: {endpoint.summary or 'No description'}"
        
        return prompt
    
    @staticmethod
    def generate_function_definitions(endpoints: List[Endpoint], customizations: Optional[Dict[str, EndpointCustomization]] = None) -> List[Dict[str, Any]]:
        """
        Generate OpenAI function calling definitions from endpoints.

        Args:
            endpoints: List of endpoints
            customizations: Optional dict mapping operation_id to EndpointCustomization

        Returns:
            List of function definitions
        """
        functions = []

        for endpoint in endpoints:
            function_name = AgentGeneratorService._create_function_name(endpoint)

            # Get custom description if available
            customization = customizations.get(endpoint.operation_id) if customizations else None
            description = AgentGeneratorService._create_function_description(endpoint, customization)

            # Build function definition
            function_def = {
                "name": function_name,
                "description": description,
                "parameters": AgentGeneratorService._create_function_parameters(endpoint)
            }

            # Add metadata for execution
            function_def["_metadata"] = {
                "endpoint_id": endpoint.id,
                "method": endpoint.method,
                "path": endpoint.path,
                "operation_id": endpoint.operation_id
            }

            functions.append(function_def)

        return functions
    
    @staticmethod
    def _create_function_name(endpoint: Endpoint) -> str:
        """
        Create a function name from endpoint.
        
        Args:
            endpoint: Endpoint
            
        Returns:
            Function name (snake_case)
        """
        # Use operation_id if available
        if endpoint.operation_id:
            return endpoint.operation_id
        
        # Otherwise create from method and path
        # GET /users/{id} -> get_users_by_id
        # POST /pets -> create_pet
        
        path_parts = endpoint.path.strip('/').split('/')
        clean_parts = []
        
        for part in path_parts:
            if part.startswith('{') and part.endswith('}'):
                clean_parts.append('by')
                clean_parts.append(part[1:-1])
            else:
                clean_parts.append(part)
        
        method_lower = endpoint.method.lower()
        name = f"{method_lower}_{'_'.join(clean_parts)}"
        
        # Clean up
        name = name.replace('-', '_').replace(' ', '_')
        
        return name
    
    @staticmethod
    def _create_function_description(endpoint: Endpoint, customization: Optional[EndpointCustomization] = None) -> str:
        """
        Create function description from endpoint, using custom description if available.

        Args:
            endpoint: Endpoint
            customization: Optional endpoint customization

        Returns:
            Function description
        """
        # Use custom description if available, otherwise use endpoint description
        if customization and customization.custom_description:
            description = customization.custom_description
        else:
            description = endpoint.summary or endpoint.description or f"{endpoint.method} {endpoint.path}"

        if endpoint.deprecated:
            description += " (DEPRECATED - use alternative if available)"

        return description
    
    @staticmethod
    def _create_function_parameters(endpoint: Endpoint) -> Dict[str, Any]:
        """
        Create function parameters schema from endpoint.
        
        Args:
            endpoint: Endpoint
            
        Returns:
            Parameters schema for function calling
        """
        properties = {}
        required = []
        
        # Add path parameters
        if endpoint.parameters and endpoint.parameters.get('path'):
            for param in endpoint.parameters['path']:
                param_name = param.get('name')
                if param_name:
                    properties[param_name] = {
                        "type": AgentGeneratorService._map_type(param.get('schema', {}).get('type') or param.get('type')),
                        "description": param.get('description', f"Path parameter: {param_name}")
                    }
                    if param.get('required', True):
                        required.append(param_name)
        
        # Add query parameters
        if endpoint.parameters and endpoint.parameters.get('query'):
            for param in endpoint.parameters['query']:
                param_name = param.get('name')
                if param_name:
                    properties[param_name] = {
                        "type": AgentGeneratorService._map_type(param.get('schema', {}).get('type') or param.get('type')),
                        "description": param.get('description', f"Query parameter: {param_name}")
                    }
                    if param.get('required', False):
                        required.append(param_name)
        
        # Add request body fields (simplified)
        if endpoint.request_body:
            content = endpoint.request_body.get('content', {})
            # Try to get JSON schema
            for content_type in ['application/json', 'application/xml']:
                if content_type in content:
                    schema = content[content_type].get('schema', {})
                    if schema.get('properties'):
                        for prop_name, prop_schema in schema['properties'].items():
                            properties[prop_name] = {
                                "type": AgentGeneratorService._map_type(prop_schema.get('type')),
                                "description": prop_schema.get('description', f"Body field: {prop_name}")
                            }
                    break
            
            if endpoint.request_body.get('required', False) and not required:
                # If body is required but we don't have specific fields, add a generic body param
                if 'body' not in properties:
                    properties['body'] = {
                        "type": "object",
                        "description": "Request body"
                    }
                    required.append('body')
        
        # If no parameters, add a placeholder
        if not properties:
            properties['_no_params'] = {
                "type": "string",
                "description": "This endpoint requires no parameters",
                "enum": ["none"]
            }
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    @staticmethod
    def _map_type(openapi_type: str) -> str:
        """
        Map OpenAPI types to JSON Schema types.
        
        Args:
            openapi_type: OpenAPI type
            
        Returns:
            JSON Schema type
        """
        type_mapping = {
            'integer': 'number',
            'int': 'number',
            'long': 'number',
            'float': 'number',
            'double': 'number',
            'string': 'string',
            'boolean': 'boolean',
            'bool': 'boolean',
            'array': 'array',
            'object': 'object'
        }
        
        return type_mapping.get(openapi_type, 'string')


# Singleton instance
agent_generator = AgentGeneratorService()