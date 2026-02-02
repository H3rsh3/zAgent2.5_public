from typing import Annotated, List, Optional

from pydantic import Field

from mcp_server.client import get_zscaler_client
from zsTenantDB import get_tenant

# =============================================================================
# READ-ONLY OPERATIONS
# =============================================================================

def zia_list_gre_ranges(
    internal_ip_range: Annotated[Optional[str], Field(description="CIDR range filter (e.g., '172.17.47.247-172.17.47.240').")] = None,
    static_ip: Annotated[Optional[str], Field(description="Filter by the associated static IP address.")] = None,
    limit: Annotated[Optional[int], Field(description="Max number of ranges to return.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zia",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List:
    """
    Discover available GRE internal IP ranges in ZIA.
    
    This is a read-only operation that returns available GRE ranges.
    If no filters are provided, returns all available ranges.
    """
    tenant = get_tenant(tenant_name)
    client = get_zscaler_client(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    gre_api = client.zia.gre_tunnel
    
    query_params = {}
    if internal_ip_range:
        query_params["internal_ip_range"] = internal_ip_range
    if static_ip:
        query_params["static_ip"] = static_ip
    if limit:
        query_params["limit"] = limit
    
    ranges, _, err = gre_api.list_gre_ranges(query_params=query_params if query_params else None)
    if err:
        raise Exception(f"Failed to retrieve GRE ranges: {err}")
    
    return ranges
