"""
Swagger/OpenAPI Parser Service

This service handles parsing, validation, and extraction of endpoints
from Swagger/OpenAPI documentation files.
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import yaml
from prance import ResolvingParser
from openapi_spec_validator import validate_spec
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError


class SwaggerParserService:
    """Service for parsing and validating Swagger/OpenAPI documents."""
    
    @staticmethod
    def parse_content(content: str, file_format: str = "json") -> Dict[str, Any]:
        """
        Parse Swagger content from string.
        
        Args:
            content: String content of the Swagger file
            file_format: Format of the file ('json' or 'yaml')
            
        Returns:
            Parsed specification as dictionary
            
        Raises:
            ValueError: If parsing fails
        """
        try:
            if file_format.lower() == "json":
                return json.loads(content)
            elif file_format.lower() in ["yaml", "yml"]:
                return yaml.safe_load(content)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {str(e)}")
    
    @staticmethod
    def validate_openapi_spec(spec: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate OpenAPI specification.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validate_spec(spec)
            return True, None
        except OpenAPIValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def get_openapi_version(spec: Dict[str, Any]) -> Optional[str]:
        """
        Extract OpenAPI/Swagger version from spec.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Version string (e.g., "3.0.0", "2.0") or None
        """
        # OpenAPI 3.x
        if "openapi" in spec:
            return spec["openapi"]
        # Swagger 2.0
        elif "swagger" in spec:
            return spec["swagger"]
        return None
    
    @staticmethod
    def get_base_url(spec: Dict[str, Any]) -> Optional[str]:
        """
        Extract base URL from specification.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Base URL string or None
        """
        # OpenAPI 3.x
        if "servers" in spec and isinstance(spec["servers"], list) and len(spec["servers"]) > 0:
            return spec["servers"][0].get("url")
        
        # Swagger 2.0
        if "host" in spec:
            scheme = spec.get("schemes", ["https"])[0] if "schemes" in spec else "https"
            base_path = spec.get("basePath", "")
            return f"{scheme}://{spec['host']}{base_path}"
        
        return None
    
    @staticmethod
    def get_api_info(spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract API information (title, description, version).
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Dictionary with API info
        """
        info = spec.get("info", {})
        return {
            "title": info.get("title", "Untitled API"),
            "description": info.get("description", ""),
            "version": info.get("version", "1.0.0")
        }
    
    @staticmethod
    def extract_endpoints(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all endpoints from the specification.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            # Skip if not a dict (could be $ref)
            if not isinstance(path_item, dict):
                continue
            
            # Extract endpoints for each HTTP method
            for method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                if method in path_item:
                    operation = path_item[method]
                    endpoint = SwaggerParserService._parse_operation(
                        path=path,
                        method=method.upper(),
                        operation=operation,
                        spec=spec
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    @staticmethod
    def _parse_operation(
        path: str,
        method: str,
        operation: Dict[str, Any],
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse a single operation/endpoint.
        
        Args:
            path: Endpoint path
            method: HTTP method
            operation: Operation object from spec
            spec: Full specification (for resolving references)
            
        Returns:
            Parsed endpoint dictionary
        """
        return {
            "method": method,
            "path": path,
            "summary": operation.get("summary", ""),
            "description": operation.get("description", ""),
            "operation_id": operation.get("operationId"),
            "tags": operation.get("tags", []),
            "parameters": SwaggerParserService._parse_parameters(operation.get("parameters", [])),
            "request_body": SwaggerParserService._parse_request_body(operation.get("requestBody")),
            "responses": SwaggerParserService._parse_responses(operation.get("responses", {})),
            "security": operation.get("security", []),
            "deprecated": operation.get("deprecated", False)
        }
    
    @staticmethod
    def _parse_parameters(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse parameters (query, path, header, cookie).
        
        Args:
            parameters: List of parameter objects
            
        Returns:
            Organized parameters dictionary
        """
        organized = {
            "query": [],
            "path": [],
            "header": [],
            "cookie": []
        }
        
        for param in parameters:
            if not isinstance(param, dict):
                continue
            
            param_in = param.get("in", "query")
            param_data = {
                "name": param.get("name"),
                "description": param.get("description", ""),
                "required": param.get("required", False),
                "schema": param.get("schema", {}),
                "type": param.get("type"),  # Swagger 2.0
                "format": param.get("format")  # Swagger 2.0
            }
            
            if param_in in organized:
                organized[param_in].append(param_data)
        
        return organized
    
    @staticmethod
    def _parse_request_body(request_body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parse request body (OpenAPI 3.x).
        
        Args:
            request_body: Request body object
            
        Returns:
            Parsed request body or None
        """
        if not request_body:
            return None
        
        return {
            "description": request_body.get("description", ""),
            "required": request_body.get("required", False),
            "content": request_body.get("content", {})
        }
    
    @staticmethod
    def _parse_responses(responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response definitions.
        
        Args:
            responses: Responses object
            
        Returns:
            Parsed responses dictionary
        """
        parsed_responses = {}
        
        for status_code, response in responses.items():
            if not isinstance(response, dict):
                continue
            
            parsed_responses[status_code] = {
                "description": response.get("description", ""),
                "content": response.get("content", {}),
                "schema": response.get("schema", {})  # Swagger 2.0
            }
        
        return parsed_responses
    
    @staticmethod
    def parse_with_refs_resolution(spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse spec and resolve all $ref references.
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Specification with resolved references
            
        Note:
            This uses Prance to resolve all $ref pointers
        """
        try:
            # Create a temporary file-like object for Prance
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(spec, f)
                temp_path = f.name
            
            try:
                parser = ResolvingParser(temp_path)
                resolved_spec = parser.specification
                return resolved_spec
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            # If resolution fails, return original spec
            print(f"Warning: Could not resolve references: {str(e)}")
            return spec


# Singleton instance
swagger_parser = SwaggerParserService()