import argparse
import os
import sys
import uvicorn
with open("debug_top.log", "w") as f:
    f.write("Top of file\n")

from typing import Dict, List, Optional, Set
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# from mcp_server import services
import services
from common.logging import configure_logging, get_logger 

# Import version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("zscaler-mcp")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version
        __version__ = version("zscaler-mcp")
    except ImportError:
        # Final fallback - read from pyproject.toml or use a default
        __version__ = "0.2.2"

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger(__name__)

class ZscalerMCPServer:
    """Main server class for the Zscaler Integrations MCP Server."""

    def __init__(
        self,
        # Removed: client_id, client_secret, customer_id, vanity_domain, cloud
        debug: bool = False,
        enabled_services: Optional[Set[str]] = None,
        enabled_tools: Optional[Set[str]] = None,
        user_agent_comment: Optional[str] = None,
        enable_write_tools: bool = False,
        write_tools: Optional[Set[str]] = None,
    ):
        """Initialize the Server without hardcoded credentials."""
        self.debug = debug
        self.user_agent_comment = user_agent_comment

        self.enabled_services = enabled_services or set(services.get_service_names())
        self.enabled_tools = enabled_tools or set()
        self.enable_write_tools = enable_write_tools
        self.write_tools = write_tools 

        configure_logging(debug=self.debug, use_stderr=True)
        logger = get_logger(__name__)
        
        # Security logging remains relevant even without credentials
        logger.info("Initializing Zscaler Integrations MCP Server (Dynamic Credential Mode)")
        
        # Logic remains the same, but notice self.zscaler_client is still None.
        # Your service tools will now need a way to fetch credentials dynamically 
        # during the tool call (e.g., from a DB or vault).
        self.zscaler_client = None

        self.server = FastMCP(
            name="Zscaler Integrations MCP Server",
            instructions="This server provides access to Zscaler capabilities.",
            debug=self.debug,
            log_level="DEBUG" if self.debug else "INFO",
        )

        # Initialize and register services
        self.services = {}
        available_services = services.get_available_services()
        # print(available_services)
        # print(self.enabled_services)
        for service_name in self.enabled_services:
            if service_name in available_services:
                service_class = available_services[service_name]
                # We pass None; the service tools must handle their own auth logic now
                self.services[service_name] = service_class()

        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register all enabled tools from enabled services."""
        for service_name, service in self.services.items():
            try:
                service.register_tools(
                    self.server,
                    enabled_tools=self.enabled_tools,
                    enable_write_tools=self.enable_write_tools,
                    write_tools=self.write_tools,
                )
            except Exception as e:
                logger.error(f"Failed to register tools for service {service_name}: {e}")

    def _register_resources(self):
        """Register all resources from enabled services."""
        for service_name, service in self.services.items():
            try:
                service.register_resources(self.server)
            except Exception as e:
                logger.error(f"Failed to register resources for service {service_name}: {e}")

    def run(self, transport="stdio", host="127.0.0.1", port=8000):
        """Run the MCP server."""
        return self.server.run(transport=transport)


def list_available_tools(selected_services=None, enabled_tools=None):
    """Print all available tool metadata names and descriptions, optionally filtered by services and tools."""
    import services as svc_mod

    available_services = svc_mod.get_available_services()
    if selected_services:
        available_services = {
            k: v for k, v in available_services.items() if k in selected_services
        }
    logger.info("Available tools:")
    for service_name, service_class in available_services.items():
        service = service_class(None)
        # Get tool metadata from the service's register_tools method
        if hasattr(service, "tools") and hasattr(service, "register_tools"):
            # Create a mock server to capture the tool metadata
            class MockServer:
                def __init__(self):
                    self.tools = []

                def add_tool(self, tool, name=None, description=None, annotations=None):
                    self.tools.append(
                        {
                            "tool": tool,
                            "name": name or tool.__name__,
                            "description": description or (tool.__doc__ or ""),
                            "annotations": annotations,
                        }
                    )

            mock_server = MockServer()
            service.register_tools(mock_server, enabled_tools=enabled_tools)

            for tool_info in mock_server.tools:
                logger.info(
                    f"  [{service_name}] {tool_info['name']}: {tool_info['description']}"
                )


def parse_services_list(services_string):
    """Parse and validate comma-separated service list.

    Args:
        services_string: Comma-separated string of service names

    Returns:
        List of validated service names (returns all available services if empty string)

    Raises:
        argparse.ArgumentTypeError: If any service names are invalid
    """
    # Get available services
    available_services = services.get_service_names()

    # If empty string, return all available services (default behavior)
    if not services_string:
        return available_services

    # Split by comma and clean up whitespace
    service_list = [s.strip() for s in services_string.split(",") if s.strip()]

    # Validate against available services
    invalid_services = [s for s in service_list if s not in available_services]
    if invalid_services:
        raise argparse.ArgumentTypeError(
            f"Invalid services: {', '.join(invalid_services)}. "
            f"Available services: {', '.join(available_services)}"
        )

    return service_list


def parse_tools_list(tools_string):
    """Parse and validate comma-separated tool list.

    Args:
        tools_string: Comma-separated string of tool names

    Returns:
        List of validated tool names (returns empty list if empty string)

    Raises:
        argparse.ArgumentTypeError: If any tool names are invalid
    """
    # If empty string, return empty list (no tools selected)
    if not tools_string:
        return []

    # Split by comma and clean up whitespace
    tool_list = [t.strip() for t in tools_string.split(",") if t.strip()]

    # Get all available tools from all services for validation
    available_services = services.get_available_services()
    all_available_tools = []

    for service_name, service_class in available_services.items():
        service_instance = service_class(None)  # Create instance to get tools

        # Create a mock server to capture the tool metadata names
        class MockServer:
            def __init__(self):
                self.tools = []

            def add_tool(self, tool, name=None, description=None, annotations=None):
                self.tools.append(
                    {
                        "tool": tool,
                        "name": name or tool.__name__,
                        "description": description or (tool.__doc__ or ""),
                        "annotations": annotations,
                    }
                )

        mock_server = MockServer()
        service_instance.register_tools(mock_server)

        for tool_info in mock_server.tools:
            all_available_tools.append(tool_info["name"])

    # Validate against available tools
    invalid_tools = [t for t in tool_list if t not in all_available_tools]
    if invalid_tools:
        raise argparse.ArgumentTypeError(
            f"Invalid tools: {', '.join(invalid_tools)}. "
            f"Available tools: {', '.join(all_available_tools)}"
        )

    return tool_list


def parse_args():
    """Parse command line arguments - Zscaler credential arguments removed."""
    parser = argparse.ArgumentParser(description="Zscaler Integrations MCP Server")

    # Transport and Service selection kept
    parser.add_argument("--transport", "-t", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--services", "-s", type=parse_services_list)
    parser.add_argument("--debug", "-d", action="store_true")
    
    # Security flags kept
    parser.add_argument("--enable-write-tools", action="store_true")
    parser.add_argument("--write-tools")
    parser.add_argument("--tools", "-T", help="Comma separated list of specific tools to enable")

    # --- REMOVED: client-id, client-secret, customer-id, vanity-domain, cloud ---
    # These are no longer accepted via CLI or root Environment Variables here.

    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", "-p", type=int, default=8000)

    return parser.parse_args()

def main():
    with open("debug_trace.log", "a") as f:
        f.write("Starting main\n")
    try:
        load_dotenv()
        args = parse_args()
        with open("debug_trace.log", "a") as f:
            f.write(f"Args parsed: {args}\n")

        # Create and run the server without passing credentials
        server = ZscalerMCPServer(
            debug=args.debug if args.debug else False,
            enabled_services=set(args.services) if args.services else None,
            enabled_tools=set(args.tools.split(",")) if args.tools else None,
            enable_write_tools=args.enable_write_tools,
            write_tools=set(args.write_tools.split(",")) if args.write_tools else None,
        )
        with open("debug_trace.log", "a") as f:
            f.write("Server initialized, starting run\n")
        server.run(args.transport, host=args.host, port=args.port)
        with open("debug_trace.log", "a") as f:
            f.write("Server run returned\n")
    except Exception as e:
        with open("debug_trace.log", "a") as f:
            f.write(f"Exception in main: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        raise

if __name__ == "__main__":
    main()
