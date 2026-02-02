import json
from typing import Annotated, List, Union

from pydantic import Field

from mcp_server.client import get_zscaler_client
from zsTenantDB import get_tenant

# =============================================================================
# READ-ONLY OPERATIONS
# =============================================================================

def zia_list_auth_exempt_urls(
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zia",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[str]:
    """Retrieve the current list of cookie authentication exempt URLs in ZIA."""
    tenant = get_tenant(tenant_name)
    client = get_zscaler_client(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    
    url_list, _, err = client.zia.authentication_settings.get_exempted_urls()
    if err:
        raise Exception(f"Exempt URL list retrieval failed: {err}")
    return url_list or []


# =============================================================================
# WRITE OPERATIONS
# =============================================================================

def zia_add_auth_exempt_urls(
    exempt_urls: Annotated[Union[List[str], str], Field(description="List of exempt URLs to add. Accepts list or JSON string.")],
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zia",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[str]:
    """Add URLs to the cookie authentication exempt list in ZIA."""
    # Convert string input to list if necessary
    processed_urls = exempt_urls
    if isinstance(exempt_urls, str):
        try:
            processed_urls = json.loads(exempt_urls)
            if not isinstance(processed_urls, list):
                raise ValueError("exempt_urls must be a list or JSON array string")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string for exempt_urls: {e}")
    
    if not processed_urls:
        raise ValueError("You must provide a list of exempt URLs to add")
    
    tenant = get_tenant(tenant_name)
    client = get_zscaler_client(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    
    url_list, _, err = client.zia.authentication_settings.add_urls_to_exempt_list(processed_urls)
    if err:
        raise Exception(f"Failed to add exempt URLs: {err}")
    return url_list or []


def zia_delete_auth_exempt_urls(
    exempt_urls: Annotated[Union[List[str], str], Field(description="List of exempt URLs to remove. Accepts list or JSON string.")],
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zia",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
    kwargs: str = "{}"
) -> Union[str, List[str]]:
    """Remove URLs from the cookie authentication exempt list in ZIA.
    
    🚨 DESTRUCTIVE OPERATION - Requires double confirmation.
    This action cannot be undone.
    """
    from mcp_server.common.elicitation import check_confirmation, extract_confirmed_from_kwargs
    
    # Extract confirmation from kwargs (hidden from tool schema)
    confirmed = extract_confirmed_from_kwargs(kwargs)
    
    confirmation_check = check_confirmation(
        "zia_delete_auth_exempt_urls",
        confirmed,
        {}
    )
    if confirmation_check:
        return confirmation_check
    

    # Convert string input to list if necessary
    processed_urls = exempt_urls
    if isinstance(exempt_urls, str):
        try:
            processed_urls = json.loads(exempt_urls)
            if not isinstance(processed_urls, list):
                raise ValueError("exempt_urls must be a list or JSON array string")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string for exempt_urls: {e}")
    
    if not processed_urls:
        raise ValueError("You must provide a list of exempt URLs to delete")
    
    tenant = get_tenant(tenant_name)
    client = get_zscaler_client(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    
    url_list, _, err = client.zia.authentication_settings.delete_urls_from_exempt_list(processed_urls)
    if err:
        raise Exception(f"Failed to delete exempt URLs: {err}")
    return url_list or []
