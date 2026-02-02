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


def enrollment_certificate_manager(
    action: Annotated[str, Field(description="Must be 'read'.")],
    certificate_id: Annotated[
        str,
        Field(description="Certificate ID to retrieve (fallback if name is not used)."),
    ] = None,
    name: Annotated[str, Field(description="Certificate name to search for.")] = None,
    query_params: Annotated[
        dict,
        Field(description="Optional query parameters for filtering via search key."),
    ] = None,
    use_legacy: Annotated[
        bool, Field(description="Whether to use the legacy API.")
    ] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Union[dict, List[dict], str]:
    """
    Get-only tool for retrieving ZPA Enrollment Certificates.

    Supported actions:
    - read: retrieves a certificate by name (preferred) or by ID (fallback).

    Args:
        action (str): Must be "read".
        name (str, optional): Certificate name to search for.
        certificate_id (str, optional): Fallback if name search is not used.
        query_params (dict, optional): Used for filtering via search key.

    Returns:
        dict or list[dict] or str
    """
    if action != "read":
        raise ValueError("Only 'read' action is supported.")

    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)

    api = client.zpa.enrollment_certificates

    if name:
        query_params = query_params or {}
        query_params["search"] = name
        certs, _, err = api.list_enrolment(query_params=query_params)
        if err:
            raise Exception(f"Search by name failed: {err}")
        matches = [c for c in certs if c.name.lower() == name.lower()]
        if not matches:
            return f"No certificate found matching name '{name}'"
        return matches[0].as_dict()

    elif certificate_id:
        cert, _, err = api.get_enrolment(certificate_id)
        if err:
            raise Exception(f"Lookup by ID failed: {err}")
        return cert.as_dict()

    else:
        certs, _, err = api.list_enrolment()
        if err:
            raise Exception(f"Listing certificates failed: {err}")
        return [c.as_dict() for c in (certs or [])]
