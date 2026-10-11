# LangGraph Example: MCP Server for Cybersecurity Tools
#
# This script implements a small FastAPI application that exposes a ``/scan``
# endpoint. Given an IP address, it performs a real (but limited) port scan using
# the :mod:`python-nmap` module. The goal is to illustrate how an MCP-style server
# could be structured for cybersecurity purposes.
#
# Instructor: Omar Santos @santosomar

import nmap
import requests
from mcp.server.fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("CyberSecurityTools")

@mcp.tool()
def run_nmap_scan(hosts: str, arguments: str = "-sV") -> dict:
    """
    Runs an nmap scan on the specified hosts with the given arguments.

    :param hosts: The target hosts to scan (e.g., '127.0.0.1', 'scanme.nmap.org').
    :param arguments: The nmap command arguments (e.g., '-sV -p 22,80,443').
    :return: A dictionary containing the nmap scan results.
    """
    nm = nmap.PortScanner()
    scan_results = nm.scan(hosts=hosts, arguments=arguments)
    return scan_results

@mcp.tool()
def get_cisa_kev_catalog() -> dict:
    """
    Fetches the latest CISA Known Exploited Vulnerabilities (KEV) catalog.

    :return: A dictionary containing the KEV catalog in JSON format.
    """
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
