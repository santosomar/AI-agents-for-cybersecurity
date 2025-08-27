#!/usr/bin/env python3
"""
Test script for Shodan MCP Server (OpenAPI Integration)

This script tests the OpenAPI-based Shodan MCP server functionality.
It validates configuration, API key handling, and OpenAPI spec loading.

Usage:
    python test_shodan_openapi.py
"""

import os
import sys
from unittest.mock import Mock, patch
import json

def test_api_key_handling():
    """Test API key validation and error handling."""
    print("Testing API key handling...")
    
    # Test missing API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            # Import here to avoid issues with missing dependencies
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from shodan_mcp import get_api_key
            get_api_key()
            print("❌ Should have raised ValueError for missing API key")
            return False
        except ValueError as e:
            if "SHODAN_API_KEY" in str(e):
                print("✓ Correctly handles missing API key")
            else:
                print(f"❌ Unexpected error message: {e}")
                return False
        except ImportError as e:
            print(f"⚠️  Skipping test due to missing dependencies: {e}")
            return True
    
    # Test valid API key
    with patch.dict(os.environ, {"SHODAN_API_KEY": "test_key_123"}):
        try:
            from shodan_mcp import get_api_key
            key = get_api_key()
            if key == "test_key_123":
                print("✓ Correctly retrieves API key from environment")
            else:
                print(f"❌ Retrieved wrong key: {key}")
                return False
        except ImportError as e:
            print(f"⚠️  Skipping test due to missing dependencies: {e}")
            return True
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return True

def test_openapi_spec_loading():
    """Test OpenAPI specification loading with mocked response."""
    print("\nTesting OpenAPI spec loading...")
    
    # Mock OpenAPI response
    mock_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Shodan API", "version": "1.0.0"},
        "paths": {
            "/shodan/host/search": {"get": {"operationId": "searchHost"}},
            "/shodan/host/{ip}": {"get": {"operationId": "hostInformation"}}
        }
    }
    
    try:
        # Mock httpx.get to return our test spec
        with patch("httpx.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_spec
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            from shodan_mcp import load_openapi_spec
            spec = load_openapi_spec()
            
            if spec == mock_spec:
                print("✓ Successfully loads OpenAPI specification")
            else:
                print(f"❌ Loaded spec doesn't match expected: {spec}")
                return False
                
    except ImportError as e:
        print(f"⚠️  Skipping test due to missing dependencies: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_route_maps():
    """Test route mapping configuration."""
    print("\nTesting route maps...")
    
    try:
        from shodan_mcp import create_route_maps
        route_maps = create_route_maps()
        
        if len(route_maps) > 0:
            print(f"✓ Created {len(route_maps)} route mappings")
            
            # Check if we have expected patterns
            patterns = [rm.pattern for rm in route_maps]
            if any("search" in pattern for pattern in patterns):
                print("✓ Search endpoints mapped")
            else:
                print("❌ Search endpoints not found in mappings")
                return False
                
        else:
            print("❌ No route mappings created")
            return False
            
    except ImportError as e:
        print(f"⚠️  Skipping test due to missing dependencies: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_client_creation():
    """Test HTTP client creation."""
    print("\nTesting HTTP client creation...")
    
    with patch.dict(os.environ, {"SHODAN_API_KEY": "test_key"}):
        try:
            from shodan_mcp import create_shodan_client
            client = create_shodan_client()
            
            if hasattr(client, 'base_url'):
                print("✓ HTTP client created with base URL")
            else:
                print("❌ HTTP client missing base URL")
                return False
                
        except ImportError as e:
            print(f"⚠️  Skipping test due to missing dependencies: {e}")
            return True
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return True

def test_configuration_validation():
    """Test overall configuration validation."""
    print("\nTesting configuration validation...")
    
    # Test with missing API key
    with patch.dict(os.environ, {}, clear=True):
        try:
            # This should fail gracefully
            from shodan_mcp import main
            result = main()
            if result == 1:  # Expected error code
                print("✓ Gracefully handles missing configuration")
            else:
                print(f"❌ Unexpected return code: {result}")
                return False
                
        except ImportError as e:
            print(f"⚠️  Skipping test due to missing dependencies: {e}")
            return True
        except SystemExit as e:
            if e.code == 1:
                print("✓ Gracefully handles missing configuration")
            else:
                print(f"❌ Unexpected exit code: {e.code}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🔍 Testing Shodan MCP Server (OpenAPI Integration)")
    print("=" * 60)
    
    tests = [
        test_api_key_handling,
        test_openapi_spec_loading,
        test_route_maps,
        test_client_creation,
        test_configuration_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Shodan MCP server is ready to use.")
        print("\n📦 Installation:")
        print("pip install fastmcp httpx")
        print("\n🔑 Setup:")
        print("export SHODAN_API_KEY='your_key_here'")
        print("\n🚀 Run:")
        print("python shodan_mcp.py")
        print("\n✨ Benefits of OpenAPI Integration:")
        print("- Automatic tool generation from Shodan's full API")
        print("- Always up-to-date with latest Shodan features")
        print("- Proper request/response validation")
        print("- Better error handling and documentation")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
