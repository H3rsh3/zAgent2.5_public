from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field

from mcp_server.client import get_zscaler_client
from zsTenantDB import get_tenant

# ============================================================================
# READ-ONLY OPERATIONS
# ============================================================================

def zdx_list_departments(
    search: Annotated[
        Optional[str], Field(description="Search term to filter results by name or ID.")
    ] = None,
    since: Annotated[
        Optional[int],
        Field(
            description="Number of hours to look back for devices (default 2 hours if not provided)."
        ),
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zdx",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict[str, Any]]:
    """
    Lists ZDX departments with optional filtering.
    This is a read-only operation.

    Returns a list of departments (e.g., IT, Finance) configured within the ZDX tenant.
    Supports optional filtering by search term and time range.

    Args:
        search: Optional search term to filter departments by name or ID.
        since: Optional number of hours to look back for device data (default 2 hours).
        use_legacy: Whether to use the legacy API (default False).
        service: The Zscaler service to use (default "zdx").

    Returns:
        List of department dictionaries containing department information.

    Raises:
        Exception: If the department listing fails due to API errors.

    Examples:
        List all departments:
        >>> departments = zdx_list_departments()

        Search for specific department:
        >>> departments = zdx_list_departments(search="Engineering")

        List departments with time filter:
        >>> departments = zdx_list_departments(since=24)
    """
    tenant = get_tenant(tenant_name)
    if not tenant:
        raise ValueError(f"Tenant '{tenant_name}' not found.")
    client = get_zscaler_client(
        client_id=tenant.clientId,
        client_secret=tenant.clientSecret,
        customer_id=tenant.customerId,
        vanity_domain=tenant.vanityDomain,
        use_legacy=use_legacy,
        service=service
    )

    query_params = {}
    if search:
        query_params["search"] = search
    if since:
        query_params["since"] = since

    departments, _, err = client.zdx.admin.list_departments(
        query_params=query_params
    )
    if err:
        raise Exception(f"Error retrieving departments: {err}")
    return [d.as_dict() for d in departments]


def zdx_list_locations(
    search: Annotated[
        Optional[str], Field(description="Search term to filter results by name or ID.")
    ] = None,
    since: Annotated[
        Optional[int],
        Field(
            description="Number of hours to look back for devices (default 2 hours if not provided)."
        ),
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zdx",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict[str, Any]]:
    """
    Lists ZDX locations with optional filtering.
    This is a read-only operation.

    Returns a list of locations (e.g., San Francisco, London) configured within the ZDX tenant.
    Supports optional filtering by search term and time range.

    Args:
        search: Optional search term to filter locations by name or ID.
        since: Optional number of hours to look back for device data (default 2 hours).
        use_legacy: Whether to use the legacy API (default False).
        service: The Zscaler service to use (default "zdx").

    Returns:
        List of location dictionaries containing location information.

    Raises:
        Exception: If the location listing fails due to API errors.

    Examples:
        List all locations:
        >>> locations = zdx_list_locations()

        Search for specific location:
        >>> locations = zdx_list_locations(search="San Francisco")

        List locations with time filter:
        >>> locations = zdx_list_locations(since=48)
    """
    tenant = get_tenant(tenant_name)
    if not tenant:
        raise ValueError(f"Tenant '{tenant_name}' not found.")
    client = get_zscaler_client(
        client_id=tenant.clientId,
        client_secret=tenant.clientSecret,
        customer_id=tenant.customerId,
        vanity_domain=tenant.vanityDomain,
        use_legacy=use_legacy,
        service=service
    )

    query_params = {}
    if search:
        query_params["search"] = search
    if since:
        query_params["since"] = since

    locations, _, err = client.zdx.admin.list_locations(query_params=query_params)
    if err:
        raise Exception(f"Error retrieving locations: {err}")
    return [location.as_dict() for location in locations]
