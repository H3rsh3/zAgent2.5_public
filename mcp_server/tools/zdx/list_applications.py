from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field

from mcp_server.client import get_zscaler_client
from zsTenantDB import get_tenant


def zdx_list_applications(
    location_id: Annotated[
        Optional[List[str]], Field(description="Filter by location ID(s).")
    ] = None,
    department_id: Annotated[
        Optional[List[str]], Field(description="Filter by department ID(s).")
    ] = None,
    geo_id: Annotated[
        Optional[List[str]], Field(description="Filter by geolocation ID(s).")
    ] = None,
    since: Annotated[
        Optional[int], Field(description="Number of hours to look back (default 2h).")
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zdx",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict[str, Any]]:
    """
    Tool for listing all active applications configured within the ZDX tenant.
    
    Returns a list of all active applications with their details, supporting various
    filtering options including location, department, geolocation, and time range.
    
    Args:
        location_id: Optional list of location IDs to filter applications by specific locations.
        department_id: Optional list of department IDs to filter applications by specific departments.
        geo_id: Optional list of geolocation IDs to filter applications by geographic regions.
        since: Optional number of hours to look back for application data (default 2 hours).
        use_legacy: Whether to use the legacy API (default False).
        service: The Zscaler service to use (default "zdx").
        
    Returns:
        List of application dictionaries containing application details.
        
    Raises:
        Exception: If the application listing fails due to API errors.
        
    Examples:
        List all applications in ZDX for the past 2 hours:
        >>> applications = zdx_list_applications()
        
        List applications for a specific location:
        >>> applications = zdx_list_applications(location_id=["545845"])
        
        List applications for the past 10 hours:
        >>> applications = zdx_list_applications(since=10)
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
    if location_id:
        query_params["location_id"] = location_id
    if department_id:
        query_params["department_id"] = department_id
    if geo_id:
        query_params["geo_id"] = geo_id
    if since:
        query_params["since"] = since

    results, _, err = client.zdx.apps.list_apps(query_params=query_params)
    if err:
        raise Exception(f"Application listing failed: {err}")
    
    # The ZDX SDK returns a list of ActiveApplications objects
    if results:
        return [app.as_dict() for app in results]
    else:
        return []