from typing import Annotated, Union

from pydantic import Field

from mcp_server.client import get_zscaler_client

from zsTenantDB import get_tenant

# =============================================================================

def get_authenticated_client(
    tenant_name: str = "",
    use_legacy: bool = False,
    service: str = "zpa"
):
    """
    Get an authenticated Zscaler client, either using tenant credentials (if tenant_name provided)
    or environment variables (default).
    """
    if tenant_name:
        tenant = get_tenant(tenant_name)
        if not tenant:
            raise ValueError(f"Tenant '{tenant_name}' not found.")
        
        # When using a tenant, we prioritize tenant credentials.
        # Assuming OneAPI is preferred if tenant details are present.
        return get_zscaler_client(
            client_id=tenant.clientId,
            client_secret=tenant.clientSecret,
            customer_id=tenant.customerId,
            vanity_domain=tenant.vanityDomain
        )
    else:
        return get_zscaler_client(use_legacy=use_legacy, service=service)
    
# =============================================================================


def trusted_network_manager(
    action: Annotated[
        str,
        Field(description="Action to perform. Must be 'read'."),
    ],
    network_id: Annotated[
        str,
        Field(description="If provided, retrieves trusted network by ID."),
    ] = None,
    name: Annotated[
        str,
        Field(
            description="If provided, will be used to search for the trusted network."
        ),
    ] = None,
    query_params: Annotated[
        dict,
        Field(description="Optional query parameters for filtering results."),
    ] = None,
    use_legacy: Annotated[
        bool,
        Field(description="Whether to use the legacy API."),
    ] = False,
    service: Annotated[
        str,
        Field(description="The service to use."),
    ] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Union[dict, list[dict], str]:
    """
    Tool for retrieving ZPA Trusted Networks.

    Supported actions:
    - read: Fetch all trusted networks or one by ID or name.

    Args:
        action (str): 'read'
        name (str): If provided, will be used to search for the trusted network.
        network_id (str): If provided, retrieves trusted network by ID.

    Returns:
        Union[dict, list[dict], str]: Trusted network(s) data.
    """
    if action != "read":
        raise ValueError("Only 'read' action is supported")

    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.trusted_networks
    query_params = query_params or {}

    # Fetch by network ID
    if network_id:
        result, _, err = api.get_network(network_id)
        if err:
            raise Exception(f"Failed to fetch trusted network {network_id}: {err}")
        return result.as_dict()

    # Fetch by name if provided
    if name:
        query_params["search"] = name
        networks, _, err = api.list_trusted_networks(query_params=query_params)
        if err:
            raise Exception(f"Failed to search trusted networks by name: {err}")
        matched = next((n for n in networks if n.name == name), None)
        if not matched:
            raise Exception(f"No trusted network found with name '{name}'")
        return matched.as_dict()

    # List all trusted networks
    networks, _, err = api.list_trusted_networks(query_params=query_params)
    if err:
        raise Exception(f"Failed to list trusted networks: {err}")
    return [n.as_dict() for n in networks]
