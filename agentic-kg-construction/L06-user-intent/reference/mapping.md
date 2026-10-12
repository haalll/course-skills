# L06 mapping: ADK to Claude Agent SDK (DEC-001), UNVERIFIED

Round 7 checked only that the API surface exists, by importing claude-agent-sdk 0.2.165 (course-lab lab/sdk/probe.py,
out_probe.txt): `tool`, `create_sdk_mcp_server`, `ClaudeAgentOptions.can_use_tool` (async callback taking tool name, input,
context; returns allow or deny), `ClaudeAgentOptions.hooks` with event `PreToolUse` and `HookMatcher`, `max_budget_usd`, `max_turns`.
Behaviour (does a deny reach the model, can a hook block an in-process tool, ordering with permission modes) was NOT run: it needs a live model call. I-005 stays open.

| ADK pattern | SDK idea | Status |
|---|---|---|
| Two tools sharing session state | Two tools (in-process MCP tools) sharing an application-side store | inference |
| Approval tool inside the model's reach | A permission callback / `PreToolUse` hook on the approve tool, so the human answer comes from the client and not from the model | surface exists (`can_use_tool`, `PreToolUse`), behaviour unrun; this is the hard version of gotcha c |
| Turn boundary by `invocation_id` | The client controls turns, so refuse approval until a new user message arrived | inference |
