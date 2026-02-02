from typing import Annotated, List, Union

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


def app_protection_profile_manager(
    action: Annotated[str, Field(description="Must be 'read'.")],
    name: Annotated[
        str,
        Field(
            description="Name of the profile to match. If provided, only profiles with matching name will be returned."
        ),
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Union[List[dict], dict]:
    """
    Tool for listing and searching ZPA App Protection Profiles (Inspection Profiles).

    Supported actions:
    - read: returns all profiles or a specific profile by name.

    Args:
        action (str): Must be 'read'.
        name (str, optional): Name of the profile to match. If provided, only profiles with matching name will be returned.

    Returns:
        list[dict] or dict: A single profile dict if name is matched, or a list of all profiles.
    """
    if action != "read":
        raise ValueError("Only 'read' action is supported")

    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)

    query_params = {"search": name} if name else {}

    profiles, _, err = client.zpa.app_protection.list_profiles(
        query_params=query_params
    )
    if err:
        raise Exception(f"Failed to list app protection profiles: {err}")

    profile_dicts = [p.as_dict() for p in (profiles or [])]

    if name:
        for p in profile_dicts:
            if p.get("name") == name:
                return p
        raise ValueError(f"No profile found with name: {name}")

    return profile_dicts
