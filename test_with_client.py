from mcp_server import client
import sys
import os
# Add root directory to path to import zsTenantDB
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zscaler import ZscalerClient
from zsTenantDB import get_tenant

from mcp_server.client import get_zscaler_client as get_zscaler_client_base

def get_zscaler_client(tenant_name: str = None, tenant_config: dict = None):
    if tenant_config:
        config = tenant_config
    elif tenant_name:
        tenant = get_tenant(tenant_name)
        print(dir(tenant))
        if not tenant:
            raise ValueError(f"Tenant '{tenant_name}' not found. Please add it first.")
        
        # Construct config dict
        config = {
            "clientId": tenant.clientId,
            "clientSecret": tenant.clientSecret,
            "vanityDomain": tenant.vanityDomain,
            "customerId": tenant.customerId
        }
    else:
        raise ValueError("Either tenant_name or tenant_config must be provided.")
    
    # Initialize Zscaler Client
    client = ZscalerClient(user_config=config)
    return client

def get_zia_client(tenant_name: str = None, tenant_config: dict = None):
    return get_zscaler_client(tenant_name, tenant_config).zia

def get_zcc_client(tenant_name: str):
    return get_zscaler_client(tenant_name).zcc

def get_zInsights_client(tenant_name: str):
    return get_zscaler_client(tenant_name).zinsights


if __name__ == "__main__":
    # Simple test
    tenant_name = "aixsh"  # Replace with an actual tenant name from your DB
    # client = get_zscaler_client(tenant_name)
    # print(client)
    tenant = get_tenant(tenant_name)
    client2 = get_zscaler_client_base(client_id= tenant.clientId, 
                                      client_secret= tenant.clientSecret, 
                                      customer_id= tenant.customerId, 
                                      vanity_domain= tenant.vanityDomain)
    # print(client2)
    # print(dir(client2.zcc.devices))
    print(client2.zcc.devices.list_devices())
