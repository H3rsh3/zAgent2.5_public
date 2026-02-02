# Changelog

All notable changes to this project will be documented in this file.

## [2026-02-01] - ZDX Tools Multi-Tenancy Refactoring

### Summary
Refactored the ZDX tools to support multi-tenancy and dynamic credential fetching from the SQLite tenant database. This aligns ZDX tools with the pattern used in ZCC tools for consistent implementation across Zscaler services.

### Task Log
- [x] Research codebase to understand architecture
- [x] Analyze `app.py`, `llm_agent.py`, `LLMs.py`, `zsTenantDB.py`
- [x] Create Implementation Plan for ZDX refactoring
- [x] Document Architecture in `architecture.md`
- [x] Refactor all 11 ZDX tool files for multi-tenancy
- [x] Update `mcp_server/tools/zdx/__init__.py` for tool exports
- [x] Update `mcp_server/services.py` to register the new `ZDXService`
- [x] Verify refactored tools using `py_compile`

### Implementation Plan Highlights
- **Dynamic Credentials**: Tools now fetch client ID, secret, customer ID, and vanity domain from `zsTenantDB` based on the `tenant_name` argument.
- **Service Integration**: Created a dedicated `ZDXService` class in `services.py` to manage tool registration within the MCP server.
- **Unified Client Pattern**: Standardized the use of `get_zscaler_client` across all ZDX functions.

### Walkthrough of Changes
- **Refactored Files**:
    - `mcp_server/tools/zdx/active_devices.py`
    - `mcp_server/tools/zdx/administration.py`
    - `mcp_server/tools/zdx/list_applications.py`
    - `mcp_server/tools/zdx/get_application_metric.py`
    - `mcp_server/tools/zdx/get_application_score.py`
    - `mcp_server/tools/zdx/get_application_user.py`
    - `mcp_server/tools/zdx/list_alerts.py`
    - `mcp_server/tools/zdx/list_deep_traces.py`
    - `mcp_server/tools/zdx/list_historical_alerts.py`
    - `mcp_server/tools/zdx/list_software_inventory.py`
- **Registration**: Tools are properly exported via `zdx/__init__.py` and registered in `services.py` under the `zdx` service name.
- **Verification**: All modified files passed syntax checks via `python3 -m py_compile`.


## [2026-02-01] - ZInsights Tools Multi-Tenancy Refactoring

### Summary
Refactored all ZInsights tool functions to support multi-tenancy by integrating dynamic credential fetching. This ensures that the ZInsights tools follow the same patterns as ZCC and ZDX tools.

### Task Log
- [x] Create Implementation Plan for ZInsights refactoring
- [x] Refactor 6 tool files containing 16 analytics functions
- [x] Standardize function signatures to include `tenant_name`
- [x] Implement logic to fetch credentials from `zsTenantDB` dynamically
- [x] Register `ZInsightsService` in `mcp_server/services.py`
- [x] Verify changes with syntax checks

### Implementation Plan Highlights
- **Dynamic Credentials**: Tools dynamically fetch `clientId`, `clientSecret`, `customerId`, and `vanityDomain` based on the `tenant_name`.
- **Read-Only Focus**: All ZInsights tools remain read-only, providing analytics on web traffic, firewall, IoT, and security.

### Walkthrough of Changes
- **Refactored Files**:
    - `mcp_server/tools/zinsights/cyber_security.py`
    - `mcp_server/tools/zinsights/firewall.py`
    - `mcp_server/tools/zinsights/iot.py`
    - `mcp_server/tools/zinsights/saas_security.py`
    - `mcp_server/tools/zinsights/shadow_it.py`
    - `mcp_server/tools/zinsights/web_traffic.py`
- **MCP Registration**: Added `ZInsightsService` to `services.py` and registered it in `_AVAILABLE_SERVICES`.
- **Validation**: All 6 files passed syntax checks via `python3 -m py_compile`.


## [2026-02-01] - Unified Logging, Dependencies, and Security Implementation (LOGGING REVERTED)

### Added
- **Unified Logging**: Implemented a centralized logging system with daily rotation in `logs/zagent.log`.
  - Updated `mcp_server/common/logging.py` to support `TimedRotatingFileHandler`.
  - Integrated logging into `app.py`, `llm_agent.py`, and `mcp_server/main.py`.
- **Dependency Management**:
  - `requirements.txt`: Standard list of project dependencies.
  - `requirements.py`: Automation script for installing dependencies.
- **Security Enhancements**:
  - Comprehensive `.gitignore` to exclude `.env`, `tenants.db`, `logs/`, and IDE-specific files (`.obsidian/`).
  - Removed sensitive files from Git tracking history.

### Changed
- `llm_agent.py`: Switched to structured logging while maintaining console `print` statements for CLI interaction.
- `mcp_server/main.py`: Replaced manual debug log hacks with standardized logging calls.

---
*Referenced Artifacts:*
- [Task List](file:///home/ulx/.gemini/antigravity/brain/13598103-9a99-45ab-adcf-32e5fbf411a6/task.md)
- [ZInsights Implementation Plan](file:///home/ulx/.gemini/antigravity/brain/13598103-9a99-45ab-adcf-32e5fbf411a6/implementation_plan.md)
- [Logging Implementation Plan](file:///home/ulx/.gemini/antigravity/brain/13598103-9a99-45ab-adcf-32e5fbf411a6/logging_implementation_plan.md)
- [Logging Walkthrough](file:///home/ulx/.gemini/antigravity/brain/13598103-9a99-45ab-adcf-32e5fbf411a6/logging_walkthrough.md)
