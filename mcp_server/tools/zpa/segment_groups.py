from typing import Annotated, Dict, List, Optional

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
# READ-ONLY OPERATIONS
# =============================================================================

def zpa_list_segment_groups(
    search: Annotated[Optional[str], Field(description="Search term for listing groups.")] = None,
    page: Annotated[Optional[str], Field(description="Page number for pagination.")] = None,
    page_size: Annotated[Optional[str], Field(description="Items per page for pagination.")] = None,
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict]:
    """List ZPA segment groups with optional filtering and pagination."""
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    sg = client.zpa.segment_groups
    
    qp = {"microtenant_id": microtenant_id}
    if search:
        qp["search"] = search
    if page:
        qp["page"] = page
    if page_size:
        qp["page_size"] = page_size
    
    groups, _, err = sg.list_groups(query_params=qp)
    if err:
        raise Exception(f"Failed to list segment groups: {err}")
    return [g.as_dict() for g in (groups or [])]


def zpa_get_segment_group(
    group_id: Annotated[str, Field(description="ID of the segment group.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Get a specific ZPA segment group by ID."""
    if not group_id:
        raise ValueError("group_id is required")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    sg = client.zpa.segment_groups
    
    result, _, err = sg.get_group(group_id, query_params={"microtenant_id": microtenant_id})
    if err:
        raise Exception(f"Failed to get segment group {group_id}: {err}")
    return result.as_dict()


# =============================================================================
# WRITE OPERATIONS
# =============================================================================

def zpa_create_segment_group(
    name: Annotated[str, Field(description="Name of the segment group.")],
    description: Annotated[Optional[str], Field(description="Description of the segment group.")] = None,
    enabled: Annotated[bool, Field(description="Whether the group is enabled.")] = True,
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Create a new ZPA segment group."""
    if not name:
        raise ValueError("name is required")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    sg = client.zpa.segment_groups
    
    body = {"name": name, "description": description, "enabled": enabled}
    if microtenant_id:
        body["microtenant_id"] = microtenant_id
    
    result, _, err = sg.add_group(**body)
    if err:
        raise Exception(f"Failed to create segment group: {err}")
    return result.as_dict()


def zpa_update_segment_group(
    group_id: Annotated[str, Field(description="ID of the segment group.")],
    name: Annotated[Optional[str], Field(description="Name of the segment group.")] = None,
    description: Annotated[Optional[str], Field(description="Description of the segment group.")] = None,
    enabled: Annotated[Optional[bool], Field(description="Whether the group is enabled.")] = None,
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Update an existing ZPA segment group."""
    if not group_id:
        raise ValueError("group_id is required for update")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    sg = client.zpa.segment_groups
    
    body = {"name": name, "description": description, "enabled": enabled}
    if microtenant_id:
        body["microtenant_id"] = microtenant_id
    
    result, _, err = sg.update_group_v2(group_id, **body)
    if err:
        raise Exception(f"Failed to update segment group {group_id}: {err}")
    return result.as_dict()


def zpa_delete_segment_group(
    group_id: Annotated[str, Field(description="ID of the segment group.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
    kwargs: str = "{}"
) -> str:
    """Delete a ZPA segment group.
    
    🚨 DESTRUCTIVE OPERATION - Requires double confirmation.
    This action cannot be undone.
    """
    from mcp_server.common.elicitation import check_confirmation, extract_confirmed_from_kwargs
    
    # Extract confirmation from kwargs (hidden from tool schema)
    confirmed = extract_confirmed_from_kwargs(kwargs)
    
    confirmation_check = check_confirmation(
        "zpa_delete_segment_group",
        confirmed,
        {"group_id": group_id}
    )
    if confirmation_check:
        return confirmation_check
    
    if not group_id:
        raise ValueError("group_id is required for delete")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    sg = client.zpa.segment_groups
    
    _, _, err = sg.delete_group(group_id, microtenant_id=microtenant_id)
    if err:
        raise Exception(f"Failed to delete segment group {group_id}: {err}")
    return f"Successfully deleted segment group {group_id}"
