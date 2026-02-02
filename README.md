# Zscaler AI Assistant

A powerful AI-driven assistant that integrates with Zscaler via Model Context Protocol (MCP) to provide security insights, analytics, and management capabilities.

## Features
- **Multi-Tenant Support**: Manage multiple Zscaler tenants dynamically.
- **Unified Chat Interface**: Interact with Zscaler services (ZCC, ZIA, ZDX, ZInsights) through a natural language interface.
- **Dual Interface**: Use the Streamlit web app for a premium UI or the CLI for direct terminal interaction.

## Prerequisites
- Python 3.9+
- A Google Gemini API Key (`GOOGLE_API_KEY`)
- Zscaler API Credentials (for ZIA, ZDX, ZInsights, and ZCC)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd zAgent2.5
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Create a virtual environment** (Recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**:
   Run the setup script:
   ```bash
   python3 requirements.py
   ```

## Usage

### 1. Add Tenants (Required)
Tenants can only be added via the Graphical User Interface. You must initialize your tenants here first.

Launch the Streamlit application:
```bash
streamlit run app.py
```
- Navigate to the **Tenant Manager** page.
- Add your Zscaler tenant details (Client ID, Secret, Vanity Domain, etc.).
- Use the **Test Connection** button to verify credentials.

### 2. Choose Your Interface
Once your tenants are configured in the database, you can use either the Web UI or the CLI.

#### Option A: Streamlit App (Web UI)
If `app.py` is already running, simply switch to the **Chat** page in the sidebar to start interacting with the assistant.

#### Option B: CLI Agent
You can run the agent directly from the terminal:
```bash
python3 llm_agent.py
```
Type your queries and press Enter. The CLI supports persistent history via LangGraph.

## Architecture
- **Frontend**: Streamlit (`app.py`) for UI and tenant management.
- **Agent Orchestration**: LangGraph (`llm_agent.py`) for maintaining state and tool calling logic.
- **MCP Server**: FastMCP server (`mcp_server/main.py`) providing Zscaler tools to the LLM.
- **Database**: SQLite (`tenants.db`) manages tenant credentials securely.

## Security
- Credentials are stored locally in a SQLite database (`tenants.db`).
- Credentials are never passed on to the LLM.
- Log files (when enabled) are stored in the `logs/` directory.
