# Shodan MCP Server - OpenAPI Integration
#
# This script implements an MCP (Model Context Protocol) server for Shodan using FastMCP's
# OpenAPI integration. It automatically generates tools from Shodan's OpenAPI specification,
# providing a complete interface to Shodan's REST API for cybersecurity reconnaissance.
#
# Instructor: Omar Santos @santosomar

import os
import httpx
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from typing import Optional

def get_api_key() -> str:
    """
    Get Shodan API key from environment variable.
    
    Returns:
        str: The Shodan API key
        
    Raises:
        ValueError: If API key is not found in environment
    """
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        raise ValueError(
            "SHODAN_API_KEY environment variable not set. "
            "Please set your Shodan API key: export SHODAN_API_KEY='your_key_here'"
        )
    return api_key

def create_shodan_client() -> httpx.AsyncClient:
    """
    Create an HTTP client configured for Shodan API with authentication.
    
    Returns:
        httpx.AsyncClient: Configured HTTP client
    """
    api_key = get_api_key()
    
    # Create client with base URL and timeout settings
    client = httpx.AsyncClient(
        base_url="https://api.shodan.io",
        timeout=30.0,
        headers={
            "User-Agent": "Shodan-MCP-Server/1.0"
        }
    )
    
    return client

def load_openapi_spec() -> dict:
    """
    Load Shodan's OpenAPI specification from their API.
    
    Returns:
        dict: The OpenAPI specification
    """
    try:
        print("📥 Loading Shodan OpenAPI specification...")
        response = httpx.get("https://developer.shodan.io/api/openapi.json", timeout=10)
        response.raise_for_status()
        spec = response.json()
        print(f"✅ Loaded OpenAPI spec with {len(spec.get('paths', {}))} endpoints")
        return spec
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to load OpenAPI specification: {e}")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error loading OpenAPI spec: {e.response.status_code}")

def create_route_maps() -> list[RouteMap]:
    """
    Create custom route mappings for better MCP integration.
    
    Returns:
        list[RouteMap]: List of route mapping configurations
    """
    return [
        # Map GET requests with path parameters (like /shodan/host/{ip}) to ResourceTemplate
        RouteMap(
            methods=["GET"], 
            pattern=r".*\{.*\}.*", 
            mcp_type=MCPType.RESOURCE_TEMPLATE
        ),
        # Map search endpoints to Tools for better discoverability
        RouteMap(
            methods=["GET"], 
            pattern=r".*/search.*", 
            mcp_type=MCPType.TOOL
        ),
        # Map count endpoints to Tools
        RouteMap(
            methods=["GET"], 
            pattern=r".*/count.*", 
            mcp_type=MCPType.TOOL
        ),
        # Map DNS endpoints to Tools
        RouteMap(
            methods=["GET"], 
            pattern=r".*/dns/.*", 
            mcp_type=MCPType.TOOL
        ),
        # Map scan endpoints to Tools
        RouteMap(
            methods=["POST", "GET"], 
            pattern=r".*/scan.*", 
            mcp_type=MCPType.TOOL
        ),
        # Map account and API info to Resources
        RouteMap(
            methods=["GET"], 
            pattern=r".*/account/.*|.*/api-info.*", 
            mcp_type=MCPType.RESOURCE
        ),
        # Default: map all other GET requests to Resources
        RouteMap(
            methods=["GET"], 
            pattern=r".*", 
            mcp_type=MCPType.RESOURCE
        ),
    ]

def create_mcp_server() -> FastMCP:
    """
    Create and configure the Shodan MCP server using OpenAPI integration.
    
    Returns:
        FastMCP: Configured MCP server
    """
    # Load OpenAPI specification
    openapi_spec = load_openapi_spec()
    
    # Create HTTP client
    client = create_shodan_client()
    
    # Create route mappings for better organization
    route_maps = create_route_maps()
    
    # Create MCP server from OpenAPI spec
    print("🔧 Creating MCP server from OpenAPI specification...")
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name="ShodanMCPServer",
        description="Shodan cybersecurity search engine MCP server with full API access",
        route_maps=route_maps
    )
    
    # Add custom authentication middleware
    @mcp.middleware("request")
    async def add_api_key(request, call_next):
        """Add Shodan API key to all requests."""
        api_key = get_api_key()
        
        # Add API key as query parameter (Shodan's preferred method)
        if hasattr(request, 'url'):
            # For httpx requests, add to params
            if not hasattr(request, 'params'):
                request.params = {}
            request.params['key'] = api_key
        
        return await call_next(request)
    
    print("✅ MCP server created successfully")
    return mcp

def main():
    """
    Main function to create and run the Shodan MCP server.
    """
    try:
        print("🚀 Starting Shodan MCP Server")
        print("=" * 50)
        
        # Validate API key first
        api_key = get_api_key()
        print(f"🔑 API Key found: {api_key[:8]}...")
        
        # Create MCP server
        mcp = create_mcp_server()
        
        print("\n📋 Server Information:")
        print("- Name: Shodan MCP Server")
        print("- Base URL: https://api.shodan.io")
        print("- Transport: stdio")
        print("- Authentication: API Key (from SHODAN_API_KEY env var)")
        
        print("\n🛠️  Available Tools (auto-generated from OpenAPI):")
        print("- Host search and information retrieval")
        print("- DNS resolution and reverse lookup")
        print("- Account and API information")
        print("- Internet scanning capabilities")
        print("- Search facets and filters")
        print("- And many more based on Shodan's full API")
        
        print("\n📚 Usage:")
        print("Set your API key: export SHODAN_API_KEY='your_key_here'")
        print("Get a free API key at: https://account.shodan.io/register")
        
        print("\n🔄 Starting server...")
        
        # Run the MCP server
        mcp.run(transport="stdio")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Quick Setup:")
        print("1. Get a Shodan API key: https://account.shodan.io/register")
        print("2. Set environment variable: export SHODAN_API_KEY='your_key_here'")
        print("3. Run the server: python shodan_mcp.py")
        return 1
        
    except RuntimeError as e:
        print(f"❌ Runtime Error: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())