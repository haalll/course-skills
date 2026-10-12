# L06 mapping: ADK to Claude Agent SDK (DEC-001), UNVERIFIED

Nothing here was checked against the SDK in round 7 (I-005 is still open). Treat as hypotheses.

| ADK pattern | SDK idea | Status |
|---|---|---|
| Two tools sharing session state | Two tools (in-process MCP tools) sharing an application-side store | inference |
| Approval tool inside the model's reach | A permission callback / `PreToolUse` hook on the approve tool, so the human answer comes from the client and not from the model | inference, to check; this is the hard version of gotcha c |
| Turn boundary by `invocation_id` | The client controls turns, so refuse approval until a new user message arrived | inference |
