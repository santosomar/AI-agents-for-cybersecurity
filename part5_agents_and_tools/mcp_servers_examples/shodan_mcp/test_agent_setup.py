#!/usr/bin/env python3
"""
Test script for Ethical Hacking Agent Setup

This script validates that all dependencies and configurations are properly
set up for the ethical hacking agent to work with the Shodan MCP server.

Usage:
    python test_agent_setup.py
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test that required environment variables are set."""
    print("🔑 Testing environment variables...")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Found .env file")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Loaded .env file successfully")
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping .env loading")
    else:
        print("⚠️  No .env file found. You can create one from env_template.txt")
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "SHODAN_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Create a .env file with your API keys (see env_template.txt)")
        return False
    
    return True

def test_dependencies():
    """Test that required Python packages are installed."""
    print("\n📦 Testing Python dependencies...")
    
    required_packages = [
        ("fastmcp", "FastMCP"),
        ("httpx", "httpx"),
        ("langgraph", "LangGraph"),
        ("langchain_mcp_adapters", "LangChain MCP Adapters"),
        ("langchain_openai", "LangChain OpenAI"),
        ("dotenv", "python-dotenv")
    ]
    
    missing_packages = []
    
    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_file_structure():
    """Test that required files are present."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        ("shodan_mcp.py", "Shodan MCP Server"),
        ("ethical_hacking_agent.py", "Ethical Hacking Agent"),
        ("requirements.txt", "Requirements file"),
        ("README.md", "Documentation")
    ]
    
    missing_files = []
    
    for filename, description in required_files:
        if Path(filename).exists():
            print(f"✅ {description} ({filename})")
        else:
            print(f"❌ {description} ({filename}) - Not found")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_shodan_connectivity():
    """Test basic connectivity to Shodan API."""
    print("\n🌐 Testing Shodan API connectivity...")
    
    try:
        import httpx
        api_key = os.getenv("SHODAN_API_KEY")
        
        if not api_key:
            print("⚠️  Skipping connectivity test - no API key")
            return True
        
        # Test basic API info endpoint
        response = httpx.get(
            "https://api.shodan.io/api-info",
            params={"key": api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Shodan API connectivity successful")
            return True
        elif response.status_code == 401:
            print("❌ Invalid Shodan API key")
            return False
        else:
            print(f"⚠️  Shodan API returned status {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  httpx not available, skipping connectivity test")
        return True
    except Exception as e:
        print(f"⚠️  Connectivity test failed: {e}")
        return True  # Don't fail the overall test for connectivity issues

def main():
    """Run all setup tests."""
    print("🧪 Ethical Hacking Agent - Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Python Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("Shodan Connectivity", test_shodan_connectivity)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The ethical hacking agent is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run the agent: python ethical_hacking_agent.py")
        print("2. Or run the MCP server: python shodan_mcp.py")
        print("3. Check the README.md for detailed usage instructions")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 Quick fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment: cp env_template.txt .env (then edit .env)")
        print("3. Get API keys:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("   - Shodan: https://account.shodan.io/register")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
