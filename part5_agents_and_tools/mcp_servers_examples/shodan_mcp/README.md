# Shodan MCP Server (OpenAPI Integration)

A Model Context Protocol (MCP) server that provides seamless access to Shodan's cybersecurity search engine using FastMCP's OpenAPI integration. This server automatically generates all tools and resources from Shodan's official OpenAPI specification, ensuring complete API coverage and automatic updates.

## 🚀 Key Features

### Automatic API Integration
- **Full API Coverage**: Automatically generates tools from Shodan's complete OpenAPI specification
- **Always Current**: Stays up-to-date with Shodan's latest features and endpoints
- **Zero Maintenance**: No manual tool definitions required

### Intelligent Route Mapping
- **Search Tools**: Search endpoints mapped as MCP Tools for easy discovery
- **Host Resources**: Host information endpoints as ResourceTemplates
- **DNS Services**: DNS resolution and reverse lookup tools
- **Account Management**: Profile and API information as Resources

### Enterprise-Ready
- **Async Performance**: Built on httpx for high-performance async operations
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Authentication**: Secure API key management via environment variables
- **Logging**: Structured logging for monitoring and debugging

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- FastMCP with OpenAPI support
- Shodan API key (free at https://account.shodan.io/register)

### Quick Setup

1. **Install Dependencies**:
   ```bash
   pip install fastmcp httpx
   # OR install from requirements
   pip install -r requirements.txt
   ```

2. **Get Shodan API Key**:
   - Register at https://account.shodan.io/register
   - Find your API key in the account dashboard

3. **Configure Environment**:
   ```bash
   export SHODAN_API_KEY="your_api_key_here"
   ```

4. **Run the Server**:
   ```bash
   python shodan_mcp.py
   ```

## 🤖 Ethical Hacking Agent

The `ethical_hacking_agent.py` demonstrates how to use the Shodan MCP server with an AI agent for automated security assessments and reconnaissance.

### Agent Setup

1. **Install Agent Dependencies**:
   ```bash
   pip install -r requirements.txt  # Includes agent dependencies
   ```

2. **Configure Environment**:
   ```bash
   # Copy the template and edit with your API keys
   cp env_template.txt .env
   # Edit .env with your OPENAI_API_KEY and SHODAN_API_KEY
   ```

3. **Test Setup**:
   ```bash
   python test_agent_setup.py
   ```

4. **Run the Agent**:
   ```bash
   python ethical_hacking_agent.py
   ```

### Agent Capabilities

The ethical hacking agent performs four main scenarios:

1. **Infrastructure Reconnaissance**: Domain-based asset discovery and analysis
2. **Vulnerability Assessment**: Search for potentially vulnerable services
3. **IoT Security Analysis**: Analyze IoT device security posture
4. **DNS Intelligence Gathering**: DNS-based reconnaissance techniques

Each scenario demonstrates responsible security research practices and provides educational insights into cybersecurity assessment methodologies.

## 🛠️ Available Tools (Auto-Generated)

The server automatically generates tools from Shodan's OpenAPI specification. Here are the main categories:

### Search & Discovery
- **Host Search** (`/shodan/host/search`): Search Shodan's database with advanced filters
- **Host Count** (`/shodan/host/count`): Get result counts without using query credits
- **Host Information** (`/shodan/host/{ip}`): Detailed information about specific IPs
- **Search Facets** (`/shodan/host/search/facets`): Available facets for analysis
- **Search Filters** (`/shodan/host/search/filters`): Available search filters

### DNS Services
- **DNS Resolve** (`/dns/resolve`): Resolve hostnames to IP addresses
- **DNS Reverse** (`/dns/reverse`): Reverse DNS lookups for IPs
- **DNS Domain** (`/dns/domain/{domain}`): Domain information and subdomains

### Scanning & Monitoring
- **Internet Scan** (`/shodan/scan/internet`): Request Internet-wide scans
- **Scan Status** (`/shodan/scans`): View scan history and status
- **Custom Scans** (`/shodan/scan`): Submit custom scan requests

### Account & API
- **Account Profile** (`/account/profile`): API key info and credits
- **API Information** (`/api-info`): Available endpoints and methods
- **Query Search** (`/shodan/query/search`): Search saved queries

### Alerts & Monitoring (Enterprise)
- **Network Alerts** (`/shodan/alert`): Monitor network changes
- **Alert Management** (`/shodan/alert/{id}`): Manage specific alerts
- **Notifiers** (`/notifier`): Configure alert notifications

## 🔍 Usage Examples

### Basic Search
```python
# The MCP client will have access to all Shodan endpoints
# Example searches that work automatically:

# Search for SSH servers
GET /shodan/host/search?query=port:22&key=API_KEY

# Get detailed host information
GET /shodan/host/8.8.8.8?key=API_KEY

# Count results without using credits
GET /shodan/host/count?query=apache&key=API_KEY
```

### Advanced Queries
```python
# Complex searches with filters
GET /shodan/host/search?query=apache country:US org:"Amazon"&facets=port,product

# DNS operations
GET /dns/resolve?hostnames=google.com,github.com

# Reverse DNS
GET /dns/reverse?ips=8.8.8.8,1.1.1.1
```

## 🎯 Query Syntax & Filters

Shodan supports powerful search queries with filters:

### Basic Searches
- `apache` - Find Apache servers
- `port:22` - Find SSH services
- `nginx` - Find Nginx servers
- `product:MySQL` - Find MySQL databases

### Advanced Filters
- `country:US` - Filter by country (US, DE, CN, etc.)
- `city:"New York"` - Filter by city
- `org:"Google"` - Filter by organization
- `net:192.168.1.0/24` - Scan network range
- `hostname:example.com` - Filter by hostname
- `os:Windows` - Filter by operating system
- `version:2.4` - Filter by software version

### Combining Filters
```
apache country:US port:443
product:MySQL version:5.7 country:DE
nginx org:"Cloudflare" -country:CN
```

### Facet Analysis
Use facets to get statistical breakdowns:
- `country` - Results by country
- `org` - Results by organization  
- `port` - Results by port
- `product` - Results by product/service
- `version` - Results by version
- `asn` - Results by Autonomous System

## 🔧 Configuration

### Environment Variables
```bash
# Required
export SHODAN_API_KEY="your_api_key_here"

# Optional
export SHODAN_TIMEOUT="30"          # Request timeout in seconds
export SHODAN_DEBUG="true"          # Enable debug logging
export SHODAN_BASE_URL="https://api.shodan.io"  # Custom base URL
```

### Route Mapping Customization
The server uses intelligent route mapping:

```python
# Search endpoints → Tools (for AI agent use)
RouteMap(methods=["GET"], pattern=r".*/search.*", mcp_type=MCPType.TOOL)

# Host info with parameters → ResourceTemplates  
RouteMap(methods=["GET"], pattern=r".*\{.*\}.*", mcp_type=MCPType.RESOURCE_TEMPLATE)

# Account/API info → Resources
RouteMap(methods=["GET"], pattern=r".*/account/.*", mcp_type=MCPType.RESOURCE)
```

## 🔐 Security Best Practices

### API Key Management
- **Environment Variables**: Always use `SHODAN_API_KEY` environment variable
- **Never Hardcode**: Never commit API keys to version control
- **Rotation**: Regularly rotate API keys for production use
- **Scope Limitation**: Use API keys with minimal required permissions

### Rate Limiting & Credits
- **Monitor Usage**: Check account profile regularly for credit usage
- **Efficient Queries**: Use count endpoints to avoid unnecessary credit usage
- **Caching**: Implement caching for frequently accessed data
- **Batch Operations**: Group related queries when possible

### Ethical Usage
- **Legitimate Research**: Use only for authorized security research
- **Responsible Disclosure**: Follow responsible disclosure for vulnerabilities
- **Legal Compliance**: Comply with applicable laws and regulations
- **Target Consent**: Ensure proper authorization for target systems

## 🚀 Integration with AI Agents

### LangGraph Integration
```python
from langgraph import StateGraph
from mcp.client import Client

async def create_shodan_agent():
    # Connect to Shodan MCP server
    client = Client("stdio", "python shodan_mcp.py")
    
    # All Shodan endpoints automatically available as tools
    def reconnaissance_step(state):
        target = state["target"]
        
        # Search for the target
        search_results = await client.call_tool(
            "shodan_host_search", 
            {"query": f"hostname:{target}"}
        )
        
        # Get detailed host info for found IPs
        hosts = []
        for match in search_results.get("matches", []):
            host_info = await client.call_tool(
                "shodan_host_info",
                {"ip": match["ip_str"]}
            )
            hosts.append(host_info)
        
        return {"reconnaissance_data": hosts}
    
    # Build agent workflow
    graph = StateGraph()
    graph.add_node("recon", reconnaissance_step)
    return graph.compile()
```

### Claude/GPT Integration
```python
# The MCP server exposes all Shodan capabilities to AI models
# Models can automatically discover and use:
# - Search tools for finding targets
# - Host information for detailed analysis  
# - DNS tools for infrastructure mapping
# - Account tools for credit management
```

## 🧪 Testing

Run the test suite to validate functionality:

```bash
python test_shodan_openapi.py
```

The tests validate:
- ✅ API key configuration
- ✅ OpenAPI specification loading
- ✅ Route mapping configuration
- ✅ HTTP client setup
- ✅ Error handling

## 📊 Monitoring & Debugging

### Debug Mode
```bash
SHODAN_DEBUG=true python shodan_mcp.py
```

### Logging
The server includes structured logging:
- Request/response logging
- Error tracking with context
- Performance metrics
- API usage monitoring

### Health Checks
Monitor server health:
- API key validity
- Shodan API connectivity
- Request success rates
- Credit usage tracking

## 🆚 Advantages of OpenAPI Integration

### vs Manual Tool Definition
| Feature | OpenAPI Integration | Manual Tools |
|---------|-------------------|--------------|
| **API Coverage** | 100% automatic | Manual subset |
| **Maintenance** | Zero maintenance | Constant updates |
| **Documentation** | Auto-generated | Manual writing |
| **Validation** | Built-in | Custom implementation |
| **Error Handling** | Standardized | Custom per tool |
| **Future-Proof** | Always current | Becomes outdated |

### Performance Benefits
- **Async Operations**: Built on httpx for high concurrency
- **Connection Pooling**: Efficient HTTP connection reuse  
- **Request Validation**: Automatic parameter validation
- **Response Parsing**: Optimized JSON handling

## 🔄 Updates & Maintenance

The OpenAPI integration automatically stays current with Shodan's API:

1. **Automatic Updates**: Server loads latest OpenAPI spec on startup
2. **New Endpoints**: Automatically available without code changes
3. **Parameter Changes**: Handled transparently by OpenAPI validation
4. **Deprecations**: Gracefully handled with proper error messages

## 🤝 Contributing

Contributions welcome! Focus areas:

1. **Route Mapping**: Improve MCP type assignments for better UX
2. **Error Handling**: Enhanced error messages and recovery
3. **Performance**: Caching and optimization strategies
4. **Documentation**: Usage examples and best practices
5. **Testing**: Additional test coverage and scenarios

## 📄 License

This project follows the same license as the parent repository.

## ⚠️ Disclaimer

This tool is for legitimate cybersecurity research and educational purposes only. Users are responsible for:

- Complying with applicable laws and regulations
- Following Shodan's Terms of Service
- Obtaining proper authorization for target systems
- Using the tool ethically and responsibly

The authors are not responsible for misuse of this tool.

---

## 🆘 Troubleshooting

### Common Issues

**API Key Not Found**
```
Error: SHODAN_API_KEY environment variable not set
```
Solution: `export SHODAN_API_KEY='your_key_here'`

**Invalid API Key**
```
HTTP 401: Unauthorized
```
Solution: Verify API key is correct and active

**Rate Limiting**
```
HTTP 429: Too Many Requests
```
Solution: Wait and retry, or upgrade Shodan account

**Connection Issues**
```
Connection error - unable to reach Shodan API
```
Solution: Check internet connectivity and firewall settings

**OpenAPI Loading Failed**
```
Failed to load OpenAPI specification
```
Solution: Check internet connection to developer.shodan.io

### Getting Help

1. **Check API Status**: Visit https://developer.shodan.io/api/status
2. **Verify Account**: Login to https://account.shodan.io
3. **Test Connectivity**: `curl https://api.shodan.io/api-info`
4. **Review Logs**: Enable debug mode for detailed logging

For additional support, consult the Shodan documentation at https://developer.shodan.io/