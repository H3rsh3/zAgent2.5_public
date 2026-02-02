import streamlit as st
import asyncio
from zsTenantDB import add_tenant, delete_tenant, get_all_tenants
from llm_agent import ZscalerAgent 
from langchain_core.messages import HumanMessage, AIMessage
from mcp_server.utils import get_zia_client

# --- Page Config ---
st.set_page_config(page_title="Zscaler Manager", layout="wide")

# --- Agent Management Logic ---
class AgentManager:
    """
    Wraps the async ZscalerAgent to provide a sync interface for Streamlit.
    """
    def __init__(self):
        self.agent = ZscalerAgent()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # Initialize the MCP connection and compile the graph
        self.loop.run_until_complete(self.agent.initialize())
    
    def chat(self, user_msg, thread_id="1"):
        """Sync wrapper for the agent's graph execution."""
        initial_input = {"messages": [user_msg]}
        config = {"configurable": {"thread_id": thread_id}}
        
        # We use ainvoke through the manager's loop
        # Note: We return the full state to keep history consistency
        result = self.loop.run_until_complete(
            self.agent.graph.ainvoke(initial_input, config=config)
        )
        return result["messages"][-1] # Return the final AIMessage

    def close(self):
        self.loop.run_until_complete(self.agent.close())
        self.loop.close()

@st.cache_resource
def get_agent_manager():
    """Ensures only one instance of the agent/MCP server runs."""
    manager = AgentManager()
    return manager

# --- UI Components ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Tenant Manager", "Chat"])

# --- Tenant Manager Page ---
if page == "Tenant Manager":
    st.header("Tenant Management")
    st.subheader("Existing Tenants")
    tenants = get_all_tenants()
    if tenants:
        for t in tenants:
            with st.expander(f"{t.tenantName} ({t.vanityDomain or 'No Domain'})"):
                with st.form(key=f"edit_{t.tenantName}"):
                    st.text_input("Tenant Name", value=t.tenantName, disabled=True)
                    new_clientId = st.text_input("Client ID", value=t.clientId or "")
                    new_clientSecret = st.text_input("Client Secret", value=t.clientSecret or "", type="password")
                    new_vanityDomain = st.text_input("Vanity Domain", value=t.vanityDomain or "")
                    new_customerId = st.text_input("Customer ID", value=t.customerId or "")
                    new_testTenant = st.text_input("Test Tenant", value=t.testTenant or "")
                    
                    update_submitted = st.form_submit_button("Update")
                
                if update_submitted:
                    add_tenant(t.tenantName, new_clientId, new_clientSecret, new_vanityDomain, new_customerId, new_testTenant)
                    st.success(f"Updated {t.tenantName}")
                    st.rerun()
                
                if st.button("Delete Tenant", key=f"del_{t.tenantName}"):
                    delete_tenant(t.tenantName)
                    st.rerun()
    else:
        st.info("No tenants configured.")

    with st.form("add_tenant"):
        st.subheader("Add New Tenant")
        tenantName = st.text_input("Tenant Name (e.g. CorpProd)")
        clientId = st.text_input("Client ID")
        clientSecret = st.text_input("Client Secret", type="password")
        vanityDomain = st.text_input("Vanity Domain (e.g. zscaler.net)")
        customerId = st.text_input("Customer ID")
        testTenant = st.text_input("Test Tenant")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Add Tenant")
        with col2:
            test_conn = st.form_submit_button("Test Connection")
        
        if test_conn:
            try:
                config = {
                    "clientId": clientId,
                    "clientSecret": clientSecret,
                    "vanityDomain": vanityDomain,
                    "customerId": customerId
                }
                client_zia = get_zia_client(tenant_config=config)
                activation_status, err, status = client_zia.activate.status()
                if activation_status:
                    st.success(f"Connection Successful! Status: {status}")
                else:
                    st.error(f"Connection Failed. Status: {status}, Error: {err}")
            except Exception as e:
                st.error(f"Test Failed: {str(e)}")

        if submitted:
            if tenantName:
                res = add_tenant(tenantName, clientId, clientSecret, vanityDomain, customerId, testTenant)
                if res:
                    st.success(f"Tenant {tenantName} added!")
                    st.rerun()
                else:
                    st.error("Failed to add tenant.")
            else:
                st.error("Tenant Name is required.")

# --- Chat Interface Page ---
elif page == "Chat":
    st.header("Zscaler AI Assistant")
    st.caption("Manage your Zscaler environment and query security insights.")
    
    # 1. Initialize the Agent Manager
    manager = get_agent_manager()

    # 2. Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 3. Display chat messages from history
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # 4. Accept user input
    if prompt := st.chat_input("How can I help with Zscaler?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        user_msg = HumanMessage(content=prompt)
        st.session_state.messages.append(user_msg)

        # 5. Generate response using the AgentManager
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking and checking Zscaler..."):
                try:
                    # Call the manager's sync 'chat' method
                    final_msg = manager.chat(user_msg)
                    
                    st.markdown(final_msg.content)
                    
                    # Add to history
                    st.session_state.messages.append(final_msg)
                except Exception as e:
                    st.error(f"Error: {e}")
