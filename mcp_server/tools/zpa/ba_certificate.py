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

# =============================================================================
# READ-ONLY OPERATIONS
# =============================================================================

def zpa_list_ba_certificates(
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    query_params: Annotated[Optional[Dict], Field(description="Optional query parameters for filtering.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict]:
    """List ZPA Browser Access (BA) certificates."""
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.certificates
    
    qp = query_params or {}
    if microtenant_id:
        qp["microtenant_id"] = microtenant_id
    
    certs, _, err = api.list_issued_certificates(query_params=qp)
    if err:
        raise Exception(f"Failed to list BA certificates: {err}")
    return [c.as_dict() for c in certs]


def zpa_get_ba_certificate(
    certificate_id: Annotated[str, Field(description="Certificate ID for the BA certificate.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    query_params: Annotated[Optional[Dict], Field(description="Optional query parameters.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Get a specific ZPA Browser Access certificate by ID."""
    if not certificate_id:
        raise ValueError("certificate_id is required")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.certificates
    
    qp = query_params or {}
    if microtenant_id:
        qp["microtenant_id"] = microtenant_id
    
    cert, _, err = api.get_certificate(certificate_id, query_params=qp)
    if err:
        raise Exception(f"Failed to get BA certificate {certificate_id}: {err}")
    return cert.as_dict()


# =============================================================================
# WRITE OPERATIONS
# =============================================================================

def zpa_create_ba_certificate(
    name: Annotated[str, Field(description="Name of the certificate.")],
    cert_blob: Annotated[str, Field(description="Required PEM string for the certificate.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Create a new ZPA Browser Access certificate."""
    if not name or not cert_blob:
        raise ValueError("Both name and cert_blob are required for certificate creation")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.certificates
    
    body = {"name": name, "cert_blob": cert_blob}
    if microtenant_id:
        body["microtenant_id"] = microtenant_id
    
    created, _, err = api.add_certificate(**body)
    if err:
        raise Exception(f"Failed to create BA certificate: {err}")
    return created.as_dict()


def zpa_delete_ba_certificate(
    certificate_id: Annotated[str, Field(description="Certificate ID for the BA certificate.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
    kwargs: str = "{}"
) -> str:
    """Delete a ZPA Browser Access certificate."""
    from mcp_server.common.elicitation import check_confirmation, extract_confirmed_from_kwargs
    
    # Extract confirmation from kwargs (hidden from tool schema)
    confirmed = extract_confirmed_from_kwargs(kwargs)
    
    confirmation_check = check_confirmation(
        "zpa_delete_ba_certificate",
        confirmed,
        {}
    )
    if confirmation_check:
        return confirmation_check
    

    if not certificate_id:
        raise ValueError("certificate_id is required for deletion")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.certificates
    
    _, _, err = api.delete_certificate(certificate_id, microtenant_id=microtenant_id)
    if err:
        raise Exception(f"Failed to delete BA certificate {certificate_id}: {err}")
    return f"Successfully deleted BA certificate {certificate_id}"
