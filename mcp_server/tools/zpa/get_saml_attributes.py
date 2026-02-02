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


def saml_attribute_manager(
    action: Annotated[str, Field(description="Must be 'read'.")],
    idp_name: Annotated[
        str, Field(description="The name of the IdP to filter attributes by.")
    ] = None,
    query_params: Annotated[
        dict, Field(description="Optional filters like search, page, page_size.")
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Union[List[dict], str]:
    """
    Tool for querying ZPA SAML Attributes.

    Supported actions:
    - read: Lists all SAML attributes or filters by IdP name (resolved internally).

    Args:
        action (str): Must be 'read'.
        idp_name (str, optional): The name of the IdP to filter attributes by.
        query_params (dict, optional): Optional filters like search, page, page_size.

    Returns:
        List[dict] or str: A list of SAML attribute dictionaries.
    """
    if action != "read":
        raise ValueError("Only 'read' action is supported")

    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)

    saml_api = client.zpa.saml_attributes
    idp_api = client.zpa.idp
    query_params = query_params or {}

    if idp_name:
        # Resolve IdP ID from name
        idps, _, err = idp_api.list_idps(query_params={"search": idp_name})
        if err:
            raise Exception(f"Failed to search IdP: {err}")
        idp_match = next((i for i in idps if i.name.lower() == idp_name.lower()), None)
        if not idp_match:
            raise Exception(f"No IdP found with name: {idp_name}")
        idp_id = idp_match.id

        # Fetch SAML attributes for the resolved IdP
        attributes, _, err = saml_api.list_saml_attributes_by_idp(
            idp_id=idp_id, query_params=query_params
        )
        if err:
            raise Exception(f"Failed to list SAML attributes for IdP {idp_name}: {err}")
        return [a.as_dict() for a in attributes]

    else:
        # Fetch all SAML attributes
        attributes, _, err = saml_api.list_saml_attributes(query_params=query_params)
        if err:
            raise Exception(f"Failed to list SAML attributes: {err}")
        return [a.as_dict() for a in attributes]
