import os
import sys
import asyncio
from dotenv import load_dotenv

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, SystemMessage

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# from zscaler_mcp.tools import server

from LLMs import llm, systemMessage  # Assumes these are pre-defined

# Initialize System Message
sys_msg = SystemMessage(content=systemMessage)

# Try importing adapter, if fails we might need another approach but it is installed
try:
    from langchain_mcp_adapters.tools import load_mcp_tools
except ImportError:
    print("Warning: langchain-mcp-adapters not found. Please install it.")
    load_mcp_tools = None

load_dotenv(override=True)

class ZscalerAgent:
    def __init__(self):
        self.session = None
        self.client_ctx = None
        self.read = None
        self.write = None
        self.graph = None  # Placeholder for the compiled graph

    async def initialize(self):
            # 1. Setup MCP Server Path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # script_path = os.path.join(current_dir, "zscaler_mcp", "server.py")
            script_path = os.path.join(current_dir, "mcp_server", "main.py")

            server_params = StdioServerParameters(
                command=sys.executable,
                args=[script_path],
                env=os.environ.copy()
            )
            
            # 2. Establish MCP Connection
            self.client_ctx = stdio_client(server_params)
            self.read, self.write = await self.client_ctx.__aenter__()
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            
            # 3. Load and Adapt Tools
            if load_mcp_tools:
                tools = await load_mcp_tools(self.session)
            else:
                raise ImportError("langchain-mcp-adapters is required")

            # 4. Bind Tools to LLM
            llm_with_tools = llm.bind_tools(tools)

            # 5. Define the Node Logic
            async def assistant(state: MessagesState):
                # We use ainvoke here for non-blocking execution
                response = await llm_with_tools.ainvoke([sys_msg] + state["messages"])
                return {"messages": [response]}

            # 6. Build the StateGraph
            builder = StateGraph(MessagesState)
            builder.add_node("assistant", assistant)
            builder.add_node("tools", ToolNode(tools))
            
            builder.add_edge(START, "assistant")
            builder.add_conditional_edges("assistant", tools_condition)
            builder.add_edge("tools", "assistant")

            # 7. Add Memory and Compile
            memory = MemorySaver()
            # IMPORTANT: Assign to self.graph so it's accessible outside this method
            self.graph = builder.compile(checkpointer=memory)
        
    async def close(self):
        """Cleanup method to shut down the MCP server process."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.client_ctx:
            await self.client_ctx.__aexit__(None, None, None)

# Agent Launcher
async def main():
    agent = ZscalerAgent()
    try:
        print("Initializing Zscaler Agent...")
        await agent.initialize()
        print("\nAgent initialized. Type 'exit' or 'quit' to stop.")
        print("-" * 50)
        
        while True:
            try:
                # Use to_thread to keep the input prompt from freezing the event loop
                user_input = await asyncio.to_thread(input, "You: ")
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue

                initial_input = {"messages": [HumanMessage(content=user_input)]}
                thread_conf = {"configurable": {"thread_id": "1"}}

                # Streaming the graph execution
                async for event in agent.graph.astream(initial_input, thread_conf, stream_mode="values"):
                    if "messages" in event:
                        # Print only the latest message metadata/content
                        event["messages"][-1].pretty_print()
                        
            except (KeyboardInterrupt, EOFError):
                await agent.close()
                break
            except Exception as e:
                await agent.close()
                print(f"Error: {e}")
    finally:
        print("\nClosing agent...")
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
