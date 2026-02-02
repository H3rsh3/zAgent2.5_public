from typing import Annotated, List, Optional

from pydantic import Field

from mcp_server.client import get_zscaler_client

from zsTenantDB import get_tenant

# =============================================================================
# READ-ONLY OPERATIONS
# =============================================================================

def zcc_list_devices(
    username: Annotated[Optional[str], Field(description="Username to filter by (e.g., 'jdoe@acme.com').")] = None,
    os_type: Annotated[Optional[str], Field(description="Device operating system type: ios, android, windows, macos, linux.")] = None,
    page: Annotated[Optional[int], Field(description="Page number for paginated results.")] = None,
    page_size: Annotated[Optional[int], Field(description="Number of results per page. Default is 50. Max is 5000.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zcc",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[dict]:
    """
    List ZCC device enrollment information from the Zscaler Client Connector Portal.
    
    This is a read-only operation to retrieve device information.
    """
    tenant = get_tenant(tenant_name)
    client = get_zscaler_client(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    # client = get_zscaler_client(use_legacy=use_legacy, service=service)
    
    query_params = {}
    if username:
        query_params["username"] = username
    if os_type:
        query_params["os_type"] = os_type
    if page:
        query_params["page"] = page
    if page_size:
        query_params["page_size"] = page_size
    
    devices, _, err = client.zcc.devices.list_devices(query_params=query_params)
    if err:
        raise Exception(f"Error listing ZCC devices: {err}")
    return [d.as_dict() for d in devices]
