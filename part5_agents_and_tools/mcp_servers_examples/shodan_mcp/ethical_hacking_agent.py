# Ethical Hacking Agent using Shodan MCP Server
#
# This script implements an ethical hacking agent that uses the Shodan MCP server
# to perform reconnaissance and security assessments. The agent demonstrates
# responsible security research practices and automated threat intelligence gathering.
#
# Instructor: Omar Santos @santosomar

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the path to the .env file and load it
# Make sure to create a .env file in this directory
# and add your OPENAI_API_KEY and SHODAN_API_KEY to it.
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

async def main():
    """Main function to run the ethical hacking agent."""
    print("🔍 Ethical Hacking Agent - Shodan MCP Integration")
    print("=" * 60)
    
    # Validate required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found. Please check your .env file.")
        return
    
    if not os.getenv("SHODAN_API_KEY"):
        print("❌ Error: SHODAN_API_KEY not found. Please check your .env file.")
        print("   Get a free API key at: https://account.shodan.io/register")
        return
    
    print("✅ API keys found. Initializing agent...")
    
    # The script_dir is already defined globally, so we can use it to build the server path
    server_path = os.path.join(script_dir, "shodan_mcp.py")
    
    # Initialize the MultiServerMCPClient to connect to the Shodan MCP server
    client = MultiServerMCPClient(
        {
            "shodan_tools": {
                "command": "python",
                "args": [server_path],
                "transport": "stdio",
            }
        }
    )
    
    print("🔌 Connecting to Shodan MCP server...")
    try:
        # Getting the tools from the MCP server
        tools = await client.get_tools()
        print(f"✅ Connected! Available tools: {len(tools)}")
        print(f"   Tool names: {[tool.name for tool in tools[:10]]}{'...' if len(tools) > 10 else ''}")
    except Exception as e:
        print(f"❌ Error connecting to Shodan MCP server: {e}")
        print("   Make sure the server is accessible and dependencies are installed.")
        return
    
    print("\n🤖 Initializing AI model...")
    try:
        # Initialize the AI model - using gpt-5 in this case. The lower the temperature, the more deterministic 
        # the model is.
        llm = ChatOpenAI(model="gpt-5", temperature=0.1)
        
        # Create a ReAct agent with the fetched tools
        agent = create_react_agent(llm, tools)
        print("✅ AI model and agent initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing AI model or agent: {e}")
        return
    
    # Define ethical hacking scenarios
    scenarios = [
        {
            "name": "Infrastructure Reconnaissance",
            "description": "Perform reconnaissance on a target domain",
            "task": """Perform ethical reconnaissance on the domain 'tesla.com'. 
                      Follow these steps:
                      1. Search for hosts associated with tesla.com
                      2. Get detailed information about 2-3 discovered hosts
                      3. Analyze the services and technologies found
                      4. Provide a security assessment summary
                      
                      Remember: This is for educational purposes only. Always ensure you have 
                      proper authorization before testing any systems."""
        },
        {
            "name": "Vulnerability Assessment",
            "description": "Search for potentially vulnerable services",
            "task": """Conduct a vulnerability assessment by searching for:
                      1. Exposed SSH services (port 22) in the US
                      2. Count how many results are found
                      3. Look for any specific vulnerable SSH versions
                      4. Provide recommendations for securing SSH services
                      
                      Focus on educational insights about common security issues."""
        },
        {
            "name": "IoT Security Analysis",
            "description": "Analyze IoT device security posture",
            "task": """Perform an IoT security analysis:
                      1. Search for common IoT devices (like IP cameras or routers)
                      2. Analyze the geographic distribution of these devices
                      3. Look for devices with default credentials or known vulnerabilities
                      4. Provide security recommendations for IoT deployments
                      
                      This analysis helps understand the IoT threat landscape."""
        },
        {
            "name": "DNS Intelligence Gathering",
            "description": "Gather DNS intelligence for security assessment",
            "task": """Perform DNS intelligence gathering:
                      1. Resolve DNS for multiple security-related domains (e.g., github.com, cloudflare.com)
                      2. Perform reverse DNS lookups on the resolved IPs
                      3. Search Shodan for services on these IPs
                      4. Analyze the infrastructure and security posture
                      
                      This demonstrates DNS-based reconnaissance techniques."""
        }
    ]
    
    print(f"\n🎯 Running {len(scenarios)} ethical hacking scenarios...")
    print("   Note: All activities are for educational and authorized testing purposes only.")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"📋 Scenario {i}: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print("="*60)
        
        try:
            # Run the agent with the scenario task
            response = await agent.ainvoke({
                "messages": [{
                    "role": "user", 
                    "content": scenario["task"]
                }]
            })
            
            # Extract and display the agent's response
            agent_response = response['messages'][-1].content
            print(f"\n🤖 Agent Response:\n{agent_response}")
            
        except Exception as e:
            print(f"❌ Error during scenario '{scenario['name']}': {e}")
            continue
        
        # Add a pause between scenarios for readability
        print(f"\n⏸️  Scenario {i} completed. Continuing to next scenario...")
        await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("🎉 All ethical hacking scenarios completed!")
    print("\n📚 Key Takeaways:")
    print("• Always obtain proper authorization before testing systems")
    print("• Use reconnaissance data responsibly and ethically")
    print("• Focus on improving security rather than exploiting vulnerabilities")
    print("• Follow responsible disclosure practices for any findings")
    print("• Respect rate limits and terms of service of all tools and services")
    
    print(f"\n🔗 Resources:")
    print("• Shodan Search Guide: https://help.shodan.io/the-basics/search-query-fundamentals")
    print("• Ethical Hacking Guidelines: https://www.ec-council.org/ethical-hacking/")
    print("• Responsible Disclosure: https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html")

async def run_custom_scenario():
    """
    Alternative function to run a custom scenario with user input.
    This demonstrates how to create interactive ethical hacking sessions.
    """
    print("🔧 Custom Ethical Hacking Scenario")
    print("-" * 40)
    
    # This would be expanded to accept user input in a real implementation
    custom_task = """
    Perform a comprehensive security assessment of a hypothetical organization:
    1. Search for their public-facing infrastructure
    2. Identify potential security risks
    3. Provide actionable security recommendations
    4. Create a summary report with findings
    
    Focus on constructive security insights that would help improve their security posture.
    """
    
    print(f"Custom task: {custom_task}")
    # The actual implementation would follow the same pattern as the main scenarios

if __name__ == "__main__":
    print("🚀 Starting Ethical Hacking Agent with Shodan MCP Server")
    print("⚖️  Remember: This tool is for authorized security testing and education only!")
    print("🔒 Always follow ethical guidelines and obtain proper permissions.")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Agent execution interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")
    
    print("\n👋 Ethical Hacking Agent session ended.")
