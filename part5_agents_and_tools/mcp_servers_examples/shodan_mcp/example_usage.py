#!/usr/bin/env python3
"""
Example Usage: Shodan MCP Server

This script demonstrates how to use the Shodan MCP server in various scenarios.
It shows integration patterns for AI agents, LangGraph workflows, and direct usage.

Prerequisites:
- pip install fastmcp httpx
- export SHODAN_API_KEY='your_key_here'

Usage:
    python example_usage.py
"""

import asyncio
import os
from typing import Dict, Any, List

# Example 1: Direct MCP Client Usage
async def example_direct_mcp_usage():
    """
    Example of using the Shodan MCP server directly with an MCP client.
    """
    print("📡 Example 1: Direct MCP Client Usage")
    print("-" * 50)
    
    try:
        # This would be the actual MCP client connection
        # from mcp.client import Client
        # client = Client("stdio", "python shodan_mcp.py")
        
        # Simulated client calls (replace with actual MCP client)
        print("🔍 Searching for SSH servers...")
        # search_result = await client.call_tool("shodan_host_search", {
        #     "query": "port:22",
        #     "facets": "country,org"
        # })
        
        print("✅ Found SSH servers with country and organization breakdown")
        
        print("\n🏠 Getting host information...")
        # host_info = await client.call_tool("shodan_host_info", {
        #     "ip": "8.8.8.8"
        # })
        
        print("✅ Retrieved detailed information for Google DNS server")
        
        print("\n🌐 Resolving domains...")
        # dns_result = await client.call_tool("shodan_dns_resolve", {
        #     "hostnames": "google.com,github.com"
        # })
        
        print("✅ Resolved multiple domains to IP addresses")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Example 2: LangGraph Integration
async def example_langgraph_integration():
    """
    Example of integrating Shodan MCP server with LangGraph for automated workflows.
    """
    print("\n🤖 Example 2: LangGraph Integration")
    print("-" * 50)
    
    # Simulated LangGraph workflow
    class ShodanReconAgent:
        def __init__(self):
            # self.mcp_client = Client("stdio", "python shodan_mcp.py")
            pass
        
        async def reconnaissance_workflow(self, target_domain: str) -> Dict[str, Any]:
            """
            Automated reconnaissance workflow using Shodan MCP server.
            """
            results = {
                "target": target_domain,
                "dns_info": {},
                "host_info": [],
                "search_results": {},
                "summary": {}
            }
            
            print(f"🎯 Starting reconnaissance for: {target_domain}")
            
            # Step 1: DNS Resolution
            print("  📍 Step 1: Resolving domain...")
            # dns_info = await self.mcp_client.call_tool("shodan_dns_resolve", {
            #     "hostnames": target_domain
            # })
            # results["dns_info"] = dns_info
            print(f"    ✅ Resolved {target_domain}")
            
            # Step 2: Search for domain in Shodan
            print("  🔍 Step 2: Searching Shodan database...")
            # search_results = await self.mcp_client.call_tool("shodan_host_search", {
            #     "query": f"hostname:{target_domain}",
            #     "facets": "port,product,country"
            # })
            # results["search_results"] = search_results
            print(f"    ✅ Found services for {target_domain}")
            
            # Step 3: Get detailed host information
            print("  🏠 Step 3: Getting detailed host information...")
            # for match in search_results.get("matches", [])[:5]:  # Limit to 5 hosts
            #     host_info = await self.mcp_client.call_tool("shodan_host_info", {
            #         "ip": match["ip_str"]
            #     })
            #     results["host_info"].append(host_info)
            print("    ✅ Retrieved detailed host information")
            
            # Step 4: Generate summary
            print("  📊 Step 4: Generating summary...")
            results["summary"] = {
                "total_hosts": 5,  # len(results["host_info"])
                "unique_ports": [22, 80, 443],  # Extract from results
                "countries": ["US", "DE"],  # Extract from facets
                "technologies": ["nginx", "apache"]  # Extract from products
            }
            print("    ✅ Generated reconnaissance summary")
            
            return results
    
    # Run the workflow
    agent = ShodanReconAgent()
    results = await agent.reconnaissance_workflow("example.com")
    
    print(f"\n📋 Reconnaissance Summary:")
    print(f"   Target: {results['target']}")
    print(f"   Hosts Found: {results['summary']['total_hosts']}")
    print(f"   Open Ports: {', '.join(map(str, results['summary']['unique_ports']))}")
    print(f"   Countries: {', '.join(results['summary']['countries'])}")
    print(f"   Technologies: {', '.join(results['summary']['technologies'])}")

# Example 3: Threat Intelligence Gathering
async def example_threat_intelligence():
    """
    Example of using Shodan MCP server for threat intelligence gathering.
    """
    print("\n🛡️  Example 3: Threat Intelligence Gathering")
    print("-" * 50)
    
    # Common threat intelligence queries
    threat_queries = [
        {
            "name": "Exposed Databases",
            "query": "product:MongoDB -authentication",
            "description": "Find MongoDB instances without authentication"
        },
        {
            "name": "Vulnerable SSH",
            "query": "product:OpenSSH version:7.4",
            "description": "Find potentially vulnerable SSH servers"
        },
        {
            "name": "Exposed RDP",
            "query": "port:3389 country:US",
            "description": "Find exposed RDP services in the US"
        },
        {
            "name": "IoT Devices",
            "query": "product:\"Hikvision IP Camera\"",
            "description": "Find Hikvision IP cameras"
        }
    ]
    
    print("🔍 Running threat intelligence queries...")
    
    for i, query_info in enumerate(threat_queries, 1):
        print(f"\n  📊 Query {i}: {query_info['name']}")
        print(f"      Description: {query_info['description']}")
        print(f"      Query: {query_info['query']}")
        
        # Simulate MCP call
        # count_result = await client.call_tool("shodan_search_count", {
        #     "query": query_info["query"],
        #     "facets": "country,org"
        # })
        
        # Simulated results
        print(f"      ✅ Found ~10,000 results")
        print(f"      Top Countries: US (3,000), CN (2,500), DE (1,200)")
        print(f"      Top Organizations: Amazon (500), Google (300), Microsoft (200)")

# Example 4: Infrastructure Mapping
async def example_infrastructure_mapping():
    """
    Example of mapping an organization's infrastructure using Shodan.
    """
    print("\n🗺️  Example 4: Infrastructure Mapping")
    print("-" * 50)
    
    target_org = "Example Corp"
    
    print(f"🏢 Mapping infrastructure for: {target_org}")
    
    # Step 1: Find all assets belonging to the organization
    print("\n  🔍 Step 1: Finding organizational assets...")
    # org_search = await client.call_tool("shodan_host_search", {
    #     "query": f'org:"{target_org}"',
    #     "facets": "port,product,country,asn"
    # })
    
    print(f"    ✅ Found 150 assets for {target_org}")
    
    # Step 2: Analyze service distribution
    print("\n  📊 Step 2: Analyzing service distribution...")
    services = {
        "Web Services": {"ports": [80, 443], "count": 45},
        "Email Services": {"ports": [25, 587, 993], "count": 12},
        "SSH Access": {"ports": [22], "count": 78},
        "Database Services": {"ports": [3306, 5432, 1433], "count": 8},
        "Remote Access": {"ports": [3389, 5900], "count": 7}
    }
    
    for service, info in services.items():
        print(f"    • {service}: {info['count']} instances on ports {info['ports']}")
    
    # Step 3: Geographic distribution
    print("\n  🌍 Step 3: Geographic distribution...")
    locations = {
        "United States": 89,
        "Germany": 23,
        "Singapore": 18,
        "United Kingdom": 12,
        "Canada": 8
    }
    
    for country, count in locations.items():
        print(f"    • {country}: {count} assets")
    
    # Step 4: Technology stack analysis
    print("\n  💻 Step 4: Technology stack analysis...")
    technologies = {
        "nginx": 34,
        "Apache": 28,
        "Microsoft IIS": 15,
        "OpenSSH": 78,
        "MySQL": 12,
        "PostgreSQL": 8
    }
    
    for tech, count in technologies.items():
        print(f"    • {tech}: {count} instances")

# Example 5: Security Monitoring
async def example_security_monitoring():
    """
    Example of using Shodan for continuous security monitoring.
    """
    print("\n🔒 Example 5: Security Monitoring")
    print("-" * 50)
    
    print("🚨 Setting up security monitoring alerts...")
    
    # Monitoring scenarios
    monitoring_rules = [
        {
            "name": "New Exposed Services",
            "query": "org:\"Your Company\" port:22,80,443",
            "alert_type": "new_services",
            "description": "Alert when new services are exposed"
        },
        {
            "name": "Vulnerable Software",
            "query": "org:\"Your Company\" product:OpenSSH version:7.4",
            "alert_type": "vulnerabilities",
            "description": "Alert for known vulnerable software versions"
        },
        {
            "name": "Unauthorized Changes",
            "query": "net:203.0.113.0/24",
            "alert_type": "network_changes",
            "description": "Monitor specific network ranges for changes"
        }
    ]
    
    for rule in monitoring_rules:
        print(f"\n  📋 Rule: {rule['name']}")
        print(f"      Query: {rule['query']}")
        print(f"      Type: {rule['alert_type']}")
        print(f"      Description: {rule['description']}")
        
        # Simulate alert setup
        # alert_result = await client.call_tool("shodan_create_alert", {
        #     "name": rule["name"],
        #     "filters": {"query": rule["query"]},
        #     "expires": 0  # Never expires
        # })
        
        print(f"      ✅ Alert configured successfully")

async def main():
    """
    Run all examples to demonstrate Shodan MCP server capabilities.
    """
    print("🔍 Shodan MCP Server - Usage Examples")
    print("=" * 60)
    print("Note: These examples show simulated usage patterns.")
    print("Install dependencies and set SHODAN_API_KEY to run with real data.")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv("SHODAN_API_KEY")
    if api_key:
        print(f"🔑 API Key found: {api_key[:8]}...")
    else:
        print("⚠️  No API key found. Set SHODAN_API_KEY environment variable.")
    
    # Run examples
    await example_direct_mcp_usage()
    await example_langgraph_integration()
    await example_threat_intelligence()
    await example_infrastructure_mapping()
    await example_security_monitoring()
    
    print("\n" + "=" * 60)
    print("🎉 Examples completed!")
    print("\n📚 Next Steps:")
    print("1. Install dependencies: pip install fastmcp httpx")
    print("2. Get Shodan API key: https://account.shodan.io/register")
    print("3. Set environment: export SHODAN_API_KEY='your_key'")
    print("4. Run MCP server: python shodan_mcp.py")
    print("5. Connect your AI agent to the MCP server")
    print("\n🔗 Resources:")
    print("- Shodan API Docs: https://developer.shodan.io/api")
    print("- FastMCP Docs: https://gofastmcp.com")
    print("- MCP Protocol: https://modelcontextprotocol.io")

if __name__ == "__main__":
    asyncio.run(main())
