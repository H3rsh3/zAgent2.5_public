from typing import Annotated, Dict, List, Optional

from pydantic import Field

from mcp_server.client import get_zscaler_client
from mcp_server.utils_2 import convert_v1_to_v2_response, convert_v2_to_sdk_format

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

def zpa_list_isolation_policy_rules(
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    query_params: Annotated[Optional[Dict], Field(description="Optional query parameters for filtering.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> List[Dict]:
    """List ZPA isolation policy rules."""
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.policies
    policy_type = "isolation"
    
    qp = query_params or {}
    if microtenant_id:
        qp["microtenant_id"] = microtenant_id
    
    rules, _, err = api.list_rules(policy_type, query_params=qp)
    if err:
        raise Exception(f"Failed to list isolation policy rules: {err}")
    return [r.as_dict() for r in (rules or [])]


def zpa_get_isolation_policy_rule(
    rule_id: Annotated[str, Field(description="Rule ID for the isolation policy rule.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Get a specific ZPA isolation policy rule by ID."""
    if not rule_id:
        raise ValueError("rule_id is required")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.policies
    policy_type = "isolation"
    
    result, _, err = api.get_rule(policy_type, rule_id, query_params={"microtenantId": microtenant_id})
    if err:
        raise Exception(f"Failed to get isolation policy rule {rule_id}: {err}")
    
    rule_data = result.as_dict()
    # Convert response to standardized v2 format
    if "conditions" in rule_data:
        rule_data["conditions"] = convert_v1_to_v2_response(rule_data["conditions"])
    return rule_data


# =============================================================================
# WRITE OPERATIONS
# =============================================================================

def zpa_create_isolation_policy_rule(
    name: Annotated[str, Field(description="Name of the isolation policy rule.")],
    action_type: Annotated[str, Field(description="Action type for the policy rule.")],
    zpn_isolation_profile_id: Annotated[Optional[str], Field(description="Isolation profile ID (required if action_type is 'isolate').")] = None,
    description: Annotated[Optional[str], Field(description="Description of the isolation policy rule.")] = None,
    rule_order: Annotated[Optional[str], Field(description="Rule order for the isolation policy rule.")] = None,
    conditions: Annotated[Optional[List], Field(description="Conditions for the policy rule.")] = None,
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Create a new ZPA isolation policy rule."""
    if not name or not action_type:
        raise ValueError("'name' and 'action_type' are required for creating an isolation rule")
    if action_type.lower() == "isolate" and not zpn_isolation_profile_id:
        raise ValueError("'zpn_isolation_profile_id' is required when action_type is 'isolate'")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.policies
    
    # Convert input conditions to SDK format
    try:
        processed_conditions = convert_v2_to_sdk_format(conditions)
    except Exception as e:
        raise ValueError(f"Invalid conditions format: {str(e)}")
    
    payload = {
        "name": name,
        "action": action_type,
        "zpn_isolation_profile_id": zpn_isolation_profile_id,
        "description": description,
        "rule_order": rule_order,
        "conditions": processed_conditions,
    }
    if microtenant_id:
        payload["microtenant_id"] = microtenant_id
    
    created, _, err = api.add_isolation_rule_v2(**payload)
    if err:
        raise Exception(f"Failed to create isolation policy rule: {err}")
    return created.as_dict()


def zpa_update_isolation_policy_rule(
    rule_id: Annotated[str, Field(description="Rule ID for the isolation policy rule.")],
    name: Annotated[Optional[str], Field(description="Name of the isolation policy rule.")] = None,
    action_type: Annotated[Optional[str], Field(description="Action type for the policy rule.")] = None,
    zpn_isolation_profile_id: Annotated[Optional[str], Field(description="Isolation profile ID.")] = None,
    description: Annotated[Optional[str], Field(description="Description of the isolation policy rule.")] = None,
    rule_order: Annotated[Optional[str], Field(description="Rule order for the isolation policy rule.")] = None,
    conditions: Annotated[Optional[List], Field(description="Conditions for the policy rule.")] = None,
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
) -> Dict:
    """Update an existing ZPA isolation policy rule."""
    if not rule_id:
        raise ValueError("'rule_id' is required for updating an isolation rule")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.policies
    
    # Convert input conditions to SDK format
    try:
        processed_conditions = convert_v2_to_sdk_format(conditions)
    except Exception as e:
        raise ValueError(f"Invalid conditions format: {str(e)}")
    
    payload = {
        "name": name,
        "action": action_type,
        "zpn_isolation_profile_id": zpn_isolation_profile_id,
        "description": description,
        "rule_order": rule_order,
        "conditions": processed_conditions,
    }
    if microtenant_id:
        payload["microtenant_id"] = microtenant_id
    
    updated, _, err = api.update_isolation_rule_v2(rule_id, **payload)
    if err:
        raise Exception(f"Failed to update isolation policy rule {rule_id}: {err}")
    
    rule_data = updated.as_dict()
    if "conditions" in rule_data:
        rule_data["conditions"] = convert_v1_to_v2_response(rule_data["conditions"])
    return rule_data


def zpa_delete_isolation_policy_rule(
    rule_id: Annotated[str, Field(description="Rule ID for the isolation policy rule.")],
    microtenant_id: Annotated[Optional[str], Field(description="Microtenant ID for scoping.")] = None,
    use_legacy: Annotated[bool, Field(description="Whether to use the legacy API.")] = False,
    service: Annotated[str, Field(description="The service to use.")] = "zpa",
    tenant_name: Annotated[str, Field(description="The tenant name")] = "",
    kwargs: str = "{}"
) -> str:
    """Delete a ZPA isolation policy rule."""
    from mcp_server.common.elicitation import check_confirmation, extract_confirmed_from_kwargs
    
    # Extract confirmation from kwargs (hidden from tool schema)
    confirmed = extract_confirmed_from_kwargs(kwargs)
    
    confirmation_check = check_confirmation(
        "zpa_delete_isolation_policy_rule",
        confirmed,
        {}
    )
    if confirmation_check:
        return confirmation_check
    

    if not rule_id:
        raise ValueError("'rule_id' is required")
    
    client = get_authenticated_client(tenant_name=tenant_name, use_legacy=use_legacy, service=service)
    api = client.zpa.policies
    policy_type = "isolation"
    
    _, _, err = api.delete_rule(policy_type, rule_id, microtenant_id=microtenant_id)
    if err:
        raise Exception(f"Failed to delete isolation policy rule {rule_id}: {err}")
    return f"Successfully deleted isolation policy rule {rule_id}"
