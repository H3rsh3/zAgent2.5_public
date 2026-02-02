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


def app_segments_by_type_manager(
    application_type: Annotated[
        str,
        Field(
            description="Application type to filter by. Must be one of 'BROWSER_ACCESS', 'INSPECT', or 'SECURE_REMOTE_ACCESS'."
        ),
    ],
    expand_all: Annotated[
        bool, Field(description="Whether to expand all related data.")
    ] = False,
    query_params: Annotated[
        dict,
        Field(
            description="Optional filters like 'search', 'page_size', or 'microtenant_id'."
        ),
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Union[List[dict], str]:
    """
    Tool to retrieve ZPA application segments by type.

    Args:
        application_type (str): Required. Must be one of "BROWSER_ACCESS", "INSPECT", or "SECURE_REMOTE_ACCESS".
        expand_all (bool, optional): Whether to expand all related data. Defaults to False.
        query_params (dict, optional): Filters like 'search', 'page_size', or 'microtenant_id'.

    Returns:
        list[dict]: List of matching application segments.
    """
    if application_type not in ("BROWSER_ACCESS", "INSPECT", "SECURE_REMOTE_ACCESS"):
        raise ValueError(
            "Invalid application_type. Must be one of 'BROWSER_ACCESS', 'INSPECT', or 'SECURE_REMOTE_ACCESS'."
        )

    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)

    api = client.zpa.app_segment_by_type
    query_params = query_params or {}

    segments, _, err = api.get_segments_by_type(
        application_type=application_type,
        expand_all=expand_all,
        query_params=query_params,
    )
    if err:
        raise Exception(f"Failed to retrieve application segments: {err}")

    return [segment.as_dict() for segment in segments]
