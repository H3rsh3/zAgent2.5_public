from typing import Optional, List
from sqlmodel import SQLModel, Field, Session, create_engine, select
import os

# Define the Tenant Model
class Tenant(SQLModel, table=True):
    tenantName: str = Field(primary_key=True)
    clientId: Optional[str] = Field(default=None)
    clientSecret: Optional[str] = Field(default=None)
    vanityDomain: Optional[str] = Field(default=None)
    customerId: Optional[str] = Field(default=None)
    testTenant: Optional[str] = Field(default=None)

# Database Setup
sqlite_file_name = "tenants.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# CRUD Operations
def add_tenant(tenantName: str, clientId: str = None, clientSecret: str = None, 
               vanityDomain: str = None, customerId: str = None, testTenant: str = None):
    with Session(engine) as session:
        # Check if exists
        statement = select(Tenant).where(Tenant.tenantName == tenantName)
        results = session.exec(statement)
        existing = results.first()
        if existing:
            # Update existing
            existing.clientId = clientId
            existing.clientSecret = clientSecret
            existing.vanityDomain = vanityDomain
            existing.customerId = customerId
            existing.testTenant = testTenant
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing
        
        tenant = Tenant(tenantName=tenantName, clientId=clientId, clientSecret=clientSecret, 
                        vanityDomain=vanityDomain, customerId=customerId, testTenant=testTenant)
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        return tenant

def get_tenant(tenantName: str) -> Optional[Tenant]:
    with Session(engine) as session:
        statement = select(Tenant).where(Tenant.tenantName == tenantName)
        results = session.exec(statement)
        return results.first()

def get_all_tenants() -> List[Tenant]:
    with Session(engine) as session:
        statement = select(Tenant)
        results = session.exec(statement)
        return results.all()

def delete_tenant(tenantName: str):
    with Session(engine) as session:
        statement = select(Tenant).where(Tenant.tenantName == tenantName)
        results = session.exec(statement)
        tenant = results.first()
        if tenant:
            session.delete(tenant)
            session.commit()
            return True
        return False

# Ensure tables exist
# Note: If the schema changes, you might need to delete the old DB file or migrate
create_db_and_tables()
