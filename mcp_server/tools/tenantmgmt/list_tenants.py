from typing import List, Dict
from zsTenantDB import get_all_tenants

def list_tenants() -> List[Dict]:
    """
    List all configured Zscaler tenants from the database.
    """
    tenants = get_all_tenants()
    # Convert SQLModel objects to dictionaries
    return [t.model_dump() for t in tenants]
