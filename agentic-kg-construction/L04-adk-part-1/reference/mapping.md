# ADK to Claude Agent SDK mapping (UNVERIFIED)

Target framework is the Claude Agent SDK (DEC-001). Every row comes from the round-0 review of the
SDK Python reference, of which only the first 100,000 of 158,282 characters were read (I-005).
Nothing here has been run. Confirm against current docs before use.

| ADK | Claude Agent SDK | Caveat |
|---|---|---|
| `instruction` | `ClaudeAgentOptions.system_prompt` | A plain string replaces the default Claude Code prompt. |
| `description` | `AgentDefinition(description, prompt)` via `agents={...}` | `AgentDefinition` fields are camelCase; snake_case reportedly raises `TypeError`. Options are snake_case. |
| function tool + docstring | `@tool(name, description, input_schema)`, async, returns a content list; served through `create_sdk_mcp_server` | Not docstring-driven. Referenced as `mcp__<server>__<tool>`. |
| Runner event loop | `query()` (fresh session) or `ClaudeSDKClient` (multi-turn) | Stop on `ResultMessage`; check `is_error` as well as `subtype`. |
| session state | SDK keeps conversation sessions; application state is yours | Store choice (SQLite/DuckDB) is an inference. |
| `allowed_tools` | auto-approve list only | Does not restrict; use `disallowed_tools` or `tools` for a read-only agent. |
| LiteLLM to OpenAI | not applicable | Pointing ADK's LiteLLM at Claude is a different path; keep it as a lab step. |
